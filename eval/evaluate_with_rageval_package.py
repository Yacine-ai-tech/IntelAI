"""
IntelAI RAG Evaluation using the installed PyPI `omnismart-rageval` package.

This script demonstrates evaluating the IntelAI RAG pipeline using the `rageval` 
Python package installed from PyPI, proving its effectiveness as a drop-in evaluator.
"""
import json
import os
import sys
import asyncio
import time
from pathlib import Path
from typing import Any, Dict, List

# Ensure IntelAI root is in path
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from src.services.omnismart_chatbot import UltraFastRAG

# Import RAGEvaluator from the installed package
try:
    from rageval.evaluator import RAGEvaluator
except ImportError:
    print("❌ Error: `rageval` package is not installed.")
    print("Please run: pip install omnismart-rageval[eval]")
    sys.exit(1)


async def evaluate_query_with_package(
    evaluator: RAGEvaluator, query: str, answer: str, contexts: List[str], persona: str
) -> Dict[str, Any]:
    """Score the interaction using the local RAGEvaluator instance."""
    try:
        # Score the interaction
        scores = await evaluator.score_interaction(
            query=query,
            answer=answer,
            chunks=contexts,
            tokens_used=0,  # Evaluator will compute its own LLM usage during scoring
            latency_ms=0.0,
            model="intelai-ultrafast-rag",
            persona=persona,
        )
        return scores
    except Exception as e:
        print(f"  ⚠️ rageval package evaluation failed ({e}) — returning fallback score")
        return {"overall_quality": 0.0, "groundedness": 0.0, "relevance": 0.0, "error": str(e)}


async def run_rageval_audit_async() -> Dict[str, Any]:
    eval_file = ROOT_DIR / "src" / "data" / "rag_eval.jsonl"
    if not eval_file.exists():
        eval_file = ROOT_DIR / "tests" / "rag_eval.jsonl"

    with open(eval_file, "r") as f:
        cases = [json.loads(line) for line in f if line.strip()]

    rag = UltraFastRAG()
    results = []

    # Initialize the PyPI RAGEvaluator
    print(f"🚀 Evaluating {len(cases)} queries via PyPI `rageval` package...\n")
    evaluator = RAGEvaluator()

    for i, c in enumerate(cases, 1):
        query = c["query"]
        persona = c.get("persona", "cfo")
        out = rag.answer(query, top_k=5, use_cache=False)
        answer = out.get("response", "")
        contexts = [
            f"{s.get('title', '')}: {s.get('snippet') or s.get('preview') or ''}"
            for s in out.get("sources", [])
        ]

        # Use the package evaluator asynchronously
        scores = await evaluate_query_with_package(evaluator, query, answer, contexts, persona)
        
        g_consensus = scores.get("groundedness_consensus", {}).get("consensus", scores.get("groundedness", 0.0))

        results.append({
            "case_id": i,
            "query": query,
            "persona": persona,
            "answer": answer[:120] + "..." if len(answer) > 120 else answer,
            "contexts_retrieved": len(contexts),
            "groundedness": g_consensus,
            "relevance": scores.get("relevance", 0.0),
            "faithfulness": scores.get("faithfulness", 0.0),
            "overall_quality": scores.get("overall_quality", 0.0),
            "flags": scores.get("flags", [])
        })

        print(f"[{i:02d}/{len(cases):02d}] Persona: {persona:<7} | Groundedness: {g_consensus:.2f} | Overall: {scores.get('overall_quality', 0.0):.2f} | Query: '{query}'")
        
        # Sleep to avoid Groq and Gemini rate limits on the free tier
        if i < len(cases):
            time.sleep(15)

    avg_groundedness = sum(r["groundedness"] for r in results) / max(len(results), 1)
    avg_overall = sum(r["overall_quality"] for r in results) / max(len(results), 1)

    audit_summary = {
        "service_evaluated": "IntelAI UltraFastRAG",
        "evaluator_service": "RAGeval (PyPI Package)",
        "total_queries": len(results),
        "avg_groundedness": round(avg_groundedness, 4),
        "avg_overall_quality": round(avg_overall, 4),
        "results": results
    }

    out_json = ROOT_DIR / "eval" / "RAGEVAL_PACKAGE_AUDIT_REPORT.json"
    with open(out_json, "w") as f:
        json.dump(audit_summary, f, indent=2)

    print(f"\n✅ Audit complete! Avg Groundedness: {avg_groundedness:.2%}, Avg Quality: {avg_overall:.2%}")
    print(f"📄 Report written to {out_json}")
    return audit_summary

def run_rageval_audit():
    asyncio.run(run_rageval_audit_async())

if __name__ == "__main__":
    run_rageval_audit()
