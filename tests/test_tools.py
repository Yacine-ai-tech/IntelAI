"""Persona tool-whitelist enforcement."""
from src.services.tools import list_persona_tools, run_tool


def test_whitelist_blocks_out_of_scope_tool():
    # The CHRO persona may not run finance tools — blocked before any execution.
    out = run_tool("chro", "financial_statements", {})
    assert "error" in out and "whitelist" in out["error"].lower()


def test_unknown_persona_is_rejected():
    out = run_tool("not-a-persona", "kpi_query", {})
    assert "error" in out


def test_list_persona_tools_returns_whitelist():
    tools = list_persona_tools("cfo")
    assert "kpi_query" in tools


def test_in_scope_tool_passes_the_gate():
    # kpi_query is whitelisted for ceo → must get past enforcement (executes, or fails
    # downstream on data, but is never blocked by the whitelist).
    out = run_tool("ceo", "kpi_query", {"category": "Finance"})
    assert "whitelist" not in out.get("error", "")
    assert ("result" in out) or ("error" in out)
