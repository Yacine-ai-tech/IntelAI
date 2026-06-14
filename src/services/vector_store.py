"""Pluggable vector store for IntelAI RAG.

Selected at runtime via ``VECTOR_STORE`` (env):

  * ``memory``   — no persistent store; the in-process hybrid path (BM25 + in-memory dense)
                   in ``hybrid_retrieval`` handles dense retrieval. ``get_vector_store()``
                   returns ``None`` and callers keep their existing behaviour. (default)
  * ``chroma``   — ChromaDB persistent client (the dev default per STRATEGY).
  * ``pgvector`` — Postgres + the ``vector`` extension; runs on the existing Neon DB (prod).
  * ``qdrant``   — a Qdrant server, configured via ``QDRANT_URL`` / ``QDRANT_API_KEY`` (prod).

Every backend embeds documents with ``EMBEDDING_MODEL`` (sentence-transformers) and supports
``upsert(docs)`` + ``query(text, n)``. ``vector_store_retrieve()`` fuses the store's dense
hits with BM25 (RRF) and applies the BGE reranker when available — the same hybrid recipe,
but with the dense side served from a real, persistent index.

All backends degrade gracefully: if the client library or service is unavailable, the
factory logs a warning and returns ``None`` so retrieval falls back to the in-process path —
the chat path never breaks because a vector DB is misconfigured.
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Tuple

from src.core.config import settings
from src.core.logger import get_logger

log = get_logger(__name__)

Doc = Dict[str, Any]  # {doc_id, title, content, source, category?}

# ── Shared embedder (lazy; one model per process) ─────────────────────────────
_EMBEDDER = None


def _embedder():
    global _EMBEDDER
    if _EMBEDDER is None:
        from sentence_transformers import SentenceTransformer
        log.info("Vector store embedder: %s", settings.EMBEDDING_MODEL)
        _EMBEDDER = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _EMBEDDER


def _embed(texts: List[str]):
    import numpy as np
    vecs = _embedder().encode(list(texts), normalize_embeddings=True, show_progress_bar=False)
    return np.asarray(vecs, dtype="float32")


def _dim() -> int:
    emb = _embedder()
    getter = getattr(emb, "get_embedding_dimension", None) or emb.get_sentence_embedding_dimension
    return int(getter())


# ── Backends ──────────────────────────────────────────────────────────────────
class ChromaVectorStore:
    name = "chroma"

    def __init__(self):
        import chromadb
        self.client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
        self.col = self.client.get_or_create_collection(
            settings.CHROMA_COLLECTION, metadata={"hnsw:space": "cosine"}
        )

    def upsert(self, docs: List[Doc]) -> int:
        if not docs:
            return 0
        embs = _embed([d["content"] for d in docs]).tolist()
        self.col.upsert(
            ids=[str(d["doc_id"]) for d in docs],
            embeddings=embs,
            documents=[d["content"] for d in docs],
            metadatas=[{"title": d.get("title", ""), "source": d.get("source", ""),
                        "category": d.get("category", "")} for d in docs],
        )
        return len(docs)

    def query(self, text: str, n: int = 10) -> List[Doc]:
        res = self.col.query(query_embeddings=_embed([text]).tolist(), n_results=n)
        docs = (res.get("documents") or [[]])[0]
        metas = (res.get("metadatas") or [[]])[0]
        dists = (res.get("distances") or [[]])[0]
        out: List[Doc] = []
        for i, doc in enumerate(docs):
            m = metas[i] if i < len(metas) else {}
            dist = dists[i] if i < len(dists) else 1.0
            out.append({"title": m.get("title", ""), "content": doc,
                        "source": m.get("source", ""), "score": 1.0 - float(dist)})
        return out

    def count(self) -> int:
        return self.col.count()


class PgVectorStore:
    name = "pgvector"

    def __init__(self):
        from pgvector.psycopg import register_vector  # noqa: F401 — import-checks availability
        from src.services.pg_store import _get_conn
        self._register = register_vector
        self._get_conn = _get_conn
        self.dim = _dim()
        conn = _get_conn()
        try:
            conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            conn.execute(
                f"CREATE TABLE IF NOT EXISTS doc_vectors ("
                f"doc_id TEXT PRIMARY KEY, title TEXT, content TEXT, source TEXT, "
                f"category TEXT, embedding vector({self.dim}))"
            )
            conn.commit()
        finally:
            conn.close()

    def _conn(self):
        c = self._get_conn()
        self._register(c)
        return c

    def upsert(self, docs: List[Doc]) -> int:
        if not docs:
            return 0
        embs = _embed([d["content"] for d in docs])
        conn = self._conn()
        try:
            with conn.cursor() as cur:
                cur.executemany(
                    "INSERT INTO doc_vectors (doc_id, title, content, source, category, embedding) "
                    "VALUES (%s, %s, %s, %s, %s, %s) "
                    "ON CONFLICT (doc_id) DO UPDATE SET title=EXCLUDED.title, "
                    "content=EXCLUDED.content, source=EXCLUDED.source, embedding=EXCLUDED.embedding",
                    [(str(d["doc_id"]), d.get("title", ""), d["content"], d.get("source", ""),
                      d.get("category", ""), embs[i]) for i, d in enumerate(docs)],
                )
            conn.commit()
        finally:
            conn.close()
        return len(docs)

    def query(self, text: str, n: int = 10) -> List[Doc]:
        q = _embed([text])[0]
        conn = self._conn()
        try:
            rows = conn.execute(
                "SELECT title, content, source, 1 - (embedding <=> %s) AS score "
                "FROM doc_vectors ORDER BY embedding <=> %s LIMIT %s",
                [q, q, n],
            ).fetchall()
        finally:
            conn.close()
        return [{"title": r["title"], "content": r["content"], "source": r["source"],
                 "score": float(r["score"])} for r in rows]

    def count(self) -> int:
        conn = self._get_conn()
        try:
            return int(conn.execute("SELECT count(*) AS c FROM doc_vectors").fetchone()["c"])
        finally:
            conn.close()


class QdrantVectorStore:
    name = "qdrant"

    def __init__(self):
        from qdrant_client import QdrantClient
        from qdrant_client.models import Distance, VectorParams
        if not settings.QDRANT_URL:
            raise RuntimeError("QDRANT_URL not set")
        self.client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY or None)
        self.coll = settings.CHROMA_COLLECTION
        self.dim = _dim()
        if not self.client.collection_exists(self.coll):
            self.client.create_collection(
                self.coll, vectors_config=VectorParams(size=self.dim, distance=Distance.COSINE)
            )

    @staticmethod
    def _pid(doc_id: str) -> int:
        import hashlib
        return int(hashlib.md5(str(doc_id).encode()).hexdigest()[:15], 16)

    def upsert(self, docs: List[Doc]) -> int:
        from qdrant_client.models import PointStruct
        if not docs:
            return 0
        embs = _embed([d["content"] for d in docs])
        pts = [PointStruct(
            id=self._pid(d["doc_id"]), vector=embs[i].tolist(),
            payload={"title": d.get("title", ""), "content": d["content"],
                     "source": d.get("source", ""), "category": d.get("category", "")},
        ) for i, d in enumerate(docs)]
        self.client.upsert(self.coll, points=pts)
        return len(docs)

    def query(self, text: str, n: int = 10) -> List[Doc]:
        vec = _embed([text])[0].tolist()
        if hasattr(self.client, "query_points"):  # qdrant-client >= 1.10 (search() is deprecated)
            pts = self.client.query_points(collection_name=self.coll, query=vec, limit=n).points
        else:
            pts = self.client.search(collection_name=self.coll, query_vector=vec, limit=n)
        return [{"title": p.payload.get("title", ""), "content": p.payload.get("content", ""),
                 "source": p.payload.get("source", ""), "score": float(p.score)} for p in pts]

    def count(self) -> int:
        return int(self.client.count(self.coll).count)


# ── Factory (cached) ──────────────────────────────────────────────────────────
_STORE: Any = "unset"
_BACKENDS = {"chroma": ChromaVectorStore, "pgvector": PgVectorStore, "qdrant": QdrantVectorStore}


def get_vector_store():
    """Return the configured backend instance, or ``None`` for ``memory``/unavailable."""
    global _STORE
    if _STORE != "unset":
        return _STORE
    kind = settings.VECTOR_STORE
    cls = _BACKENDS.get(kind)
    if cls is None:
        _STORE = None
        return _STORE
    try:
        _STORE = cls()
        log.info("Vector store backend active: %s", kind)
    except Exception as e:  # missing client lib or unreachable service → graceful fallback
        log.warning("Vector store '%s' unavailable (%s) — using in-process retrieval", kind, e)
        _STORE = None
    return _STORE


def reset_cache() -> None:
    """Drop the cached backend (used by tests that flip VECTOR_STORE)."""
    global _STORE
    _STORE = "unset"


def reindex(docs: Optional[List[Doc]] = None) -> int:
    """Embed + upsert the knowledge base into the configured store. No-op for ``memory``."""
    vs = get_vector_store()
    if vs is None:
        return 0
    if docs is None:
        from src.services.pg_store import get_knowledge_docs
        df = get_knowledge_docs()
        docs = [{"doc_id": r.doc_id, "title": r.title, "content": r.content,
                 "source": r.source, "category": ""} for r in df.itertuples()]
    return vs.upsert(docs)


# ── Fused retrieval (dense store + BM25 + RRF + optional rerank) ───────────────
def vector_store_retrieve(
    query: str, top_k: int = 5, language: Optional[str] = None
) -> Optional[List[Tuple[str, str, float]]]:
    """Return ``[(title, content, score)]`` from the persistent store fused with BM25,
    or ``None`` when no store is configured (caller uses its in-process path)."""
    vs = get_vector_store()
    if vs is None:
        return None
    from src.services.pg_store import get_knowledge_docs
    from src.services.hybrid_retrieval import _tokenize, rerank

    cand = max(top_k * 4, 20)
    dense = vs.query(query, n=cand)

    docs = get_knowledge_docs()
    if language and not docs.empty and "language" in docs.columns:
        ld = docs[docs["language"] == language]
        if not ld.empty:
            docs = ld

    # BM25 over the same corpus (title weighted 2x, matching the in-process retriever).
    sparse: List[Tuple[str, str]] = []
    try:
        from rank_bm25 import BM25Okapi
        titles = docs["title"].tolist()
        contents = docs["content"].fillna("").tolist()
        corpus = [f"{t}. {t}. {c}" for t, c in zip(titles, contents)]
        bm = BM25Okapi([_tokenize(x) for x in corpus])
        scores = bm.get_scores(_tokenize(query, drop_stop=True))
        order = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:cand]
        sparse = [(titles[i], contents[i]) for i in order]
    except Exception as e:
        log.warning("BM25 side skipped in vector_store_retrieve: %s", e)

    # Reciprocal Rank Fusion, keyed by title + content prefix (stable across both sources).
    K = 60
    fused: Dict[str, float] = {}
    meta: Dict[str, Tuple[str, str]] = {}

    def _key(t: str, c: str) -> str:
        return f"{t}{(c or '')[:80]}"

    for rank, d in enumerate(dense):
        k = _key(d["title"], d["content"])
        fused[k] = fused.get(k, 0.0) + 1.0 / (K + rank + 1)
        meta[k] = (d["title"], d["content"])
    for rank, (t, c) in enumerate(sparse):
        k = _key(t, c)
        fused[k] = fused.get(k, 0.0) + 1.0 / (K + rank + 1)
        meta.setdefault(k, (t, c))

    ranked = sorted(fused, key=lambda k: fused[k], reverse=True)[:cand]
    if not ranked:
        return []
    cands = [meta[k] for k in ranked]

    rr = rerank(query, [c for _, c in cands])
    if rr:
        idx = sorted(range(len(cands)), key=lambda j: rr[j], reverse=True)[:top_k]
        return [(cands[j][0], cands[j][1], float(rr[j])) for j in idx]

    top = ranked[:top_k]
    mx = max((fused[k] for k in top), default=1.0) or 1.0
    return [(meta[k][0], meta[k][1], fused[k] / mx) for k in top]
