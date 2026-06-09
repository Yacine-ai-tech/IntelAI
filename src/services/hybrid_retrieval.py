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

try:
    from FlagEmbedding import FlagReranker  # type: ignore
    _RERANKER = True
except ImportError:
    _RERANKER = False
    log.warning("FlagEmbedding not installed — reranker disabled")


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
        if not _RERANKER:
            return None
        if self._reranker is None:
            log.info("Loading reranker: %s", self.reranker_model_name)
            self._reranker = FlagReranker(self.reranker_model_name, use_fp16=True)
        return self._reranker

    def fit(self, chunks: List[str]) -> None:
        """Index a corpus of text chunks for retrieval."""
        self._chunks = list(chunks)
        if _DENSE and chunks:
            self._chunk_vecs = self._ensure_embedder().encode(chunks, show_progress_bar=False)
        if _BM25 and chunks:
            tokenized = [c.lower().split() for c in chunks]
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
        scores = self._bm25.get_scores(query.lower().split())
        idxs = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_n]
        return [(i, float(scores[i])) for i in idxs]

    def _rrf_merge(
        self, dense: List[Tuple[int, float]], sparse: List[Tuple[int, float]], top_n: int
    ) -> List[int]:
        """Reciprocal Rank Fusion merge."""
        scores: Dict[int, float] = {}
        for rank, (idx, _) in enumerate(dense):
            scores[idx] = scores.get(idx, 0.0) + 1.0 / (self.rrf_k + rank + 1)
        for rank, (idx, _) in enumerate(sparse):
            scores[idx] = scores.get(idx, 0.0) + 1.0 / (self.rrf_k + rank + 1)
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
        merged = self._rrf_merge(dense, sparse, cand_n)

        if rerank and _RERANKER:
            reranker = self._ensure_reranker()
            pairs = [(query, self._chunks[i]) for i in merged]
            scores = reranker.compute_score(pairs, normalize=True)
            if not isinstance(scores, list):
                scores = [scores]
            order = sorted(range(len(merged)), key=lambda j: scores[j], reverse=True)[:top_n]
            return [{"chunk": self._chunks[merged[j]], "score": float(scores[j])} for j in order]

        return [{"chunk": self._chunks[i], "score": 1.0} for i in merged[:top_n]]

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
        sig = (len(records), hash(tuple(t for t, _ in records)))
        if _HYBRID is None or _HYBRID_SIG != sig:
            r = HybridRetriever(
                embedding_model=os.getenv("EMBEDDING_MODEL", "BAAI/bge-large-en-v1.5"),
                reranker_model=os.getenv("RERANKER_MODEL", "BAAI/bge-reranker-v2-m3"),
            )
            r.fit([c for _, c in records])
            _HYBRID, _HYBRID_SIG = r, sig
        by_content = {c: t for t, c in records}
        out = []
        for hit in _HYBRID.retrieve(query, top_n=top_k):
            chunk = hit["chunk"]
            out.append((by_content.get(chunk, "Document"), chunk, float(hit.get("score", 1.0))))
        return out
    except Exception as e:  # never break the chat path
        log.warning("Hybrid retrieve failed (falling back to vector): %s", e)
        return []
