from omnismart_personas import (
    Persona,
    get_persona,
    persona_for_role,
    list_personas,
    scope_records,
    build_system_prompt,
    build_rag_prompt,
)


def test_nine_personas():
    assert len(list_personas()) == 9
    assert "cfo" in list_personas()


def test_get_persona_known_and_fallback():
    assert get_persona("cfo").name == "cfo"
    assert get_persona("does-not-exist").name == "general"  # safe fallback


def test_persona_for_role_mapping():
    assert persona_for_role("hr").name == "chro"     # role → persona
    assert persona_for_role("it").name == "cto"
    assert persona_for_role("unknown").name == "general"


def test_data_access_scoping():
    cfo = get_persona("cfo")
    assert cfo.can_access("Finance") and not cfo.can_access("People")
    chro = get_persona("chro")
    assert chro.can_access("People") and not chro.can_access("Finance")


def test_scope_records_filters_out_of_scope():
    rows = [
        {"category": "Finance", "metric": "revenue", "value": 10},
        {"category": "People", "metric": "headcount", "value": 50},
    ]
    cfo_rows = scope_records(get_persona("cfo"), rows)
    assert len(cfo_rows) == 1 and cfo_rows[0]["category"] == "Finance"


def test_build_system_prompt_includes_scope_and_language():
    p = get_persona("cfo")
    sp = build_system_prompt(p, language="fr")
    assert "Finance" in sp and "français" in sp


def test_build_rag_prompt_includes_query_and_context():
    p = get_persona("analyst")
    prompt = build_rag_prompt(p, "Why did margin fall?", ["gross_margin=0.42"])
    assert "Why did margin fall?" in prompt and "gross_margin=0.42" in prompt


def test_persona_is_frozen_dataclass():
    p = get_persona("ceo")
    assert isinstance(p, Persona)
    try:
        p.temperature = 0.9  # type: ignore[misc]
        raise AssertionError("Persona should be immutable")
    except Exception:
        pass
