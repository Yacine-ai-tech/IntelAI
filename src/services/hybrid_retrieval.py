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
from typing import Any, Dict, List, Optional, Tuple

from src.core.logger import get_logger

log = get_logger(__name__)

try:
    from sentence_transformers import SentenceTransformer
    from sentence_transformers import CrossEncoder
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    _DENSE = True
except ImportError:
    _DENSE = False
    log.warning("sentence-transformers / sklearn not installed — dense retrieval disabled")

try:
    from rank_bm25 import BM25Okapi
    _BM25 = True
except ImportError:
    _BM25 = False
    log.warning("rank-bm25 not installed — sparse retrieval disabled")

# The BGE reranker is loaded via sentence-transformers' CrossEncoder (not FlagEmbedding) —
# CrossEncoder uses the fast HF tokenizer and avoids FlagEmbedding's slow-tokenizer path,
# which breaks on newer transformers (XLMRobertaTokenizer.prepare_for_model removed).
_RERANKER = _DENSE

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
        embedding_model: str = "BAAI/bge-large-en-v1.5",
        reranker_model: str = "BAAI/bge-reranker-v2-m3",
        rrf_k: int = 60,
    ):
        self.embedding_model_name = embedding_model
        self.reranker_model_name = reranker_model
        self.rrf_k = rrf_k
        self._embedder = None
        self._reranker = None
        self._reranker_failed = False  # set if an installed reranker errors at runtime
        self._chunks: List[str] = []
        self._chunk_vecs = None
        self._bm25 = None

    def _ensure_embedder(self):
        if not _DENSE:
            return None
        if self._embedder is None:
            log.info("Loading embedder: %s", self.embedding_model_name)
            self._embedder = SentenceTransformer(self.embedding_model_name)
        return self._embedder

    def _ensure_reranker(self):
        # Local CrossEncoder (~600MB) is OFF by default: loading it on a constrained app host
        # (Railway/Render free) OOM-crashes the process (the 502/restart-loop we hit). The real
        # BGE reranker runs REMOTELY on the Lightning Studio (see module-level rerank()); a brief
        # outage degrades to dense+BM25+RRF fusion instead. Set USE_LOCAL_RERANKER=true only on a
        # host with RAM headroom.
        if not _RERANKER or os.getenv("USE_LOCAL_RERANKER", "false").strip().lower() not in ("1", "true", "yes", "on"):
            return None
        if self._reranker is None:
            log.info("Loading reranker (CrossEncoder): %s", self.reranker_model_name)
            self._reranker = CrossEncoder(self.reranker_model_name)
        return self._reranker

    def fit(self, chunks: List[str]) -> None:
        """Index a corpus of text chunks for retrieval."""
        self._chunks = list(chunks)
        if _DENSE and chunks:
            self._chunk_vecs = self._ensure_embedder().encode(chunks, show_progress_bar=False)
        if _BM25 and chunks:
            tokenized = [_tokenize(c) for c in chunks]
            self._bm25 = BM25Okapi(tokenized)

    def _dense_rank(self, query: str, top_n: int) -> List[Tuple[int, float]]:
        if not (_DENSE and self._chunk_vecs is not None):
            return []
        emb = self._ensure_embedder()
        q_vec = emb.encode([query])
        sims = cosine_similarity(q_vec, self._chunk_vecs)[0]
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

        if rerank and _RERANKER and not self._reranker_failed:
            try:
                reranker = self._ensure_reranker()
                pairs = [(query, self._chunks[i]) for i in merged]
                scores = reranker.predict(pairs)
                scores = [float(s) for s in scores]
                order = sorted(range(len(merged)), key=lambda j: scores[j], reverse=True)[:top_n]
                return [{"chunk": self._chunks[merged[j]], "score": float(scores[j])} for j in order]
            except Exception as e:  # installed-but-broken reranker (e.g. tokenizer version skew)
                # Degrade to dense+BM25+RRF fusion instead of failing the whole retrieval.
                self._reranker_failed = True
                log.warning("Reranker unavailable (%s) — falling back to RRF fusion for this session", e)

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


def hybrid_doc_retrieve(query: str, records: List[Tuple[str, str]], top_k: int = 5):
    """Hybrid (dense+BM25+RRF+rerank) over knowledge docs.

    ``records`` = list of ``(title, content)``. Returns ``[(title, content, score)]`` —
    the shape the chatbot's retrieval expects — or ``[]`` when disabled/unavailable/failed
    (caller falls back to the existing vector/TF-IDF path). The retriever is cached and only
    re-fit when the document set changes.
    """
    global _HYBRID, _HYBRID_SIG
    if not hybrid_enabled() or not records or not (_DENSE or _BM25):
        return []
    try:
        # Index "title. title. content" so the title (which carries the metric name /
        # acronym, e.g. "Glossary: NRR (NRR)") is searchable and weighted — a query for
        # "NRR" then surfaces the NRR doc instead of an arbitrary keyword match.
        def _indexed(t, c):
            return f"{t}. {t}. {c}"
        sig = (len(records), hash(tuple(t for t, _ in records)))
        if _HYBRID is None or _HYBRID_SIG != sig:
            r = HybridRetriever(
                embedding_model=os.getenv("EMBEDDING_MODEL", "BAAI/bge-large-en-v1.5"),
                reranker_model=os.getenv("RERANKER_MODEL", "BAAI/bge-reranker-v2-m3"),
            )
            r.fit([_indexed(t, c) for t, c in records])
            _HYBRID, _HYBRID_SIG = r, sig
        by_chunk = {_indexed(t, c): (t, c) for t, c in records}
        out = []
        for hit in _HYBRID.retrieve(query, top_n=top_k):
            title, content = by_chunk.get(hit["chunk"], ("Document", hit["chunk"]))
            out.append((title, content, float(hit.get("score", 1.0))))
        return out
    except Exception as e:  # never break the chat path
        log.warning("Hybrid retrieve failed (falling back to vector): %s", e)
        return []


# ── Standalone reranker (shared by the vector-store retrieval path) ────────────
_RERANK_RETRIEVER: Optional["HybridRetriever"] = None


_LAST_WAKE = 0.0


def _trigger_wake() -> None:
    """Fire-and-forget: ask the orchestrator to wake the on-demand inference Studio. Rate-limited
    so a burst of failed reranks triggers at most one wake per minute. Non-blocking (daemon thread)."""
    import time as _t
    global _LAST_WAKE
    url = os.getenv("ORCHESTRATOR_URL", "").strip()
    if not url or (_t.time() - _LAST_WAKE) < 60:
        return
    _LAST_WAKE = _t.time()

    def _go():
        try:
            import json as _json, urllib.request
            h = {"Content-Type": "application/json", "User-Agent": "IntelAI/1.0 (+https://ysiddo-ai-projects.app)"}
            tk = os.getenv("ORCH_TOKEN", "").strip()
            if tk:
                h["Authorization"] = "Bearer " + tk
            req = urllib.request.Request(url.rstrip("/") + "/wake", data=_json.dumps({}).encode(), headers=h)
            urllib.request.urlopen(req, timeout=90)
        except Exception:
            pass
    import threading
    threading.Thread(target=_go, daemon=True).start()


def _hosted_rerank(query: str, texts: List[str]) -> Optional[List[float]]:
    """Hosted-API rerank backstop (a real cross-encoder rerank endpoint — Cohere ``/v2/rerank`` by
    default, Jina ``/v1/rerank`` alternate) so search keeps true rerank quality when the on-demand
    Lightning Studio is down, WITHOUT loading a ~600MB local cross-encoder (survives on a 512MB
    host). Off unless ``HOSTED_RERANK_PROVIDER`` (cohere|jina) + the provider's key are set. Returns
    scores aligned with ``texts`` or ``None`` (caller keeps fusion order). Stdlib urllib only — no
    new dependency. Both providers offer a free, no-card tier."""
    provider = os.getenv("HOSTED_RERANK_PROVIDER", "").strip().lower()
    if provider not in ("cohere", "jina"):
        return None
    key = os.getenv("COHERE_API_KEY" if provider == "cohere" else "JINA_API_KEY", "").strip()
    if not key:
        return None
    try:
        import json as _json, urllib.request
        if provider == "cohere":
            url = os.getenv("COHERE_BASE_URL", "https://api.cohere.com").rstrip("/") + "/v2/rerank"
            model = os.getenv("HOSTED_RERANK_MODEL", "rerank-v3.5")  # multilingual (EN/FR)
        else:  # jina
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
    except Exception as e:
        log.warning("hosted rerank unavailable (%s) — keeping fusion order", e)
        return None


def rerank(query: str, texts: List[str]) -> Optional[List[float]]:
    """Score ``(query, text)`` pairs with the BGE CrossEncoder reranker.

    Returns a list of relevance scores aligned with ``texts``, or ``None`` when the reranker
    is unavailable / has errored (callers then keep their fusion order). Reuses one cached
    reranker instance so the model loads at most once per process.
    """
    global _RERANK_RETRIEVER
    # The CrossEncoder reranker (~600MB) can OOM small instances. Gate it behind USE_RERANKER
    # (default on) so constrained hosts can disable it and keep dense+BM25 fusion (no crash).
    if os.getenv("USE_RERANKER", "true").strip().lower() not in ("1", "true", "yes", "on"):
        return None
    if not texts:
        return None

    # Remote inference backend (Lightning AI): run the real BGE reranker off-box so small app
    # tiers (512MB) don't OOM. Set LIGHTNING_RERANK_URL (+ optional INFERENCE_TOKEN). Falls back
    # to local CrossEncoder, then to None (keep fusion order) when the backend is unreachable
    # (e.g. the on-demand Studio is asleep) — so search degrades gracefully, never breaks.
    remote = os.getenv("LIGHTNING_RERANK_URL", "").strip()
    if remote:
        try:
            import json as _json, urllib.request
            body = _json.dumps({"query": query, "texts": texts}).encode()
            h = {"Content-Type": "application/json", "User-Agent": "IntelAI/1.0 (+https://ysiddo-ai-projects.app)"}
            tk = os.getenv("INFERENCE_TOKEN", "").strip()
            if tk:
                h["Authorization"] = "Bearer " + tk
            req = urllib.request.Request(remote.rstrip("/") + "/rerank", data=body, headers=h)
            timeout = float(os.getenv("LIGHTNING_RERANK_TIMEOUT", "12"))
            scores = _json.loads(urllib.request.urlopen(req, timeout=timeout).read())["scores"]
            if isinstance(scores, list) and len(scores) == len(texts):
                return [float(s) for s in scores]
        except Exception as e:
            log.warning("remote rerank unavailable (%s) — falling back + waking studio", e)
            _trigger_wake()  # on-demand: wake the inference Studio so the next requests get rerank

    # Hosted-API backstop (default OpenAI embeddings → cosine): keeps rerank quality when the
    # on-demand Studio is unreachable, without loading a 600MB local model. Off unless
    # HOSTED_RERANK_PROVIDER is set. Returns None (→ fusion order) when disabled or on failure.
    hosted = _hosted_rerank(query, texts)
    if hosted is not None:
        return hosted

    # Local CrossEncoder fallback is OFF by default (see _ensure_reranker) — degrade to fusion
    # order instead of OOM-loading 600MB on a constrained host when the remote backend is down.
    if not _RERANKER or os.getenv("USE_LOCAL_RERANKER", "false").strip().lower() not in ("1", "true", "yes", "on"):
        return None
    if _RERANK_RETRIEVER is None:
        _RERANK_RETRIEVER = HybridRetriever()
    r = _RERANK_RETRIEVER
    if r._reranker_failed:
        return None
    try:
        reranker = r._ensure_reranker()
        scores = reranker.predict([(query, t) for t in texts])
        return [float(s) for s in scores]
    except Exception as e:
        r._reranker_failed = True
        log.warning("rerank() unavailable (%s) — keeping fusion order", e)
        return None
