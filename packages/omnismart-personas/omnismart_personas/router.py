"""Persona routing — resolve personas by name or application role, list them, and
filter records to a persona's data-access scope."""
from __future__ import annotations

from typing import Any, Dict, List, Sequence

from .templates import (
    DEFAULT_PERSONA,
    PERSONA_TEMPLATES,
    ROLE_PERSONA_MAP,
    Persona,
)


def list_personas() -> List[str]:
    """All available persona keys (e.g. ``["ceo", "cfo", ...]``)."""
    return list(PERSONA_TEMPLATES.keys())


def get_persona(name: str) -> Persona:
    """Return the :class:`Persona` for ``name``, falling back to the default persona."""
    data = PERSONA_TEMPLATES.get((name or "").lower()) or PERSONA_TEMPLATES[DEFAULT_PERSONA]
    key = (name or DEFAULT_PERSONA).lower()
    if key not in PERSONA_TEMPLATES:
        key = DEFAULT_PERSONA
    return Persona(name=key, **data)


def persona_for_role(role: str) -> Persona:
    """Resolve the persona for an application ``role`` via ``ROLE_PERSONA_MAP``."""
    key = ROLE_PERSONA_MAP.get((role or "").lower(), DEFAULT_PERSONA)
    return get_persona(key)


def scope_records(
    persona: Persona,
    records: Sequence[Dict[str, Any]],
    domain_key: str = "category",
) -> List[Dict[str, Any]]:
    """Filter ``records`` to those in the persona's data-access scope.

    Each record is a mapping; ``domain_key`` names the field holding its business
    domain (default ``"category"``). Records without that field are dropped.
    """
    return [r for r in records if persona.can_access(str(r.get(domain_key, "")))]
