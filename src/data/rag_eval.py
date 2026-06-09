"""IntelAI prompt-eval — lightweight groundedness/recall check for the RAG copilot.

This is IntelAI's own demo-grade eval (the "prompt eval discipline" from STRATEGY §1.4),
NOT the standalone RAGeval product. It runs the eval set in ``tests/rag_eval.jsonl``
through the RAG, then reports keyword recall (did the answer mention the expected terms?)
and a groundedness proxy (are those terms supported by the retrieved sources?).

Run on the Studio / prod (needs LLM + seeded DB):
    python -m src.data.rag_eval
Gate: fails (exit 1) if >20% of cases fall below their groundedness threshold.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

EVAL_FILE = Path(__file__).resolve().parents[2] / "tests" / "rag_eval.jsonl"


def load_eval_set(path: Path = EVAL_FILE) -> List[Dict[str, Any]]:
    rows = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def _recall(keywords: List[str], text: str) -> float:
    if not keywords:
        return 1.0
    t = (text or "").lower()
    return sum(1 for k in keywords if k.lower() in t) / len(keywords)


def run(path: Path = EVAL_FILE) -> Dict[str, Any]:
    from src.services.omnismart_chatbot import UltraFastRAG

    rag = UltraFastRAG()
    cases = load_eval_set(path)
    results = []
    for c in cases:
        out = rag.answer(c["query"], top_k=5, use_cache=False)
        response = out.get("response", "")
        sources_text = " ".join(
            f"{s.get('title','')} {s.get('preview','')}" for s in out.get("sources", [])
        )
        ans_recall = _recall(c.get("expected_keywords", []), response)
        groundedness = _recall(c.get("expected_keywords", []), sources_text)
        passed = ans_recall >= 0.5 and groundedness >= c.get("min_groundedness", 0.5)
        results.append({
            "query": c["query"], "persona": c.get("persona", "general"),
            "answer_recall": round(ans_recall, 2), "groundedness": round(groundedness, 2),
            "passed": passed,
        })

    n = len(results)
    below = [r for r in results if r["groundedness"] < dict(zip(
        [c["query"] for c in cases], [c.get("min_groundedness", 0.5) for c in cases]
    ))[r["query"]]]
    summary = {
        "total": n,
        "passed": sum(1 for r in results if r["passed"]),
        "below_groundedness": len(below),
        "below_pct": round(100 * len(below) / n, 1) if n else 0.0,
        "results": results,
    }
    return summary


def main() -> None:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[2] / ".env")
    s = run()
    print(f"\nIntelAI RAG eval — {s['passed']}/{s['total']} passed, "
          f"{s['below_groundedness']} below groundedness ({s['below_pct']}%)\n")
    for r in s["results"]:
        mark = "✅" if r["passed"] else "❌"
        print(f"  {mark} [{r['persona']:>7}] recall={r['answer_recall']} "
              f"ground={r['groundedness']}  {r['query']}")
    # STRATEGY §1.4 gate: fail if >20% below groundedness threshold
    if s["below_pct"] > 20:
        print(f"\n⚠️  {s['below_pct']}% below groundedness threshold (>20%) — fix before shipping.")
        sys.exit(1)
    print("\n✅ Groundedness gate passed.")


if __name__ == "__main__":
    main()
