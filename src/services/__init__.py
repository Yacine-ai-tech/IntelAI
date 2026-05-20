"""Business logic services: forecasting, insights, RAG, financial statements.

This module exposes the high-level chatbot and related helpers but avoids
importing heavy submodules at import time to prevent circular import issues
during application startup (notably `omnismart_chatbot` <-> `pg_store`).

We provide lazy attribute access: the first time a symbol is requested the
implementation is imported from `src.services.omnismart_chatbot`.
"""

from typing import Any
import importlib

_LAZY_NAMES = [
    "OmniSmartChatbot",
    "MultiStepAgent",
    "UltraFastRAG",
    "RealTimeAnalyzer",
    "VoiceChatbot",
    "StructuredExtractor",
    "LightweightConversationalAgent",
    "get_omnismart_chatbot",
    "chat",
    "ingest_document",
    "search_web",
    "parse_pdf",
    "parse_docx",
    # Backward compatibility aliases exported below
]

__all__ = _LAZY_NAMES + ["AdvancedChatbot", "UnifiedChatbot", "ConversationalAgent"]


def _load_one(name: str) -> Any:
    """Import a single symbol from src.services.omnismart_chatbot on demand."""
    mod = importlib.import_module("src.services.omnismart_chatbot")
    return getattr(mod, name)


def __getattr__(name: str) -> Any:  # module-level lazy loader (PEP 562)
    if name in _LAZY_NAMES:
        val = _load_one(name)
        globals()[name] = val
        return val
    # backward-compatible aliases
    if name == "AdvancedChatbot":
        val = _load_one("OmniSmartChatbot")
        globals()[name] = val
        return val
    if name == "UnifiedChatbot":
        val = _load_one("OmniSmartChatbot")
        globals()[name] = val
        return val
    if name == "ConversationalAgent":
        val = _load_one("LightweightConversationalAgent")
        globals()[name] = val
        return val
    raise AttributeError(f"module {__name__} has no attribute {name}")


def __dir__():
    return sorted(list(globals().keys()) + _LAZY_NAMES)

