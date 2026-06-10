"""Business-logic services: persona-routed RAG copilot, retrieval, insights,
forecasting, and the per-domain analytics modules.

Heavy submodules (the chatbot ↔ pg_store graph) are imported lazily to avoid
import-time cycles during application startup. Access a symbol and it is
resolved from ``src.services.omnismart_chatbot`` on first use.
"""
from typing import Any
import importlib

_LAZY_NAMES = [
    "UltraFastRAG",
    "PersonaContext",
    "AgentPersonaFactory",
    "get_persona_factory",
    "normalize_sources",
    "PERSONA_TEMPLATES",
    "ROLE_PERSONA_MAP",
]

__all__ = list(_LAZY_NAMES)


def __getattr__(name: str) -> Any:  # PEP 562 module-level lazy loader
    if name in _LAZY_NAMES:
        mod = importlib.import_module("src.services.omnismart_chatbot")
        val = getattr(mod, name)
        globals()[name] = val
        return val
    raise AttributeError(f"module {__name__} has no attribute {name}")


def __dir__():
    return sorted(list(globals().keys()) + _LAZY_NAMES)
