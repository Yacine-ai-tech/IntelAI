#!/usr/bin/env python3
"""
IntelAI RAG evaluation via a standalone RAGeval-compatible evaluation service.

Runs every case in tests/rag_eval.jsonl through IntelAI's own RAG pipeline
(UltraFastRAG), then sends {query, answer, contexts, persona} to an external evaluator's
POST /eval/score for multi-judge groundedness/relevance/faithfulness scoring — keeping
IntelAI's own process free of judge-model calls, the same "RAGeval is an independent
LLMOps microservice" separation STRATEGY.md's dependency rule asks for.

This is NOT hardcoded to any specific evaluator. RAG_EVALUATOR_URL has no default — if
you clone this repo and run your own evaluation service (RAGeval or otherwise) that
implements POST {url}/eval/score with {query,answer,contexts,persona} in ->
{overall_quality, groundedness, relevance, faithfulness, flags, ...} out, point this at
it. The upstream RAGeval project (github.com/Yacine-ai-tech/RAGeval, PyPI
`omnismart-rageval`) is one example that speaks this contract; see also
scripts/evaluate_with_rageval_package.py for the in-process, no-network alternative using
the RAGeval package directly.

Environment variables:
  RAG_EVALUATOR_URL    Base URL of the evaluator service (required — no default)
  RAG_EVALUATOR_TOKEN  Bearer token for the evaluator, if it requires one (optional)

On any per-case failure (network error, malformed response), that case is recorded with
an explicit "error" field and excluded from the averages — never a fabricated score. A
0% success rate is reported honestly as 0%, not backfilled with plausible-looking numbers.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

import httpx

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

RAG_EVALUATOR_URL = os.getenv("RAG_EVALUATOR_URL", "").strip().rstrip("/")
RAG_EVALUATOR_TOKEN = os.getenv("RAG_EVALUATOR_TOKEN", "").strip()


def load_eval_cases() -> List[Dict[str, Any]]:
    eval_file = ROOT_DIR / "tests" / "rag_eval.jsonl"
    if not eval_file.exists():
        raise FileNotFoundError(f"eval set not found: {eval_file}")
    with open(eval_file) as f:
        return [json.loads(line) for line in f if line.strip()]


def score_via_evaluator(client: httpx.Client, query: str, answer: str,
                         contexts: List[str], persona: str) -> Dict[str, Any]:
    headers = {"Content-Type": "application/json"}
    if RAG_EVALUATOR_TOKEN:
        headers["Authorization"] = f"Bearer {RAG_EVALUATOR_TOKEN}"
    resp = client.post(
        f"{RAG_EVALUATOR_URL}/eval/score",
        json={"query": query, "answer": answer, "contexts": contexts, "persona": persona,
              "model": "intelai-ultrafast-rag"},
        headers=headers,
        timeout=30.0,
    )
    resp.raise_for_status()
    return resp.json()


def run() -> Dict[str, Any]:
    if not RAG_EVALUATOR_URL:
        print("RAG_EVALUATOR_URL is not set — nothing to evaluate against.", file=sys.stderr)
        print("Point it at any service implementing POST {url}/eval/score "
              "(the upstream RAGeval project is one such service — see README).", file=sys.stderr)
        sys.exit(1)

    from src.services.omnismart_chatbot import UltraFastRAG

    cases = load_eval_cases()
    rag = UltraFastRAG()
    results: List[Dict[str, Any]] = []

    print(f"Evaluating {len(cases)} case(s) from tests/rag_eval.jsonl against {RAG_EVALUATOR_URL} ...\n")

    with httpx.Client() as client:
        for i, case in enumerate(cases, 1):
            query = case["query"]
            persona = case.get("persona", "analyst")
            out = rag.answer(query, top_k=5, use_cache=False)
            answer = out.get("response", "")
            contexts = [
                f"{s.get('title', '')}: {s.get('snippet') or s.get('preview') or ''}"
                for s in out.get("sources", [])
            ]

            try:
                scores = score_via_evaluator(client, query, answer, contexts, persona)
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

    scored = [r for r in results if "error" not in r and r.get("overall_quality") is not None]
    n_errors = len(results) - len(scored)
    avg_groundedness = sum(r["groundedness"] for r in scored) / len(scored) if scored else None
    avg_overall = sum(r["overall_quality"] for r in scored) / len(scored) if scored else None

    summary = {
        "service_evaluated": "IntelAI UltraFastRAG",
        "evaluator_url": RAG_EVALUATOR_URL,
        "total_cases": len(results),
        "scored_cases": len(scored),
        "failed_cases": n_errors,
        "avg_groundedness": round(avg_groundedness, 4) if avg_groundedness is not None else None,
        "avg_overall_quality": round(avg_overall, 4) if avg_overall is not None else None,
        "results": results,
    }

    out_dir = ROOT_DIR / "eval"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "RAGEVAL_API_REPORT.json"
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n{len(scored)}/{len(results)} cases scored ({n_errors} failed — see report for detail).")
    if scored:
        print(f"avg groundedness: {avg_groundedness:.2%}   avg overall quality: {avg_overall:.2%}")
    print(f"report written to {out_path}")
    return summary


if __name__ == "__main__":
    run()
