"""
IntelAI Inference Adapter
==========================
Unified adapter for compute-heavy inference (embeddings, reranking) that can't
run on the 512MB Render free tier.

Two modes selected via INTELAI_INFERENCE_MODE:

  local   — Load sentence-transformers locally (needs GPU/large RAM).
            Only use this in development or on a machine with ≥ 4GB RAM.
            Set USE_LOCAL_EMBEDDER=true to enable.

  remote  — Forward to a remote endpoint (Orchestrator Studio or public API).
            Configure INTELAI_REMOTE_ENDPOINT + INTELAI_REMOTE_TOKEN.

Remote provider dialects (auto-detected from INTELAI_REMOTE_ENDPOINT):
  orchestrator — Your private Lightning AI Studio via cloudflared tunnel.
                 Endpoint: http://localhost:8000
  cohere       — Cohere embed + rerank API (free tier available).
                 Endpoint: https://api.cohere.com  + COHERE_API_KEY
  jina         — Jina embeddings API (free tier available).
                 Endpoint: https://api.jina.ai    + JINA_API_KEY

Public provider fallback chain (remote mode):
  1. Orchestrator Studio (/embed, /rerank)  [INTELAI_REMOTE_ENDPOINT]
  2. Cohere (/v2/embed, /v2/rerank)         [COHERE_API_KEY]
  3. Jina (/v1/embeddings)                 [JINA_API_KEY — embed only]
  4. None — caller degrades to neutral scores

Env vars:
  INTELAI_INFERENCE_MODE=local|remote  (default: remote if INTELAI_REMOTE_ENDPOINT is set)
  INTELAI_REMOTE_ENDPOINT=             (Orchestrator tunnel URL)
  INTELAI_REMOTE_TOKEN=                (bearer token for Orchestrator)
  EMBEDDING_MODEL=BAAI/bge-large-en-v1.5
  RERANKER_MODEL=BAAI/bge-reranker-v2-m3
  COHERE_API_KEY=
  JINA_API_KEY=
  HOSTED_EMBEDDING_MODEL=embed-english-v3.0   (Cohere model)
  HOSTED_EMBED_INPUT_TYPE=search_document
  INTELAI_EMBED_TIMEOUT=30
  USE_LOCAL_EMBEDDER=false
  ORCHESTRATOR_URL=                     (legacy: used if INTELAI_REMOTE_ENDPOINT not set)
  INFERENCE_TOKEN=                      (legacy: used if INTELAI_REMOTE_TOKEN not set)
"""
from __future__ import annotations

import json as _json
import logging
import os
import threading
import time
import urllib.request
from typing import List, Optional

log = logging.getLogger(__name__)

# Rate-limit the orchestrator wake signal
_LAST_WAKE = 0.0

# ─── Mode resolution ──────────────────────────────────────────────────────────

def _remote_endpoint() -> str:
    """Return the configured remote inference endpoint (Orchestrator or public)."""
    return (os.getenv("INTELAI_REMOTE_ENDPOINT", "")
            or os.getenv("LIGHTNING_EMBED_URL", "")   # legacy
            or os.getenv("ORCHESTRATOR_URL", "")       # legacy
            or "").strip().rstrip("/")


def _remote_token() -> str:
    return (os.getenv("INTELAI_REMOTE_TOKEN", "")
            or os.getenv("INFERENCE_TOKEN", "")).strip()


def _use_local() -> bool:
    mode = os.getenv("INTELAI_INFERENCE_MODE", "").strip().lower()
    if mode == "local":
        return True
    if mode == "remote":
        return False
    # Auto: local only if explicitly enabled or no remote endpoint
    return (os.getenv("USE_LOCAL_EMBEDDER", "false").lower() == "true"
            and not _remote_endpoint())


def _detect_dialect(endpoint: str) -> str:
    ep = endpoint.lower()
    if "cohere.com" in ep:
        return "cohere"
    if "jina.ai" in ep:
        return "jina"
    return "orchestrator"


# ─── Wake helpers ─────────────────────────────────────────────────────────────

def _fire_wake():
    """Non-blocking wake signal to the Orchestrator (rate-limited to once per 60s)."""
    global _LAST_WAKE
    url = (os.getenv("ORCHESTRATOR_URL", "") or os.getenv("INTELAI_REMOTE_ENDPOINT", "")).strip()
    if not url:
        return
    if (time.time() - _LAST_WAKE) < 60:
        return
    _LAST_WAKE = time.time()

    def _go():
        try:
            h = {"Content-Type": "application/json", "User-Agent": "IntelAI/1.0"}
            tk = os.getenv("ORCH_TOKEN", os.getenv("INTELAI_REMOTE_TOKEN", "")).strip()
            if tk:
                h["Authorization"] = f"Bearer {tk}"
            body = _json.dumps({"gpu": False, "service": "intelai"}).encode()
            req = urllib.request.Request(url.rstrip("/") + "/wake", data=body, headers=h)
            urllib.request.urlopen(req, timeout=10)
        except Exception as e:
            log.debug("wake signal failed (non-fatal): %s", e)

    threading.Thread(target=_go, daemon=True).start()


# ─── Orchestrator (private Studio) calls ──────────────────────────────────────

def _orchestrator_embed(texts: List[str], model: Optional[str] = None) -> Optional[List[List[float]]]:
    url = _remote_endpoint()
    if not url or _detect_dialect(url) != "orchestrator":
        return None
    timeout = int(os.getenv("INTELAI_EMBED_TIMEOUT", "30"))
    try:
        payload: dict = {"texts": texts}
        if model:
            payload["model"] = model
        h = {"Content-Type": "application/json"}
        tk = _remote_token()
        if tk:
            h["Authorization"] = f"Bearer {tk}"
        req = urllib.request.Request(url + "/embed", data=_json.dumps(payload).encode(), headers=h)
        resp = _json.loads(urllib.request.urlopen(req, timeout=timeout).read())
        return resp.get("embeddings")
    except Exception as e:
        log.warning("orchestrator embed failed (%s) — waking studio", e)
        _fire_wake()
        return None


def _orchestrator_rerank(query: str, texts: List[str]) -> Optional[List[float]]:
    url = _remote_endpoint()
    if not url or _detect_dialect(url) != "orchestrator":
        return None
    timeout = int(os.getenv("INTELAI_EMBED_TIMEOUT", "30"))
    try:
        payload = {"query": query, "texts": texts}
        h = {"Content-Type": "application/json"}
        tk = _remote_token()
        if tk:
            h["Authorization"] = f"Bearer {tk}"
        req = urllib.request.Request(url + "/rerank", data=_json.dumps(payload).encode(), headers=h)
        resp = _json.loads(urllib.request.urlopen(req, timeout=timeout).read())
        return resp.get("scores")
    except Exception as e:
        log.warning("orchestrator rerank failed (%s) — waking studio", e)
        _fire_wake()
        return None


# ─── Cohere fallback ──────────────────────────────────────────────────────────

def _cohere_embed(texts: List[str]) -> Optional[List[List[float]]]:
    key = os.getenv("COHERE_API_KEY", "").strip()
    if not key:
        return None
    try:
        url = os.getenv("COHERE_BASE_URL", "https://api.cohere.com").rstrip("/") + "/v2/embed"
        payload = {
            "model": os.getenv("HOSTED_EMBEDDING_MODEL", "embed-english-v3.0"),
            "texts": list(texts),
            "input_type": os.getenv("HOSTED_EMBED_INPUT_TYPE", "search_document"),
            "embedding_types": ["float"],
        }
        h = {"Content-Type": "application/json", "Authorization": f"Bearer {key}"}
        req = urllib.request.Request(url, data=_json.dumps(payload).encode(), headers=h)
        data = _json.loads(urllib.request.urlopen(req, timeout=30).read())
        return data["embeddings"]["float"]
    except Exception as e:
        log.warning("cohere embed failed: %s", e)
        return None


def _cohere_rerank(query: str, texts: List[str]) -> Optional[List[float]]:
    key = os.getenv("COHERE_API_KEY", "").strip()
    if not key:
        return None
    try:
        url = "https://api.cohere.com/v2/rerank"
        payload = {
            "model": os.getenv("COHERE_RERANK_MODEL", "rerank-english-v3.0"),
            "query": query,
            "documents": texts,
            "top_n": len(texts),
            "return_documents": False,
        }
        h = {"Content-Type": "application/json", "Authorization": f"Bearer {key}"}
        req = urllib.request.Request(url, data=_json.dumps(payload).encode(), headers=h)
        data = _json.loads(urllib.request.urlopen(req, timeout=30).read())
        # Cohere returns results sorted by relevance_score; re-align to original order
        scores = [0.5] * len(texts)
        for item in data.get("results", []):
            if item.get("index") is not None:
                scores[item["index"]] = item.get("relevance_score", 0.5)
        return scores
    except Exception as e:
        log.warning("cohere rerank failed: %s", e)
        return None


# ─── Jina fallback (embed only) ───────────────────────────────────────────────

def _jina_embed(texts: List[str]) -> Optional[List[List[float]]]:
    key = os.getenv("JINA_API_KEY", "").strip()
    if not key:
        return None
    try:
        url = "https://api.jina.ai/v1/embeddings"
        payload = {
            "model": os.getenv("HOSTED_EMBEDDING_MODEL", "jina-embeddings-v3"),
            "input": list(texts),
        }
        h = {"Content-Type": "application/json", "Authorization": f"Bearer {key}"}
        req = urllib.request.Request(url, data=_json.dumps(payload).encode(), headers=h)
        data = _json.loads(urllib.request.urlopen(req, timeout=30).read())
        return [r["embedding"] for r in sorted(data["data"], key=lambda d: d.get("index", 0))]
    except Exception as e:
        log.warning("jina embed failed: %s", e)
        return None


# ─── Local fallback ───────────────────────────────────────────────────────────

_local_embedder = None
_local_reranker = None


def _local_embed(texts: List[str], model: Optional[str] = None) -> Optional[List[List[float]]]:
    global _local_embedder
    try:
        from sentence_transformers import SentenceTransformer
        m = model or os.getenv("EMBEDDING_MODEL", "BAAI/bge-large-en-v1.5")
        if _local_embedder is None or getattr(_local_embedder, "_name", "") != m:
            log.info("Loading local embedding model: %s (may take a while...)", m)
            _local_embedder = SentenceTransformer(m)
            _local_embedder._name = m
        vecs = _local_embedder.encode(texts, normalize_embeddings=True)
        return vecs.tolist()
    except Exception as e:
        log.warning("local embed failed: %s", e)
        return None


def _local_rerank(query: str, texts: List[str]) -> Optional[List[float]]:
    global _local_reranker
    try:
        from sentence_transformers import CrossEncoder
        m = os.getenv("RERANKER_MODEL", "BAAI/bge-reranker-v2-m3")
        if _local_reranker is None:
            log.info("Loading local reranker model: %s", m)
            _local_reranker = CrossEncoder(m)
        scores = _local_reranker.predict([(query, t) for t in texts])
        return [float(s) for s in scores]
    except Exception as e:
        log.warning("local rerank failed: %s", e)
        return None


# ─── Public API ───────────────────────────────────────────────────────────────

def embed(texts: List[str], model: Optional[str] = None) -> Optional[List[List[float]]]:
    """
    Embed texts using the configured mode (remote → cohere → jina → local → None).

    Args:
        texts: Texts to embed.
        model: Specific embedding model (only respected by orchestrator and local modes).

    Returns:
        List of float vectors, or None if all providers fail.
        Caller should degrade gracefully (e.g. return neutral similarity score).
    """
    if not texts:
        return []

    if _use_local():
        return _local_embed(texts, model)

    # Remote chain
    vecs = _orchestrator_embed(texts, model)
    if vecs and len(vecs) == len(texts):
        return vecs

    vecs = _cohere_embed(texts)
    if vecs and len(vecs) == len(texts):
        return vecs

    vecs = _jina_embed(texts)
    if vecs and len(vecs) == len(texts):
        return vecs

    if os.getenv("USE_LOCAL_EMBEDDER", "false").lower() == "true":
        return _local_embed(texts, model)

    log.warning("All embed providers failed — caller should degrade gracefully")
    return None


def rerank(query: str, texts: List[str]) -> Optional[List[float]]:
    """
    Rerank texts against a query using BGE CrossEncoder (remote → cohere → local → None).

    Args:
        query: The search query.
        texts: Candidate texts to rerank.

    Returns:
        List of float scores (higher = more relevant), aligned with texts.
        Or None if all providers fail (caller should fall back to BM25/RRF scores).
    """
    if not texts:
        return []

    if _use_local():
        return _local_rerank(query, texts)

    # Remote chain
    scores = _orchestrator_rerank(query, texts)
    if scores and len(scores) == len(texts):
        return scores

    scores = _cohere_rerank(query, texts)
    if scores and len(scores) == len(texts):
        return scores

    if os.getenv("USE_LOCAL_EMBEDDER", "false").lower() == "true":
        return _local_rerank(query, texts)

    log.warning("All rerank providers failed — caller should fall back to BM25/RRF")
    return None
