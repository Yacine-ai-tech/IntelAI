"""Cooperative progress + cancellation for the retrieval pipeline.

Retrieval is CPU-bound and, on a small host, can take many seconds (the cross-encoder
scores one query/passage pair per candidate). Instead of one opaque wait, each stage
reports what it is doing and the work stops between rerank batches when the caller has
given up, so an abandoned request no longer keeps the cores busy.

State is deliberately in-process and ephemeral: it describes a request that is running
right now, and a lost entry only means a poller sees a coarser status.
"""
from __future__ import annotations

import contextvars
import threading
import time
from typing import Any, Dict, List, Optional

_TTL_SECONDS = 900.0


class RetrievalCancelled(Exception):
    """Raised inside the pipeline when the request was cancelled or timed out."""


class ProgressBoard:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._items: Dict[str, Dict[str, Any]] = {}

    def update(self, key: str, **fields: Any) -> None:
        now = time.time()
        with self._lock:
            item = self._items.setdefault(key, {"started_at": now})
            item.update(fields)
            item["updated_at"] = now
            if len(self._items) > 512:
                cutoff = now - _TTL_SECONDS
                for k in [k for k, v in self._items.items() if v.get("updated_at", 0) < cutoff]:
                    self._items.pop(k, None)

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            item = self._items.get(key)
            return dict(item) if item else None

    def drop(self, key: str) -> None:
        with self._lock:
            self._items.pop(key, None)


board = ProgressBoard()


class RetrievalContext:
    """Carries the progress key and cancel flag for one retrieval call."""

    def __init__(self, key: Optional[str] = None) -> None:
        self.key = key
        self.cancel = threading.Event()
        self.preliminary: Optional[List[tuple]] = None

    def report(self, stage: str, **info: Any) -> None:
        if self.key:
            board.update(self.key, stage=stage, **info)

    def check(self) -> None:
        if self.cancel.is_set():
            raise RetrievalCancelled()
        if self.key:
            state = board.get(self.key)
            if state and state.get("cancelled"):
                self.cancel.set()
                raise RetrievalCancelled()


_current: contextvars.ContextVar[Optional[RetrievalContext]] = contextvars.ContextVar(
    "retrieval_context", default=None
)


def current() -> Optional[RetrievalContext]:
    return _current.get()


def bind(ctx: Optional[RetrievalContext]) -> contextvars.Token:
    return _current.set(ctx)


def unbind(token: contextvars.Token) -> None:
    _current.reset(token)


def snippet_rows(rows: List[tuple], limit: int = 600) -> List[Dict[str, Any]]:
    """Shape ``(title, content, score)`` rows for a JSON progress payload."""
    return [
        {"title": t, "content": (c or "")[:limit], "score": round(float(s), 4)}
        for t, c, s in rows
    ]


class RankedHits(list):
    """List of ``(title, content, score)`` rows with a flag for degraded ordering.

    ``partial`` is True when the cross-encoder pass was cut short and the rows are in
    fusion (RRF) order, so callers can say so instead of presenting them as final.
    """

    partial: bool = False
    stage: str = "done"


def progress_key() -> Optional[str]:
    return _key.get()


def set_progress_key(value: Optional[str]) -> contextvars.Token:
    return _key.set(value)


def reset_progress_key(token: contextvars.Token) -> None:
    _key.reset(token)


_key: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("retrieval_progress_key", default=None)


def retrieval_budget_seconds(pool: Optional[int] = None) -> float:
    """Wall-clock budget for one retrieval call.

    ``VECTOR_RETRIEVAL_TIMEOUT`` overrides everything when set. Otherwise the budget
    is a fixed allowance for embedding, vector search and BM25 plus a per-candidate
    allowance for the cross-encoder, so a larger pool is given the time it needs
    instead of hitting one fixed wall.
    """
    import os

    explicit = os.getenv("VECTOR_RETRIEVAL_TIMEOUT", "").strip()
    if explicit:
        return float(explicit)
    base = float(os.getenv("RETRIEVAL_BASE_TIMEOUT", "15"))
    per_pair = float(os.getenv("RETRIEVAL_TIMEOUT_PER_PAIR", "1.5"))
    if pool is None:
        pool = int(os.getenv("RERANK_CANDIDATES", "30"))
    return base + per_pair * max(1, pool)
