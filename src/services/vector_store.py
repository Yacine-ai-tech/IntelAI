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
    """Same explicit local|remote contract as hybrid_retrieval.py's _encode() — no
    silent multi-provider fallback chain. remote dispatches on EMBED_URL's own shape
    (HF vs. the generic self-hosted contract), same as there; INFERENCE_TOKEN is the
    credential for whichever endpoint is configured. Raises on failure rather than
    quietly trying another provider — a silent swap changes retrieval quality and
    hides a misconfigured or down host.

    Chunks into EMBED_BATCH_SIZE-sized calls for the remote path — a bulk reindex
    passes hundreds of documents in one call, and asking a remote host to embed all
    of them in a single request can outlast EMBED_TIMEOUT even though each individual
    document would embed quickly (confirmed live: 455 texts, one request, timeout;
    EMBED_BATCH_SIZE was already a configured env var but nothing in this module read
    it)."""
    provider = (os.environ.get("EMBEDDING_PROVIDER", "").strip().lower()
                or ("remote" if os.environ.get("INFERENCE_MODE", "").strip().lower() == "remote"
                    else "local"))
    if provider == "remote" and len(texts) > 1:
        batch_size = int(os.environ.get("EMBED_BATCH_SIZE", "32"))
        if len(texts) > batch_size:
            import numpy as np
            chunks = [_embed_batch(texts[i:i + batch_size]) for i in range(0, len(texts), batch_size)]
            return np.concatenate(chunks, axis=0)
    return _embed_batch(texts)


def _embed_batch(texts: List[str]):
    import numpy as np
    provider = (os.environ.get("EMBEDDING_PROVIDER", "").strip().lower()
                or ("remote" if os.environ.get("INFERENCE_MODE", "").strip().lower() == "remote"
                    else "local"))

    if provider == "local":
        vecs = _embedder().encode(list(texts), normalize_embeddings=True, show_progress_bar=False)
        return np.asarray(vecs, dtype="float32")

    if provider != "remote":
        raise RuntimeError(f"EMBEDDING_PROVIDER must be 'local' or 'remote', got {provider!r}")

    remote = os.environ.get("EMBED_URL", "").strip() or os.environ.get("EMBEDDING_ENDPOINT", "").strip()
    if not remote:
        raise RuntimeError("EMBEDDING_PROVIDER=remote but neither EMBED_URL nor EMBEDDING_ENDPOINT is set")
    import time
    import urllib.error
    import urllib.request, json as _json
    h = {"Content-Type": "application/json", "User-Agent": "IntelAI/1.0"}
    tk = os.environ.get("INFERENCE_TOKEN", "").strip()
    if tk:
        h["Authorization"] = "Bearer " + tk
    timeout = float(os.environ.get("EMBED_TIMEOUT", "30"))

    # A self-hosted remote embed host (as opposed to a managed API) can be genuinely
    # up and warm and still fail one request in three — confirmed live: a direct
    # probe succeeded, and the very next call to the same host moments later,
    # inside the same reindex, failed. A single unretried attempt turns that
    # ordinary transient blip into a hard reindex failure for the whole batch.
    # Retry a few times with backoff before giving up — this does NOT paper over a
    # persistently broken host (it still raises after all attempts fail) but stops
    # one bad millisecond from failing a multi-minute job.
    attempts = int(os.environ.get("EMBED_RETRY_ATTEMPTS", "4"))
    backoffs = [3, 8, 20, 20][:attempts]
    last_exc: Optional[Exception] = None
    for attempt, wait in enumerate(backoffs):
        try:
            if "huggingface.co" in remote:
                body = _json.dumps({"inputs": list(texts)}).encode()
                req = urllib.request.Request(remote, data=body, headers=h)
                res = _json.loads(urllib.request.urlopen(req, timeout=timeout).read())
                arr = np.asarray(res, dtype="float32")
                if arr.ndim == 3:  # per-token vectors from a plain feature-extraction pipeline
                    arr = arr.mean(axis=1)
                return arr

            body = _json.dumps({"texts": list(texts)}).encode()
            req = urllib.request.Request(remote.rstrip("/") + "/embed", data=body, headers=h)
            res = _json.loads(urllib.request.urlopen(req, timeout=timeout).read())
            vecs = res.get("embeddings")
            if not (isinstance(vecs, list) and len(vecs) == len(texts)):
                raise RuntimeError(f"remote embed host returned {len(vecs) if isinstance(vecs, list) else type(vecs)} vectors for {len(texts)} texts")
            return np.asarray(vecs, dtype="float32")
        except (urllib.error.URLError, TimeoutError) as e:
            last_exc = e
            if attempt < len(backoffs) - 1:
                log.warning("remote embed attempt %d/%d failed (%s) — retrying in %ds",
                            attempt + 1, len(backoffs), e, wait)
                time.sleep(wait)
    raise RuntimeError(f"remote embed host failed after {len(backoffs)} attempts: {last_exc}") from last_exc

def _dim() -> int:
    provider = os.environ.get("EMBEDDING_PROVIDER", "hf").lower()
    if provider in ("cohere", "hf", "remote"):
        return 1024 # embed-english-v3.0 / bge-m3 dense dim — the portfolio's default embed model
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

    def reset(self) -> None:
        """Drop + recreate the collection — see QdrantVectorStore.reset()'s docstring
        for why this matters: without it, reindex(force=True) silently no-ops here too,
        and upsert()'s add/update-by-id never removes a point whose document was
        deleted from Postgres."""
        self.client.delete_collection(settings.CHROMA_COLLECTION)
        self.col = self.client.get_or_create_collection(
            settings.CHROMA_COLLECTION, metadata={"hnsw:space": "cosine"}
        )


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

    def reset(self) -> None:
        """Drop + recreate the table at the CURRENT embedding dimension. Fixes a dimension
        mismatch (e.g. table built with 1024-d vectors but the active model is 384-d)."""
        conn = self._get_conn()
        try:
            conn.execute("DROP TABLE IF EXISTS doc_vectors")
            conn.execute(
                f"CREATE TABLE doc_vectors ("
                f"doc_id TEXT PRIMARY KEY, title TEXT, content TEXT, source TEXT, "
                f"category TEXT, embedding vector({self.dim}))"
            )
            conn.commit()
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
        self.coll = settings.QDRANT_COLLECTION
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

    def reset(self) -> None:
        """Drop + recreate the collection. Without this, reindex(force=True) silently
        no-ops for Qdrant (reindex() only calls .reset() when hasattr(vs, "reset")) —
        confirmed live: a force reindex left old points untouched, and since upsert()
        only adds/updates by doc_id and never deletes, points for documents removed
        from Postgres (e.g. a cleaned-up duplicate) stayed in Qdrant indefinitely,
        still retrievable, alongside their replacements."""
        from qdrant_client.models import Distance, VectorParams
        if self.client.collection_exists(self.coll):
            self.client.delete_collection(self.coll)
        self.client.create_collection(
            self.coll, vectors_config=VectorParams(size=self.dim, distance=Distance.COSINE)
        )


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


def reindex(docs: Optional[List[Doc]] = None, force: bool = False) -> int:
    """Embed + upsert the knowledge base into the configured store. No-op for ``memory``.
    ``force=True`` drops + recreates the store first (rebuilds at the current embedding dim)."""
    vs = get_vector_store()
    if vs is None:
        return 0
    if force and hasattr(vs, "reset"):
        vs.reset()
    if docs is None:
        from src.services.pg_store import get_knowledge_docs
        # all_owners=True: the store is one shared collection embedding the whole
        # corpus, including every visitor's private uploads — vector_store_retrieve()
        # enforces owner scoping afterwards by post-filtering dense hits against the
        # requester's own scoped get_knowledge_docs() call, not by narrowing what
        # gets indexed here.
        df = get_knowledge_docs(all_owners=True)
        # This store keeps one embedding per document (not per-chunk, unlike
        # hybrid_retrieval.py's proper chunking) — some real documents in this corpus
        # are 100K+ chars (a 56-page report), and embedding that whole string as one
        # HF request is what actually made a 455-doc reindex outlast every timeout
        # tried so far, not the batch count. Capped to what's actually useful for a
        # single dense vector anyway; the fused chat path still gets full-length
        # chunks from hybrid_retrieval.py separately.
        cap = int(os.getenv("VECTOR_STORE_CONTENT_CHARS", "4000"))
        docs = [{"doc_id": r.doc_id, "title": r.title, "content": (r.content or "")[:cap],
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

    def _key(t: str, c: str) -> str:
        return f"{t}{(c or '')[:80]}"

    # get_knowledge_docs() is scoped to this requester (global + their own uploads) —
    # the store itself is one shared collection indexed with every visitor's private
    # docs (see reindex()'s all_owners=True), so dense hits are authorized here by
    # checking each one against this scoped corpus, not by trusting the store's answer.
    # Over-fetch since some raw hits get dropped by the filter below.
    docs = get_knowledge_docs()
    if language and not docs.empty and "language" in docs.columns:
        ld = docs[docs["language"] == language]
        if not ld.empty:
            docs = ld

    allowed = {
        _key(t, c) for t, c in zip(docs["title"].tolist(), docs["content"].fillna("").tolist())
    } if not docs.empty else set()
    raw_dense = vs.query(query, n=cand * 3)
    dense = [d for d in raw_dense if _key(d["title"], d["content"]) in allowed][:cand]

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
