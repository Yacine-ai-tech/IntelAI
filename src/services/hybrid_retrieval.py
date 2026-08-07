"""
HybridRetriever — 2026-leading RAG retrieval.

Combines:
  - Dense retrieval via BAAI/bge-m3 embeddings
  - Sparse retrieval via BM25 (rank_bm25)
  - Reciprocal Rank Fusion (RRF) merging
  - BAAI/bge-reranker-v2-m3 final reranking

Supports `local` and `remote` inference modes.
Configured via INFERENCE_MODE, EMBEDDING_ENDPOINT, RERANKER_ENDPOINT, HF_TOKEN.
"""
from __future__ import annotations

import os
import json
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

from src.core.logger import get_logger

log = get_logger(__name__)

from sentence_transformers import SentenceTransformer, CrossEncoder
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from rank_bm25 import BM25Okapi

_DENSE = True
_BM25 = True
_RERANKER = True

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
    Hybrid dense+sparse retriever with BGE reranker.
    Supports 'local' or 'remote' inference modes.
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
        self._chunks: List[str] = []
        self._chunk_vecs = None
        self._bm25 = None
        
        self.inference_mode = os.getenv("INFERENCE_MODE", "remote").strip().lower()

    def _ensure_embedder(self):
        if self.inference_mode != "local":
            return None
        if self._embedder is None:
            log.info("Loading local embedder: %s", self.embedding_model_name)
            self._embedder = SentenceTransformer(self.embedding_model_name)
        return self._embedder

    def _get_embeddings(self, texts: List[str]) -> np.ndarray:
        if not texts:
            return np.array([])
            
        if self.inference_mode == "local":
            emb = self._ensure_embedder()
            return emb.encode(texts, show_progress_bar=False)
            
        # Remote Mode
        endpoint = os.getenv("EMBEDDING_ENDPOINT", f"https://api-inference.huggingface.co/models/{self.embedding_model_name}")
        headers = {"Content-Type": "application/json"}
        token = os.getenv("HF_TOKEN") or os.getenv("INFERENCE_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"
            
        try:
            req = urllib.request.Request(endpoint, data=json.dumps({"inputs": texts}).encode(), headers=headers)
            res = json.loads(urllib.request.urlopen(req, timeout=30).read())
            return np.array(res)
        except Exception as e:
            log.error("Failed to fetch remote embeddings: %s", e)
            raise e

    def fit(self, chunks: List[str]) -> None:
        """Index a corpus of text chunks for retrieval."""
        self._chunks = list(chunks)
        if chunks:
            self._chunk_vecs = self._get_embeddings(chunks)
            tokenized = [_tokenize(c) for c in chunks]
            self._bm25 = BM25Okapi(tokenized)

    def _dense_rank(self, query: str, top_n: int) -> List[Tuple[int, float]]:
        if self._chunk_vecs is None or len(self._chunk_vecs) == 0:
            return []
        
        q_vec = self._get_embeddings([query])
        sims = cosine_similarity(q_vec, self._chunk_vecs)[0]
        idxs = sims.argsort()[::-1][:top_n]
        return [(int(i), float(sims[i])) for i in idxs]

    def _sparse_rank(self, query: str, top_n: int) -> List[Tuple[int, float]]:
        if self._bm25 is None:
            return []
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

    def retrieve(self, query: str, top_n: int = 5, do_rerank: bool = True) -> List[Dict[str, Any]]:
        """Hybrid retrieval + reranking. Returns a list of {chunk, score}."""
        if not self._chunks:
            return []
        cand_n = max(top_n * 4, 20)
        dense = self._dense_rank(query, cand_n)
        sparse = self._sparse_rank(query, cand_n)
        if not (dense or sparse):
            return []
            
        rrf = self._rrf_scores(dense, sparse)
        merged = sorted(rrf, key=lambda i: rrf[i], reverse=True)[:cand_n]

        if do_rerank:
            r_func = globals().get("rerank")
            if r_func:
                texts = [self._chunks[i] for i in merged]
                scores = r_func(query, texts)
                if scores is not None:
                    order = sorted(range(len(merged)), key=lambda j: scores[j], reverse=True)[:top_n]
                    return [{"chunk": self._chunks[merged[j]], "score": float(scores[j])} for j in order]

        # Rerank fallback (if disabled or failed): return RRF-ranked results
        top = merged[:top_n]
        mx = max((rrf[i] for i in top), default=1.0) or 1.0
        return [{"chunk": self._chunks[i], "score": rrf[i] / mx} for i in top]


# ── Module-level helpers (opt-in wiring for the RAG path) ─────────────────────
_HYBRID: Optional["HybridRetriever"] = None
_HYBRID_SIG = None


def hybrid_enabled() -> bool:
    """Hybrid retrieval is always enabled now as per strategy."""
    return True


def hybrid_doc_retrieve(query: str, records: List[Tuple[str, str]], top_k: int = 5):
    """Hybrid (dense+BM25+RRF+rerank) over knowledge docs.
    ``records`` = list of ``(title, content)``. Returns ``[(title, content, score)]``
    """
    global _HYBRID, _HYBRID_SIG
    if not records:
        return []
    try:
        def _indexed(t, c):
            return f"{t}. {t}. {c}"
        sig = (len(records), hash(tuple(t for t, _ in records)))
        if _HYBRID is None or _HYBRID_SIG != sig:
            r = HybridRetriever(
                embedding_model=os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3"),
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
    except Exception as e:
        log.error("Hybrid retrieve failed: %s", e)
        raise e


# ── Standalone reranker ────────────────────────────────────────────────────────
_LOCAL_RERANKER = None

def rerank(query: str, texts: List[str]) -> Optional[List[float]]:
    """
    Rerank texts against a query using local CrossEncoder or remote endpoint.
    """
    global _LOCAL_RERANKER
    if not texts:
        return None
        
    mode = os.getenv("INFERENCE_MODE", "remote").strip().lower()
    reranker_model = os.getenv("RERANKER_MODEL", "BAAI/bge-reranker-v2-m3")

    if mode == "local":
        if _LOCAL_RERANKER is None:
            log.info("Loading local reranker: %s", reranker_model)
            _LOCAL_RERANKER = CrossEncoder(reranker_model)
        scores = _LOCAL_RERANKER.predict([(query, t) for t in texts])
        return [float(s) for s in scores]

    # Remote mode
    endpoint = os.getenv("RERANKER_ENDPOINT", f"https://api-inference.huggingface.co/models/{reranker_model}")
    headers = {"Content-Type": "application/json"}
    token = os.getenv("HF_TOKEN") or os.getenv("INFERENCE_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
        
    # Standard HF Inference payload: "query </s> text"
    payload = {"inputs": [f"{query} </s> {t}" for t in texts]}
    try:
        req = urllib.request.Request(endpoint, data=json.dumps(payload).encode(), headers=headers)
        res = json.loads(urllib.request.urlopen(req, timeout=30).read())
        
        # Parse standard HF responses
        if isinstance(res, list) and len(res) > 0:
            if isinstance(res[0], list) and len(res[0]) == len(texts):
                return [float(item["score"]) for item in res[0]]
            elif len(res) == len(texts):
                return [float(item[0]["score"] if isinstance(item, list) else item.get("score", 0.0)) for item in res]
        return None
    except Exception as e:
        log.error("Failed to fetch remote reranking: %s", e)
        raise e
