"""omnismart-personas — role-based, data-scoped LLM persona templates + router.

Quickstart::

    from omnismart_personas import persona_for_role, build_rag_prompt, scope_records

    persona = persona_for_role("cfo")            # CFO persona (Finance/Growth scope)
    rows = scope_records(persona, all_kpi_rows)  # drop out-of-scope domains
    prompt = build_rag_prompt(persona, "What drove the Q1 margin change?",
                              [f"{r['metric']}={r['value']}" for r in rows])
"""
from .templates import (
    DEFAULT_PERSONA,
    PERSONA_TEMPLATES,
    ROLE_PERSONA_MAP,
    Persona,
)
from .router import (
    get_persona,
    list_personas,
    persona_for_role,
    scope_records,
)
from .context import build_rag_prompt, build_system_prompt

__version__ = "0.1.0"

__all__ = [
    "Persona",
    "PERSONA_TEMPLATES",
    "ROLE_PERSONA_MAP",
    "DEFAULT_PERSONA",
    "get_persona",
    "persona_for_role",
    "list_personas",
    "scope_records",
    "build_system_prompt",
    "build_rag_prompt",
    "__version__",
]
