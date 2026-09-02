"""
HybridRetriever — 2026-leading RAG retrieval.

Combines:
  - Dense retrieval via BGE-large-en-v1.5 embeddings
  - Sparse retrieval via BM25 (rank_bm25)
  - Reciprocal Rank Fusion (RRF) merging
  - BGE Reranker v2 m3 final reranking

Falls back gracefully if optional libraries are missing.

Enabled via env: USE_HYBRID_RETRIEVAL=true
Vector store via env: VECTOR_STORE=chroma | qdrant (default: chroma in dev)
"""
from __future__ import annotations


import os
# Pass agnostic tokens down to huggingface_hub to prevent rate limits
_agnostic_token = os.getenv("RERANK_TOKEN", os.getenv("INFERENCE_TOKEN", "")).strip()
if _agnostic_token and not os.getenv("HF_TOKEN"):
    os.environ["HF_TOKEN"] = _agnostic_token

import time
from typing import Any, Dict, List, Optional, Tuple

from src.core.logger import get_logger

log = get_logger(__name__)

try:
    import numpy as np
    _NUMPY = True
except ImportError:  # pragma: no cover — numpy is a hard dependency, this is a safety net only
    _NUMPY = False
    log.warning("numpy not installed — dense retrieval disabled")

# Local embedding/reranker models (sentence-transformers, ~1.3GB with torch) are commented
# out of requirements.txt by default — they OOM a 512MB deploy host. Dense retrieval's math
# (cosine similarity) only needs numpy, which IS a hard dependency; the embedding VECTORS
# themselves can come from a remote inference host instead (see _remote_embed below), so
# dense retrieval still works on a constrained host as long as EMBEDDING_ENDPOINT is set —
# _DENSE (can we do the math) and _LOCAL_EMBED (can we also load a model in-process) are
# deliberately separate capabilities.
_DENSE = _NUMPY
try:
    from sentence_transformers import SentenceTransformer
    from sentence_transformers import CrossEncoder
    _LOCAL_EMBED = True
except ImportError:
    _LOCAL_EMBED = False
    log.info("sentence-transformers not installed — local embedding/reranker unavailable "
             "(remote EMBEDDING_ENDPOINT / RERANK_URL still work)")


def _is_still_waking(result: Any) -> bool:
    """True when a remote inference host answered 'not ready yet, I'm starting'.

    An on-demand host does NOT hold the connection open while it boots — it answers
    quickly with an error body that signals a wake was triggered, e.g. a `_woke`
    flag, rather than blocking until the boot completes. So a longer socket timeout
    is useless here; the client has to come back later. Sleeping is the normal,
    expected state of an on-demand host, not a fault.
    """
    if not isinstance(result, dict):
        return False
    if not result.get("error"):
        return False
    if result.get("_woke"):
        return True
    blob = f"{result.get('error')} {result.get('failover_errors', '')}"
    return "530" in blob or "waking" in blob.lower() or "cold" in blob.lower()


def _post_json_awaiting_wake(url: str, payload: Dict[str, Any], headers: Dict[str, str],
                             timeout: float, what: str) -> Any:
    """POST JSON, retrying while the host reports it is still waking up.

    This is a retry against the SAME configured provider — not the silent
    provider-chaining that _encode/rerank deliberately refuse to do. The provider never
    changes; we simply wait for the one that was chosen to finish booting, which is the
    documented behaviour of an on-demand GPU host doing its own wake logic (we never
    poke its wake endpoint ourselves).

    Budget: INFERENCE_WAKE_TIMEOUT seconds total (default 420 — a cold on-demand host
    plus tunnel typically needs a couple of minutes), polled with backoff.
    """
    import json as _json, urllib.request, urllib.error
    budget = float(os.getenv("INFERENCE_WAKE_TIMEOUT", "420"))
    delay = float(os.getenv("INFERENCE_RETRY_DELAY", "15"))
    deadline = time.monotonic() + budget
    attempt = 0
    last_desc = "unknown"
    while True:
        attempt += 1
        try:
            req = urllib.request.Request(url, data=_json.dumps(payload).encode(), headers=headers)
            result = _json.loads(urllib.request.urlopen(req, timeout=timeout).read())
            if not _is_still_waking(result):
                if attempt > 1:
                    log.info("%s ready after %d attempt(s)", what, attempt)
                return result
            last_desc = str(result.get("error"))[:120]
        except urllib.error.HTTPError as e:
            err_body = ""
            try:
                err_body = e.read().decode("utf-8").lower()
            except Exception:
                pass
            if e.code >= 400 and e.code < 500 and e.code != 408 and e.code != 429:
                if "waking" not in err_body and "530" not in err_body and "cold" not in err_body:
                    raise
            last_desc = f"HTTPError: {e.code} {e.reason}"[:120]
        except Exception as e:
            # A transport-level failure can also mean "still coming up" — keep waiting
            # until the budget is spent, then surface the real error.
            last_desc = f"{type(e).__name__}: {e}"[:120]
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise RuntimeError(
                f"{what}: host still not ready after {budget:.0f}s "
                f"({attempt} attempts). Last: {last_desc}")
        log.info("%s: host still waking (attempt %d, %s) — retrying in %.0fs "
                 "(%.0fs of budget left)", what, attempt, last_desc, delay, remaining)
        time.sleep(min(delay, max(remaining, 0)))
        delay = min(delay * 1.5, 60.0)


_READY_CACHE: Dict[str, Any] = {"ts": 0.0, "ready": True}


def _probe_remote_json(endpoint: str, payload: Dict[str, Any], timeout: float) -> bool:
    import json as _json, urllib.request
    headers = {"Content-Type": "application/json", "User-Agent": "IntelAI/1.0"}
    tk = os.getenv("INFERENCE_TOKEN", "").strip()
    if tk:
        headers["Authorization"] = "Bearer " + tk
    try:
        req = urllib.request.Request(endpoint, data=_json.dumps(payload).encode(), headers=headers)
        result = _json.loads(urllib.request.urlopen(req, timeout=timeout).read())
        return not _is_still_waking(result)
    except Exception:
        return False


def remote_inference_reachable() -> bool:
    """Fast, TTL-cached check for whether the remote embed AND rerank hosts are
    currently answering (vs. still waking / down).

    vector_store_retrieve() and hybrid_doc_retrieve() both ultimately depend on
    these same remote hosts, but each pays its own multi-second (12s / 20s)
    attempt independently — confirmed live 2026-09-02: a single chat turn
    against a down host paid both in full, sequentially, before ever reaching
    the BM25/local fallback. Embed and rerank are checked separately and both
    must be up: live testing found them fail independently (embed reachable
    while rerank was still waking), so probing only one under-reports and lets
    hybrid_doc_retrieve still hang on the other. A cache hit is a
    dict-timestamp comparison; a cache miss still costs at most two real ~3s
    probes, so callers can skip straight to their fallback while either host
    stays down instead of re-discovering that fact the slow way.
    """
    now = time.monotonic()
    ttl = float(os.getenv("REMOTE_INFERENCE_READY_CACHE_TTL", "20"))
    if now - _READY_CACHE["ts"] < ttl:
        return bool(_READY_CACHE["ready"])

    probe_timeout = float(os.getenv("REMOTE_INFERENCE_READY_PROBE_TIMEOUT", "3"))
    ready = True

    if os.getenv("EMBEDDING_PROVIDER", "").strip().lower() == "remote":
        url = os.getenv("EMBED_URL", "").strip() or os.getenv("EMBEDDING_ENDPOINT", "").strip()
        if url and "huggingface.co" not in url:
            endpoint = url if url.endswith("/embed") else url.rstrip("/") + "/embed"
            ready = ready and _probe_remote_json(endpoint, {"texts": ["ping"]}, probe_timeout)

    if ready and os.getenv("RERANK_PROVIDER", "").strip().lower() == "remote":
        url = os.getenv("RERANK_URL", "").strip()
        if url and "huggingface.co" not in url:
            endpoint = url if url.endswith("/rerank") else url.rstrip("/") + "/rerank"
            ready = ready and _probe_remote_json(endpoint, {"query": "ping", "texts": ["ping"]}, probe_timeout)

    _READY_CACHE["ts"] = now
    _READY_CACHE["ready"] = ready
    return ready


def _cosine_similarity(a, b):
    """Minimal cosine-similarity matrix (rows of ``a`` vs rows of ``b``) — avoids a
    scikit-learn dependency for a single function; numpy is already a hard dependency."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    a_norm = a / np.clip(np.linalg.norm(a, axis=1, keepdims=True), 1e-12, None)
    b_norm = b / np.clip(np.linalg.norm(b, axis=1, keepdims=True), 1e-12, None)
    return a_norm @ b_norm.T


try:
    from rank_bm25 import BM25Okapi
    _BM25 = True
except ImportError:
    _BM25 = False
    log.warning("rank-bm25 not installed — sparse retrieval disabled")

# The BGE reranker is loaded via sentence-transformers' CrossEncoder (not FlagEmbedding) —
# CrossEncoder uses the fast HF tokenizer and avoids FlagEmbedding's slow-tokenizer path,
# which breaks on newer transformers (XLMRobertaTokenizer.prepare_for_model removed).
# Local-only capability (see _LOCAL_EMBED note above) — the remote rerank path in rerank()
# below doesn't depend on this at all.
_RERANKER = _LOCAL_EMBED

import re as _re
_WORD_RE = _re.compile(r"[a-z0-9]+")


def _tokenize(text: str, drop_stop: bool = False) -> List[str]:
    """Lowercase alphanumeric tokens (punctuation-free) so query and corpus match
    consistently. With drop_stop, strip question/filler words so content terms drive
    BM25 — but never return empty (fall back to the full token list)."""
    toks = _WORD_RE.findall((text or "").lower())
    if drop_stop:
        kept = [t for t in toks if t not in _STOPWORDS]
        return kept or toks
    return toks


# Question/filler words stripped from BM25 queries so content terms drive ranking.
_STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being", "am",
    "what", "which", "who", "whom", "whose", "how", "when", "where", "why",
    "our", "we", "us", "you", "your", "i", "me", "my", "it", "its", "they", "them",
    "of", "to", "in", "on", "for", "and", "or", "with", "at", "by", "from", "as",
    "do", "does", "did", "have", "has", "had", "this", "that", "these", "those",
    "about", "across", "over", "into", "than", "vs", "versus", "between", "per",
    "recent", "recently", "latest", "current", "currently", "now", "today",
    "please", "tell", "show", "give", "me", "many", "much", "long", "relate",
    "related", "relates", "any", "some", "all", "more", "most", "been", "should",
    "can", "could", "would", "will", "doing", "get", "got", "there", "here",
}


class HybridRetriever:
    """
    Hybrid dense+sparse retriever with optional BGE reranker.

    Usage::

        h = HybridRetriever()
        h.fit(chunks)              # index a corpus
        top = h.retrieve(query)    # returns ranked chunks
    """

    def __init__(
        self,
        embedding_model: str = "BAAI/bge-m3",
        reranker_model: str = "BAAI/bge-reranker-v2-m3",
        rrf_k: int = 60,
    ):
        self.embedding_model_name = embedding_model
        self.reranker_model_name = reranker_model
        self.rrf_k = rrf_k
        self._embedder = None
        self._reranker = None
        # Cooldown timestamp (epoch seconds), not a permanent latch: this retriever is a
        # process-wide singleton (see hybrid_doc_retrieve's module-level cache), so a plain
        # bool here meant one transient timeout — e.g. contention from a concurrent
        # request, or a cold remote host — permanently disabled reranking for every
        # request the process ever served afterward, until a redeploy. Confirmed live:
        # a benchmark run under concurrent load tripped one rerank timeout and every
        # later single-request probe kept getting RRF-fallback scores (top result
        # normalized to exactly 1.0) even though isolated rerank calls independently
        # measured well within budget. A short cooldown bounds the blast radius of one
        # failure without hammering a genuinely-down host on every request.
        self._reranker_fail_until = 0.0
        self._chunks: List[str] = []
        self._chunk_vecs = None
        self._bm25 = None

    def _ensure_embedder(self):
        if not _LOCAL_EMBED:
            return None
        if self._embedder is None:
            log.info("Loading embedder: %s", self.embedding_model_name)
            self._embedder = SentenceTransformer(self.embedding_model_name)
        return self._embedder

    def _remote_embed(self, texts: List[str]):
        """Embed on the configured remote inference host. Raises on failure — the caller
        does NOT fall back to a local model (see _encode).

        Sent in batches (EMBED_BATCH_SIZE, default 32): indexing the whole knowledge
        base is hundreds of chunks, and hosted inference APIs reject or time out on a
        single huge payload.
        """
        batch = max(1, int(os.getenv("EMBED_BATCH_SIZE", "32")))
        if len(texts) > batch:
            parts = [self._remote_embed_batch(texts[i:i + batch])
                     for i in range(0, len(texts), batch)]
            return np.vstack(parts)
        return self._remote_embed_batch(texts)

    def _remote_embed_batch(self, texts: List[str]):
        url = os.getenv("EMBED_URL", "").strip() or os.getenv("EMBEDDING_ENDPOINT", "").strip()
        if not url:
            raise RuntimeError(
                "EMBEDDING_PROVIDER=remote but neither EMBED_URL nor EMBEDDING_ENDPOINT is set")
        import json as _json, urllib.request
        h = {"Content-Type": "application/json", "User-Agent": "IntelAI/1.0"}
        timeout = float(os.getenv("EMBED_TIMEOUT", "30"))
        # INFERENCE_TOKEN is the credential for whatever EMBED_URL/EMBEDDING_ENDPOINT
        # currently points at — HF, or any other compliant host. Set its value to
        # match whichever endpoint is configured; the code stays agnostic.
        tk = os.getenv("INFERENCE_TOKEN", "").strip()
        if tk:
            h["Authorization"] = "Bearer " + tk

        if "huggingface.co" in url:
            # HF Inference API: POST straight to the model URL with {"inputs": [...]}.
            # Response is a list of vectors for a sentence-embedding model, or a list of
            # per-token vectors (one extra nesting level) for a plain feature-extraction
            # pipeline — mean-pool the token axis in that case.
            body = _json.dumps({"inputs": texts}).encode()
            req = urllib.request.Request(url, data=body, headers=h)
            result = _json.loads(urllib.request.urlopen(req, timeout=timeout).read())
            arr = np.asarray(result, dtype=float)
            if arr.ndim == 3:
                arr = arr.mean(axis=1)
            return arr
        # Generic contract (any self-hosted inference host) — same shape
        # AUDIO_PROCESSOR_URL/DOC_PROCESSOR_URL use elsewhere in this codebase.
        # Waits through an on-demand host's cold start (see _post_json_awaiting_wake).
        endpoint = url if url.endswith("/embed") else url.rstrip("/") + "/embed"
        result = _post_json_awaiting_wake(
            endpoint,
            {"texts": texts, "model": self.embedding_model_name},
            h, timeout, "remote embed",
        )
        vecs = result.get("embeddings")
        if not vecs:
            raise RuntimeError(f"remote embed host returned no embeddings ({url})")
        return np.asarray(vecs)

    def _encode(self, texts: List[str]):
        """Dense-embed texts using EXACTLY the configured provider — no fallback chain.

        EMBEDDING_PROVIDER=local (default)  load the model in-process on this host;
                                            requires sentence-transformers installed.
        EMBEDDING_PROVIDER=remote           call EMBED_URL/EMBEDDING_ENDPOINT.

        A silent local<->remote fallback is deliberately NOT provided: it hides a
        misconfigured or down inference host behind quietly different (usually worse)
        retrieval, which is far harder to debug than a loud failure. Whichever mode is
        configured is the mode that runs; if it can't run, this raises.
        """
        provider = (os.getenv("EMBEDDING_PROVIDER", "").strip().lower()
                    or ("remote" if os.getenv("INFERENCE_MODE", "").strip().lower() == "remote"
                        else "local"))
        if provider == "remote":
            return self._remote_embed(texts)
        if provider != "local":
            raise RuntimeError(f"EMBEDDING_PROVIDER must be 'local' or 'remote', got {provider!r}")
        embedder = self._ensure_embedder()
        if embedder is None:
            raise RuntimeError(
                "EMBEDDING_PROVIDER=local but sentence-transformers isn't installed on this "
                "host. Install it (pip install sentence-transformers) or set "
                "EMBEDDING_PROVIDER=remote + EMBED_URL.")
        return embedder.encode(texts, show_progress_bar=False)

    def _ensure_reranker(self, force: bool = False):
        """Load the local CrossEncoder (~600MB). Only used when RERANK_PROVIDER=local —
        the module-level rerank() dispatches explicitly, so `force=True` from that path
        means "the operator asked for local, load it". Note this model does not fit a
        512MB app host; use RERANK_PROVIDER=remote|cohere|jina|hf on constrained hosts."""
        if not _RERANKER:
            raise RuntimeError("sentence-transformers not installed — local reranker unavailable")
        if not force:
            return None
        if self._reranker is None:
            log.info("Loading reranker (CrossEncoder): %s", self.reranker_model_name)
            self._reranker = CrossEncoder(self.reranker_model_name)
        return self._reranker

    def fit(self, chunks: List[str]) -> None:
        """Index a corpus of text chunks for retrieval.

        Dense and sparse are two *halves of one retriever*, not two interchangeable
        providers — so if the embedding backend is unavailable we log the real error
        loudly and still build BM25, because returning BM25-only results is far better
        than returning nothing. (This is not the silent provider-swapping that
        _encode deliberately refuses to do: the configured embedding provider is never
        substituted for a different one; dense simply drops out of the fusion.)
        """
        self._chunks = list(chunks)
        self._chunk_vecs = None
        if _DENSE and chunks:
            try:
                self._chunk_vecs = self._encode(chunks)
            except Exception as e:
                log.error("Dense embedding unavailable (%s) — indexing BM25-only. "
                          "Retrieval quality is degraded; fix EMBEDDING_PROVIDER/EMBED_URL.", e)
        if _BM25 and chunks:
            tokenized = [_tokenize(c) for c in chunks]
            self._bm25 = BM25Okapi(tokenized)
        if self._chunk_vecs is None and self._bm25 is None:
            log.error("Neither dense nor sparse retrieval is available — hybrid retrieval "
                      "will return nothing. Install rank-bm25 and/or fix the embedding provider.")

    def _dense_rank(self, query: str, top_n: int) -> List[Tuple[int, float]]:
        if not (_DENSE and self._chunk_vecs is not None):
            return []
        try:
            q_vec = self._encode([query])
        except Exception as e:
            log.error("Dense query embedding failed (%s) — using sparse ranking only", e)
            return []
        if q_vec is None:
            return []
        sims = _cosine_similarity(q_vec, self._chunk_vecs)[0]
        idxs = sims.argsort()[::-1][:top_n]
        return [(int(i), float(sims[i])) for i in idxs]

    def _sparse_rank(self, query: str, top_n: int) -> List[Tuple[int, float]]:
        if not (_BM25 and self._bm25 is not None):
            return []
        # Strip question/stopwords so the content terms drive BM25 — natural-language
        # queries ("what is our latest revenue?") otherwise rank on boilerplate and
        # return near-random docs across a uniform corpus (e.g. the glossary).
        scores = self._bm25.get_scores(_tokenize(query, drop_stop=True))
        idxs = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_n]
        return [(i, float(scores[i])) for i in idxs]

    def _rrf_scores(
        self, dense: List[Tuple[int, float]], sparse: List[Tuple[int, float]]
    ) -> Dict[int, float]:
        """Reciprocal Rank Fusion — returns {doc_idx: fused_score}."""
        scores: Dict[int, float] = {}
        for rank, (idx, _) in enumerate(dense):
            scores[idx] = scores.get(idx, 0.0) + 1.0 / (self.rrf_k + rank + 1)
        for rank, (idx, _) in enumerate(sparse):
            scores[idx] = scores.get(idx, 0.0) + 1.0 / (self.rrf_k + rank + 1)
        return scores

    def _rrf_merge(
        self, dense: List[Tuple[int, float]], sparse: List[Tuple[int, float]], top_n: int
    ) -> List[int]:
        """Reciprocal Rank Fusion merge (ranked indices)."""
        scores = self._rrf_scores(dense, sparse)
        return sorted(scores, key=lambda i: scores[i], reverse=True)[:top_n]

    def retrieve(self, query: str, top_n: int = 5, rerank: bool = True) -> List[Dict[str, Any]]:
        """Hybrid retrieval + optional reranking. Returns a list of {chunk, score}."""
        if not self._chunks:
            return []
        cand_n = max(top_n * 4, 20)
        dense = self._dense_rank(query, cand_n)
        sparse = self._sparse_rank(query, cand_n)
        if not (dense or sparse):
            return []
        rrf = self._rrf_scores(dense, sparse)
        merged = sorted(rrf, key=lambda i: rrf[i], reverse=True)[:cand_n]

        if rerank and time.time() >= self._reranker_fail_until:
            try:
                r_func = globals().get("rerank")
                if r_func:
                    texts = [self._chunks[i] for i in merged]
                    scores = r_func(query, texts)
                    if scores is not None:
                        order = sorted(range(len(merged)), key=lambda j: scores[j], reverse=True)[:top_n]
                        return [{"chunk": self._chunks[merged[j]], "score": float(scores[j])} for j in order]
            except Exception as e:
                # Degrade to dense+BM25+RRF fusion for this call and for a short cooldown
                # afterward (not permanently — see the field comment above).
                cooldown = float(os.getenv("RERANK_FAIL_COOLDOWN", "30"))
                self._reranker_fail_until = time.time() + cooldown
                log.warning("Reranker unavailable (%s) — falling back to RRF fusion for %.0fs", e, cooldown)

        # No (working) reranker: return RRF-ranked results with relevance normalized to
        # 0..1 (top result = 1.0) so the score is meaningful, not a flat 1.0 for all.
        top = merged[:top_n]
        mx = max((rrf[i] for i in top), default=1.0) or 1.0
        return [{"chunk": self._chunks[i], "score": rrf[i] / mx} for i in top]

# ── Module-level helpers (opt-in wiring for the RAG path) ─────────────────────
_HYBRID: Optional["HybridRetriever"] = None
_HYBRID_SIG = None


def hybrid_enabled() -> bool:
    """Hybrid retrieval is opt-in via USE_HYBRID_RETRIEVAL (needs BGE models)."""
    return os.getenv("USE_HYBRID_RETRIEVAL", "false").strip().lower() in ("1", "true", "yes", "on")


def chunk_text(text: str, size: int, overlap: int) -> List[str]:
    """Split text into overlapping passages on natural boundaries.

    Retrieval units must be passages, not whole documents: an embedding model
    compresses whatever it is given into one fixed-length vector, so embedding a
    30k-character report yields a vector that represents the document's average
    topic and matches no specific question well (and anything past the model's
    context window is silently truncated away). BM25 degrades the same way — term
    weights get diluted across an entire document. Splitting on paragraph, then
    sentence, then hard-cut boundaries keeps passages semantically coherent, and
    the overlap stops an answer that straddles a boundary from being lost.
    """
    text = (text or "").strip()
    if not text or len(text) <= size:
        return [text] if text else []
    paras = [p.strip() for p in _re.split(r"\n\s*\n", text) if p.strip()]
    chunks, cur = [], ""
    for p in paras:
        if len(p) > size:  # a single oversized paragraph -> sentence-split it
            for s in _re.split(r"(?<=[.!?])\s+", p):
                if len(cur) + len(s) + 1 <= size:
                    cur = f"{cur} {s}".strip()
                else:
                    if cur:
                        chunks.append(cur)
                    cur = s[:size] if len(s) > size else s
        elif len(cur) + len(p) + 2 <= size:
            cur = f"{cur}\n\n{p}".strip()
        else:
            if cur:
                chunks.append(cur)
            cur = p
    if cur:
        chunks.append(cur)
    if overlap > 0 and len(chunks) > 1:
        stitched = [chunks[0]]
        for prev, nxt in zip(chunks, chunks[1:]):
            stitched.append((prev[-overlap:] + "\n" + nxt).strip())
        chunks = stitched
    return chunks


def hybrid_doc_retrieve(query: str, records: List[Tuple[str, str]], top_k: int = 5):
    """Hybrid (dense+BM25+RRF+rerank) over knowledge docs, at passage granularity.

    ``records`` = list of ``(title, content)``. Returns ``[(title, passage, score)]`` —
    the shape the chatbot's retrieval expects — or ``[]`` when disabled/unavailable/failed.
    The retriever is cached and only re-fit when the document set changes.

    Documents are split into overlapping passages (CHUNK_SIZE/CHUNK_OVERLAP) before
    indexing, and what is returned is the matching *passage*, not the whole document:
    feeding a whole 30k-char report into the answer prompt buries the one relevant
    sentence in noise and burns the context budget, which is exactly how a retrieval
    "hit" still produces an ungrounded answer.
    """
    global _HYBRID, _HYBRID_SIG
    if not hybrid_enabled() or not records or not (_DENSE or _BM25):
        return []
    try:
        size = int(os.getenv("CHUNK_SIZE", "900"))
        overlap = int(os.getenv("CHUNK_OVERLAP", "120"))

        # Index "title. title. passage" so the title (which carries the metric name /
        # acronym, e.g. "Glossary: NRR (NRR)") is searchable and weighted — a query for
        # "NRR" then surfaces the NRR passage instead of an arbitrary keyword match.
        def _indexed(t, c):
            return f"{t}. {t}. {c}"

        passages: List[Tuple[str, str]] = []          # (title, passage)
        for title, content in records:
            for piece in chunk_text(content or "", size, overlap):
                passages.append((title, piece))
        if not passages:
            return []

        sig = (len(passages), hash(tuple(t for t, _ in passages)), size, overlap)
        if _HYBRID is None or _HYBRID_SIG != sig:
            r = HybridRetriever(
                embedding_model=os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3"),
                reranker_model=os.getenv("RERANKER_MODEL", "BAAI/bge-reranker-v2-m3"),
            )
            log.info("Hybrid index: %d docs -> %d passages (size=%d overlap=%d)",
                     len(records), len(passages), size, overlap)
            r.fit([_indexed(t, c) for t, c in passages])
            _HYBRID, _HYBRID_SIG = r, sig
        by_chunk = {_indexed(t, c): (t, c) for t, c in passages}
        out = []
        for hit in _HYBRID.retrieve(query, top_n=top_k):
            title, passage = by_chunk.get(hit["chunk"], ("Document", hit["chunk"]))
            out.append((title, passage, float(hit.get("score", 1.0))))
        return out
    except Exception as e:  # never break the chat path
        log.warning("Hybrid retrieve failed (falling back to vector): %s", e)
        return []


# ── Standalone reranker (shared by the vector-store retrieval path) ────────────
_RERANK_RETRIEVER: Optional["HybridRetriever"] = None


def _rerank_local(query: str, texts: List[str]) -> List[float]:
    """Cross-encoder loaded in-process on this host. Raises if unavailable."""
    global _RERANK_RETRIEVER
    if not _RERANKER:
        raise RuntimeError(
            "RERANK_PROVIDER=local but sentence-transformers isn't installed on this host. "
            "Install it, or set RERANK_PROVIDER=remote|cohere|jina|hf.")
    if _RERANK_RETRIEVER is None:
        _RERANK_RETRIEVER = HybridRetriever()
    reranker = _RERANK_RETRIEVER._ensure_reranker(force=True)
    scores = reranker.predict([(query, t) for t in texts])
    return [float(s) for s in scores]


def _rerank_remote(query: str, texts: List[str]) -> List[float]:
    """RERANK_URL + INFERENCE_TOKEN, provider-agnostic — same split as _remote_embed_batch:
    dispatches on the URL's own shape, not a named-vendor config flag. A huggingface.co
    URL is called in HF's native cross-encoder shape; anything else via the generic
    POST {url}/rerank contract ({"query","texts":[...]} -> {"scores":[...]}) that
    any compliant host can implement."""
    remote = os.getenv("RERANK_URL", "").strip()
    if not remote:
        raise RuntimeError("RERANK_PROVIDER=remote but RERANK_URL is not set")
    h = {"Content-Type": "application/json", "User-Agent": "IntelAI/1.0"}
    tk = os.getenv("INFERENCE_TOKEN", "").strip()
    if tk:
        h["Authorization"] = "Bearer " + tk
    timeout = float(os.getenv("RERANK_TIMEOUT", "12"))

    if "huggingface.co" in remote:
        import urllib.request, json as _json
        body = _json.dumps({"inputs": [f"{query} </s> {t}" for t in texts]}).encode()
        req = urllib.request.Request(remote, data=body, headers=h)
        res = _json.loads(urllib.request.urlopen(req, timeout=timeout).read())
        if isinstance(res, list) and res:
            if isinstance(res[0], list) and len(res[0]) == len(texts):
                return [float(item["score"]) for item in res[0]]
            if len(res) == len(texts):
                return [float(item[0]["score"] if isinstance(item, list) else item.get("score", 0.0)) for item in res]
        raise RuntimeError(f"HF rerank returned an unexpected shape for {len(texts)} texts")

    # Waits through an on-demand host's cold start, same as the embed path.
    endpoint = remote if remote.endswith("/rerank") else remote.rstrip("/") + "/rerank"
    result = _post_json_awaiting_wake(
        endpoint,
        {"query": query, "texts": texts}, h, timeout, "remote rerank",
    )
    scores = result.get("scores")
    if not (isinstance(scores, list) and len(scores) == len(texts)):
        raise RuntimeError(f"remote rerank host returned {len(scores) if isinstance(scores, list) else type(scores)} scores for {len(texts)} texts")
    return [float(s) for s in scores]


def _rerank_hf(query: str, texts: List[str]) -> List[float]:
    """Hugging Face Inference API cross-encoder. Raises if unavailable."""
    hf_token = os.getenv("RERANK_TOKEN", os.getenv("INFERENCE_TOKEN", "")).strip()
    if not hf_token:
        raise RuntimeError("RERANK_PROVIDER=hf but RERANK_TOKEN / INFERENCE_TOKEN is not set")
    import urllib.request, json as _json
    model = os.getenv("HF_RERANK_MODEL", "BAAI/bge-reranker-v2-m3")
    url = f"https://router.huggingface.co/hf-inference/models/{model}"
    h = {"Authorization": f"Bearer {hf_token}", "Content-Type": "application/json"}
    body = _json.dumps({"inputs": [f"{query} </s> {t}" for t in texts]}).encode()
    req = urllib.request.Request(url, data=body, headers=h)
    res = _json.loads(urllib.request.urlopen(req, timeout=float(os.getenv("RERANK_TIMEOUT", "15"))).read())
    if isinstance(res, list) and res:
        if isinstance(res[0], list) and len(res[0]) == len(texts):
            return [float(item["score"]) for item in res[0]]
        if len(res) == len(texts):
            return [float(item[0]["score"] if isinstance(item, list) else item.get("score", 0.0)) for item in res]
    raise RuntimeError(f"HF rerank returned an unexpected shape for {len(texts)} texts")


def _rerank_hosted(query: str, texts: List[str], provider: str) -> List[float]:
    """Hosted cross-encoder rerank API — Cohere /v2/rerank or Jina /v1/rerank.
    Raises if unavailable. Stdlib urllib only; both have a free, no-card tier."""
    key = os.getenv("RERANK_TOKEN", os.getenv("INFERENCE_TOKEN", "")).strip()
    if not key:
        raise RuntimeError(f"RERANK_PROVIDER={provider} but "
                           f"{'COHERE_API_KEY' if provider == 'cohere' else 'JINA_API_KEY'} is not set")
    import json as _json, urllib.request
    if provider == "cohere":
        url = os.getenv("COHERE_BASE_URL", "https://api.cohere.com").rstrip("/") + "/v2/rerank"
        model = os.getenv("HOSTED_RERANK_MODEL", "rerank-v3.5")  # multilingual (EN/FR)
    else:
        url = "https://api.jina.ai/v1/rerank"
        model = os.getenv("HOSTED_RERANK_MODEL", "jina-reranker-v2-base-multilingual")
    body = _json.dumps({"model": model, "query": query,
                        "documents": list(texts), "top_n": len(texts)}).encode()
    req = urllib.request.Request(url, data=body, headers={
        "Content-Type": "application/json", "Authorization": "Bearer " + key})
    timeout = float(os.getenv("HOSTED_RERANK_TIMEOUT", "12"))
    results = _json.loads(urllib.request.urlopen(req, timeout=timeout).read())["results"]
    # Both APIs return [{"index", "relevance_score"}] sorted by score — realign to input order.
    scores = [0.0] * len(texts)
    for r in results:
        idx = r.get("index")
        if isinstance(idx, int) and 0 <= idx < len(texts):
            scores[idx] = float(r.get("relevance_score", 0.0))
    return scores


_RERANK_BACKENDS = {
    "local":  lambda q, t: _rerank_local(q, t),
    "remote": lambda q, t: _rerank_remote(q, t),
    "hf":     lambda q, t: _rerank_hf(q, t),
    "cohere": lambda q, t: _rerank_hosted(q, t, "cohere"),
    "jina":   lambda q, t: _rerank_hosted(q, t, "jina"),
}


def rerank(query: str, texts: List[str]) -> Optional[List[float]]:
    """Rerank using EXACTLY the configured RERANK_PROVIDER — no fallback chain.

    local  cross-encoder loaded in-process on this host (needs sentence-transformers)
    remote self-hosted rerank endpoint (RERANK_URL)
    hf     Hugging Face Inference API (RERANK_TOKEN / INFERENCE_TOKEN)
    cohere Cohere /v2/rerank (RERANK_TOKEN / INFERENCE_TOKEN)
    jina   Jina /v1/rerank (RERANK_TOKEN / INFERENCE_TOKEN)

    Chaining providers is deliberately NOT done: a silent failover changes retrieval
    quality (and cost) without anyone noticing, and hides the fact that the intended
    backend is down. On failure this logs the real error and returns None, which means
    "keep the RRF fusion order" — an honest, explicit degradation, not a different
    model quietly answering. Set USE_RERANKER=false to turn reranking off entirely.
    """
    if os.getenv("USE_RERANKER", "true").strip().lower() not in ("1", "true", "yes", "on"):
        return None
    if not texts:
        return None

    provider = os.getenv("RERANK_PROVIDER", "local").strip().lower()
    backend = _RERANK_BACKENDS.get(provider)
    if backend is None:
        log.error("RERANK_PROVIDER=%r is not one of %s — skipping rerank",
                  provider, sorted(_RERANK_BACKENDS))
        return None
    try:
        return backend(query, texts)
    except Exception as e:
        log.error("rerank via provider %r failed (%s) — keeping RRF fusion order. "
                  "Fix the provider config rather than relying on this degradation.", provider, e)
        return None
