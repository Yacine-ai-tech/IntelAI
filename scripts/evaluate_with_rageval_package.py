#!/usr/bin/env python3
"""
IntelAI RAG evaluation using the `omnismart-rageval` PyPI package, in-process.

Same tests/rag_eval.jsonl cases and the same IntelAI RAG pipeline (UltraFastRAG) as
scripts/evaluate_with_rageval.py, but scores them by calling the RAGEvaluator class
directly — no running RAGeval server, no network call, no evaluator URL/token to
configure. This is the "drop-in library" side of RAGeval; evaluate_with_rageval.py is
the "independent microservice" side — both exist so this repo demonstrates the actual
range of ways RAGeval is meant to be used, without hardcoding a dependency on it (this
script degrades to a clear, actionable error if the optional package isn't installed;
nothing else in IntelAI imports it).

Install: pip install omnismart-rageval
(not a core requirement.txt dependency — this script is illustrative/optional tooling)
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

try:
    from rageval.evaluator import RAGEvaluator
except ImportError:
    print("The `rageval` package isn't installed. Run: pip install omnismart-rageval", file=sys.stderr)
    sys.exit(1)

# Free-tier LLM judge rate limits — 0 to disable.
CALL_DELAY_SECONDS = float(os.getenv("RAGEVAL_CALL_DELAY_SECONDS", "5"))


def load_eval_cases() -> List[Dict[str, Any]]:
    eval_file = ROOT_DIR / "tests" / "rag_eval.jsonl"
    if not eval_file.exists():
        raise FileNotFoundError(f"eval set not found: {eval_file}")
    with open(eval_file) as f:
        return [json.loads(line) for line in f if line.strip()]


async def run_async() -> Dict[str, Any]:
    from src.services.omnismart_chatbot import UltraFastRAG

    cases = load_eval_cases()
    rag = UltraFastRAG()
    evaluator = RAGEvaluator()
    results: List[Dict[str, Any]] = []

    print(f"Evaluating {len(cases)} case(s) from tests/rag_eval.jsonl via the rageval package ...\n")

    for i, case in enumerate(cases, 1):
        query = case["query"]
        persona = case.get("persona", "analyst")
        t0 = time.monotonic()
        out = rag.answer(query, top_k=5, use_cache=False)
        latency_ms = (time.monotonic() - t0) * 1000
        answer = out.get("response", "")
        contexts = [
            f"{s.get('title', '')}: {s.get('snippet') or s.get('preview') or ''}"
            for s in out.get("sources", [])
        ]

        try:
            scores = await evaluator.score_interaction(
                query=query, answer=answer, chunks=contexts,
                tokens_used=0, latency_ms=latency_ms,
                model="intelai-ultrafast-rag", persona=persona,
            )
            g = scores.get("groundedness_consensus", {}).get("consensus", scores.get("groundedness"))
            result = {
                "case_id": i, "query": query, "persona": persona,
                "contexts_retrieved": len(contexts),
                "groundedness": g, "relevance": scores.get("relevance"),
                "faithfulness": scores.get("faithfulness"),
                "overall_quality": scores.get("overall_quality"),
                "flags": scores.get("flags", []),
            }
            print(f"[{i:02d}/{len(cases):02d}] persona={persona:<9} "
                  f"groundedness={g!s:<6} overall={scores.get('overall_quality')!s:<6} "
                  f"query='{query[:60]}'")
        except Exception as e:
            result = {"case_id": i, "query": query, "persona": persona, "error": str(e)}
            print(f"[{i:02d}/{len(cases):02d}] persona={persona:<9} ERROR: {e}")

        results.append(result)
        if CALL_DELAY_SECONDS and i < len(cases):
            time.sleep(CALL_DELAY_SECONDS)

    scored = [r for r in results if "error" not in r and r.get("overall_quality") is not None]
    n_errors = len(results) - len(scored)
    avg_groundedness = sum(r["groundedness"] for r in scored) / len(scored) if scored else None
    avg_overall = sum(r["overall_quality"] for r in scored) / len(scored) if scored else None

    summary = {
        "service_evaluated": "IntelAI UltraFastRAG",
        "evaluator": "rageval package (in-process, no network)",
        "total_cases": len(results),
        "scored_cases": len(scored),
        "failed_cases": n_errors,
        "avg_groundedness": round(avg_groundedness, 4) if avg_groundedness is not None else None,
        "avg_overall_quality": round(avg_overall, 4) if avg_overall is not None else None,
        "results": results,
    }

    out_dir = ROOT_DIR / "eval"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "RAGEVAL_PACKAGE_REPORT.json"
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n{len(scored)}/{len(results)} cases scored ({n_errors} failed — see report for detail).")
    if scored:
        print(f"avg groundedness: {avg_groundedness:.2%}   avg overall quality: {avg_overall:.2%}")
    print(f"report written to {out_path}")
    return summary


def run() -> Dict[str, Any]:
    return asyncio.run(run_async())


if __name__ == "__main__":
    run()
