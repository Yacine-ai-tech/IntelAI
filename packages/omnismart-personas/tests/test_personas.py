import pytest
from omnismart_personas.templates import PERSONA_TEMPLATES, ROLE_PERSONA_MAP, Persona

def test_persona_templates_exist():
    assert len(PERSONA_TEMPLATES) > 0
    assert "ceo" in PERSONA_TEMPLATES

def test_persona_creation():
    raw = PERSONA_TEMPLATES["ceo"]
    ceo = Persona(
        name="ceo",
        display_name=raw["display_name"],
        system_prompt=raw["system_prompt"],
        allowed_tools=raw["allowed_tools"],
        data_access=raw["data_access"],
        temperature=raw["temperature"]
    )
    assert ceo.name == "ceo"
    assert ceo.temperature == 0.4
    assert ceo.can_access("Finance")
    assert ceo.can_access("growth")
    assert not ceo.can_access("Marketing")

def test_role_map():
    assert ROLE_PERSONA_MAP["ceo"] == "ceo"
    assert ROLE_PERSONA_MAP["admin"] == "general"
