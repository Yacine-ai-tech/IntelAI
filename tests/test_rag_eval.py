"""Structural validation of the RAG eval set (no LLM/DB needed → CI-safe).
The full groundedness run is `python -m src.data.rag_eval` (Studio/prod)."""
import json
from pathlib import Path

EVAL = Path(__file__).resolve().parents[1] / "src" / "data" / "rag_eval.jsonl"


def _load():
    return [json.loads(l) for l in EVAL.read_text().splitlines() if l.strip()]


def test_eval_set_exists_and_sized():
    rows = _load()
    assert len(rows) >= 20, "prompt-eval set should have >= 20 cases (STRATEGY §1.4)"


def test_eval_entries_well_formed():
    for r in _load():
        assert isinstance(r.get("query"), str) and r["query"].strip()
        assert isinstance(r.get("expected_keywords"), list) and r["expected_keywords"]
        assert all(isinstance(k, str) for k in r["expected_keywords"])
        assert 0.0 <= float(r.get("min_groundedness", 0.5)) <= 1.0


def test_eval_personas_valid():
    valid = {"ceo", "cfo", "cto", "coo", "chro", "esg", "risk", "analyst", "general"}
    for r in _load():
        assert r.get("persona", "general") in valid
