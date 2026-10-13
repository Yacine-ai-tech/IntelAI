"""Staged retrieval: pool sizing, BM25 reuse, progress, cancellation and budgets."""
import os
import sys
import types
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.services import retrieval_progress as rp  # noqa: E402

pytestmark = pytest.mark.unit


def test_pool_sizes_follow_strategy_defaults(monkeypatch):
    from src.services.vector_store import _pool_sizes
    for name in ("RETRIEVAL_DENSE_K", "RETRIEVAL_SPARSE_K", "RERANK_CANDIDATES"):
        monkeypatch.delenv(name, raising=False)
    assert _pool_sizes(5) == (50, 50, 30)
    assert _pool_sizes(20) == (50, 50, 60)  # never smaller than 3x the requested count
    monkeypatch.setenv("RERANK_CANDIDATES", "12")
    assert _pool_sizes(2)[2] == 12


def test_bm25_index_is_reused_until_the_corpus_changes():
    pytest.importorskip("rank_bm25")
    from src.services import vector_store as vs
    first = vs._bm25_index(["A", "B"], ["alpha text", "beta text"])
    assert vs._bm25_index(["A", "B"], ["alpha text", "beta text"]) is first
    assert vs._bm25_index(["A", "B"], ["alpha text", "gamma text"]) is not first


def test_budget_scales_with_pool_and_honours_override(monkeypatch):
    monkeypatch.delenv("VECTOR_RETRIEVAL_TIMEOUT", raising=False)
    monkeypatch.setenv("RETRIEVAL_BASE_TIMEOUT", "10")
    monkeypatch.setenv("RETRIEVAL_TIMEOUT_PER_PAIR", "2")
    assert rp.retrieval_budget_seconds(30) == 70
    assert rp.retrieval_budget_seconds(10) == 30
    monkeypatch.setenv("VECTOR_RETRIEVAL_TIMEOUT", "42")
    assert rp.retrieval_budget_seconds(30) == 42


def test_local_rerank_reports_progress_and_preserves_scores(monkeypatch):
    from src.services import hybrid_retrieval as hr

    class FakeCE:
        calls = []

        def predict(self, pairs, batch_size=8):
            FakeCE.calls.append(len(pairs))
            return [float(len(t)) for _, t in pairs]

    class FakeRetriever:
        reranker_model_name = "fake"

        def _ensure_reranker(self, force=False):
            return FakeCE()

    monkeypatch.setattr(hr, "_RERANKER", True)
    monkeypatch.setattr(hr, "_RERANK_RETRIEVER", FakeRetriever())
    monkeypatch.setenv("RERANK_BATCH_SIZE", "3")
    texts = ["ccc", "a", "bb", "dddd", "eeeee", "ffffff", "g"]
    ctx = rp.RetrievalContext(key="job-progress")
    token = rp.bind(ctx)
    try:
        scores = hr._rerank_local("q", texts)
    finally:
        rp.unbind(token)
    assert scores == [float(len(t)) for t in texts]       # order of inputs preserved
    assert FakeCE.calls == [3, 3, 1]                       # chunked, length-sorted
    state = rp.board.get("job-progress")
    assert state["stage"] == "reranking" and state["done"] == 7 and state["total"] == 7


def test_cancellation_stops_between_batches(monkeypatch):
    from src.services import hybrid_retrieval as hr

    class FakeCE:
        n = 0

        def predict(self, pairs, batch_size=8):
            FakeCE.n += 1
            return [0.0] * len(pairs)

    class FakeRetriever:
        reranker_model_name = "fake"

        def _ensure_reranker(self, force=False):
            return FakeCE()

    monkeypatch.setattr(hr, "_RERANKER", True)
    monkeypatch.setattr(hr, "_RERANK_RETRIEVER", FakeRetriever())
    monkeypatch.setenv("RERANK_BATCH_SIZE", "2")
    ctx = rp.RetrievalContext(key="job-cancel")
    ctx.cancel.set()
    token = rp.bind(ctx)
    try:
        with pytest.raises(rp.RetrievalCancelled):
            hr._rerank_local("q", ["a", "b", "c", "d"])
    finally:
        rp.unbind(token)
    assert FakeCE.n == 0


def test_board_cancel_flag_is_seen_by_context():
    ctx = rp.RetrievalContext(key="job-flag")
    rp.board.update("job-flag", stage="reranking")
    ctx.check()
    rp.board.update("job-flag", cancelled=True)
    with pytest.raises(rp.RetrievalCancelled):
        ctx.check()


def test_model_loads_share_one_lock():
    from src.services import hybrid_retrieval as hr
    assert hr._LOCAL_EMBEDDERS_LOCK is hr._LOCAL_RERANKER_LOAD_LOCK is hr._MODEL_LOAD_LOCK
