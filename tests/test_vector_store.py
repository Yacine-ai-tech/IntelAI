"""Vector store factory + fallback behaviour (hermetic — no heavy backends required).

``settings`` is a frozen dataclass, so we rebind the module-level ``settings`` reference
that the factory reads (not mutate the instance) to exercise each VECTOR_STORE value.
"""
from types import SimpleNamespace

from src.services import vector_store as vs


def _factory_for(kind: str):
    orig = vs.settings
    vs.settings = SimpleNamespace(VECTOR_STORE=kind)
    vs.reset_cache()
    try:
        return vs.get_vector_store()
    finally:
        vs.settings = orig
        vs.reset_cache()


def test_memory_returns_no_backend():
    """memory mode = no persistent backend; callers keep the in-process retrieval path."""
    assert _factory_for("memory") is None


def test_unknown_backend_falls_back_to_none():
    """An unknown VECTOR_STORE value must not raise — it degrades to the in-process path."""
    assert _factory_for("does-not-exist") is None


def test_vector_store_retrieve_signals_memory_with_none():
    orig = vs.settings
    vs.settings = SimpleNamespace(VECTOR_STORE="memory")
    vs.reset_cache()
    try:
        assert vs.vector_store_retrieve("anything", top_k=3) is None
    finally:
        vs.settings = orig
        vs.reset_cache()
