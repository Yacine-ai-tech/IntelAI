"""Context building — turn a persona + retrieved snippets into a ready-to-send prompt."""
from __future__ import annotations

from typing import Iterable, Optional

from .templates import Persona

_LANG_INSTRUCTION = {
    "en": "Reply in English.",
    "fr": "Répondez en français.",
}


def build_system_prompt(
    persona: Persona,
    *,
    language: str = "en",
    extra: Optional[str] = None,
) -> str:
    """Compose the persona's system prompt with a language directive, its data-access
    scope, and optional extra instructions."""
    parts = [
        persona.system_prompt,
        _LANG_INSTRUCTION.get(language, _LANG_INSTRUCTION["en"]),
        f"Data access scope: {', '.join(persona.data_access) or 'none'}. "
        "Never reference data outside this scope.",
    ]
    if extra:
        parts.append(extra.strip())
    return "\n\n".join(parts)


def build_rag_prompt(
    persona: Persona,
    query: str,
    snippets: Iterable[str],
    *,
    language: str = "en",
) -> str:
    """Build a full persona-routed RAG prompt: system prompt + retrieved context + query."""
    context = "\n".join(f"- {s}" for s in snippets) or "(no relevant context found)"
    return (
        f"{build_system_prompt(persona, language=language)}\n\n"
        f"RETRIEVED CONTEXT:\n{context}\n\n"
        f"USER QUERY: {query}\n\n"
        "Answer using only the retrieved context and your scope. Cite sources where relevant."
    )
