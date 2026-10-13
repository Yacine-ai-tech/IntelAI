import pytest

pytestmark = pytest.mark.unit

from src.services.metric_aliases import expand_query


def test_reporting_name_gains_glossary_term():
    out = expand_query("Report the recorded value of Board Diversity Ratio for 2024-03.")
    assert out.startswith("Report the recorded value of Board Diversity Ratio for 2024-03.")
    assert "Board Diversity %" in out


def test_unrelated_query_is_unchanged():
    q = "What does the 2025 ESG report cover?"
    assert expand_query(q) == q


def test_whole_phrase_only():
    assert expand_query("customers by region") .endswith("(Customer Count)")
    assert expand_query("the customerservice desk") == "the customerservice desk"
