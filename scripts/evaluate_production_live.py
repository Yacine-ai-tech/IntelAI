#!/usr/bin/env python3
"""
IntelAI RAG evaluation against the REAL, LIVE production deployment.

Unlike scripts/evaluate_with_rageval.py and evaluate_with_rageval_package.py — which
both call UltraFastRAG.answer() in-process, so retrieval (embed + rerank, dozens of
remote HTTP round trips) runs on whatever machine executes the script — this script
calls the live production POST /api/v1/chat endpoint for every case. All retrieval work
happens on Render's own network against the real deployed service; the machine running
this script only ever sends/receives small JSON payloads, plus makes the (also small,
non-embedding) LLM judge calls to score each answer.

Environment variables:
  PROD_GATEWAY_URL   Base URL of the live gateway (default: the real production domain)
  PROD_ADMIN_TOKEN   Pre-obtained admin JWT. If unset, this script calls
                      POST {PROD_GATEWAY_URL}/api/v1/auth/demo-login?role=admin itself.

Scoring uses the `rageval` package's RAGEvaluator directly (no running RAGeval service
needed) — same package, same judges (JUDGE_MODELS), as evaluate_with_rageval_package.py.
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

import httpx
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Judge LLM calls are RAGeval's job, not IntelAI's — load RAGeval's own .env for judge
# credentials (its own GROQ_API_KEY, separate from IntelAI's, so a bulk eval run can't
# exhaust the same daily quota IntelAI's live chat traffic depends on) rather than
# IntelAI's .env. This script has no other import that would load either as a side
# effect (see module docstring: no `src.*` import, so retrieval never runs on this
# machine) — RAGEVAL_ENV_PATH overrides the sibling-repo guess for other layouts.
_rageval_env = Path(os.getenv("RAGEVAL_ENV_PATH", "")) if os.getenv("RAGEVAL_ENV_PATH") else ROOT_DIR.parent / "RAGeval" / ".env"
if _rageval_env.exists():
    load_dotenv(_rageval_env)
else:
    print(f"Warning: RAGeval .env not found at {_rageval_env} — falling back to IntelAI's own .env "
          f"for judge credentials (this reintroduces the shared-Groq-quota problem).", file=sys.stderr)
    load_dotenv(ROOT_DIR / ".env")

try:
    from rageval.evaluator import RAGEvaluator
except ImportError:
    print("The `rageval` package isn't installed. Run: pip install omnismart-rageval", file=sys.stderr)
    sys.exit(1)

GATEWAY = os.getenv("PROD_GATEWAY_URL", "https://intelai.ysiddo-ai-projects.app").rstrip("/")


def load_eval_cases() -> List[Dict[str, Any]]:
    eval_file = ROOT_DIR / "tests" / "rag_eval.jsonl"
    with open(eval_file) as f:
        return [json.loads(line) for line in f if line.strip()]


def _retry(fn, attempts: int = 3, base_delay: float = 3.0):
    """Retries transient failures from THIS machine's own flaky connection (DNS
    resolution failures, TLS handshake timeouts) — distinct from a real error from the
    service being tested, which still fails after all attempts, honestly."""
    last_exc = None
    for attempt in range(attempts):
        try:
            return fn()
        except Exception as e:
            last_exc = e
            if attempt < attempts - 1:
                time.sleep(base_delay * (attempt + 1))
    raise last_exc


def get_admin_token(client: httpx.Client) -> str:
    token = os.getenv("PROD_ADMIN_TOKEN", "").strip()
    if token:
        return token
    resp = client.post(f"{GATEWAY}/api/v1/auth/demo-login", params={"role": "admin"}, timeout=30.0)
    resp.raise_for_status()
    return resp.json()["access_token"]


# Eval cases use domain-flavored persona tags (esg, finance, hr, ...) that don't all
# match ChatRequest.persona's real routing keys — map to the closest real persona so
# each case is actually routed the way a real user asking that question would be.
PERSONA_MAP = {
    "esg": "esg", "finance": "cfo", "hr": "chro", "it": "cio",
    "logistics": "coo", "operations": "coo", "growth": "ceo", "analyst": "ceo",
}


def run() -> Dict[str, Any]:
    cases = load_eval_cases()
    only = os.getenv("EVAL_ONLY_CASE_IDS", "").strip()
    if only:
        wanted = {int(x) for x in only.split(",") if x.strip()}
        cases = [c for idx, c in enumerate(cases, 1) if idx in wanted]
        case_ids = sorted(wanted)
    else:
        case_ids = list(range(1, len(cases) + 1))
    evaluator = RAGEvaluator()
    results: List[Dict[str, Any]] = []

    print(f"Evaluating {len(cases)} case(s) from tests/rag_eval.jsonl against LIVE production ({GATEWAY}) ...\n")

    with httpx.Client(timeout=120.0) as client:
        token = get_admin_token(client)
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        for i, case in zip(case_ids, cases):
            query = case["query"]
            persona = PERSONA_MAP.get(case.get("persona", ""), case.get("persona", "ceo"))
            t0 = time.monotonic()
            try:
                resp = _retry(lambda: client.post(f"{GATEWAY}/api/v1/chat", headers=headers,
                                                    json={"message": query, "persona": persona}))
                resp.raise_for_status()
                out = resp.json()
                latency_ms = (time.monotonic() - t0) * 1000
                answer = out.get("response", "")
                contexts = [
                    f"{s.get('title', '')}: {s.get('snippet') or s.get('preview') or ''}"
                    for s in out.get("sources", [])
                ]
            except Exception as e:
                results.append({"case_id": i, "query": query, "persona": persona, "error": f"chat_call_failed: {e}"})
                print(f"[{i:02d}/{len(cases):02d}] persona={persona:<9} CHAT ERROR: {e}")
                continue

            try:
                scores = asyncio.run(evaluator.score_interaction(
                    query=query, answer=answer, chunks=contexts,
                    tokens_used=out.get("tokens_used", 0), latency_ms=latency_ms,
                    model="intelai-production-live", persona=persona,
                ))
                g = scores.get("groundedness_consensus", {}).get("consensus", scores.get("groundedness"))
                result = {
                    "case_id": i, "query": query, "persona": persona,
                    "contexts_retrieved": len(contexts), "latency_ms": round(latency_ms),
                    "groundedness": g, "relevance": scores.get("relevance"),
                    "faithfulness": scores.get("faithfulness"),
                    "overall_quality": scores.get("overall_quality"),
                    "flags": scores.get("flags", []),
                }
                print(f"[{i:02d}/{len(cases):02d}] persona={persona:<9} "
                      f"groundedness={g!s:<6} overall={scores.get('overall_quality')!s:<6} "
                      f"latency={latency_ms:.0f}ms query='{query[:50]}'")
            except Exception as e:
                result = {"case_id": i, "query": query, "persona": persona, "error": f"scoring_failed: {e}"}
                print(f"[{i:02d}/{len(cases):02d}] persona={persona:<9} SCORE ERROR: {e}")

            results.append(result)

    scored = [r for r in results if "error" not in r and r.get("overall_quality") is not None]
    n_errors = len(results) - len(scored)
    avg_groundedness = sum(r["groundedness"] for r in scored) / len(scored) if scored else None
    avg_overall = sum(r["overall_quality"] for r in scored) / len(scored) if scored else None
    avg_latency = sum(r["latency_ms"] for r in scored) / len(scored) if scored else None

    summary = {
        "service_evaluated": "IntelAI production (live /api/v1/chat)",
        "gateway_url": GATEWAY,
        "total_cases": len(results),
        "scored_cases": len(scored),
        "failed_cases": n_errors,
        "avg_groundedness": round(avg_groundedness, 4) if avg_groundedness is not None else None,
        "avg_overall_quality": round(avg_overall, 4) if avg_overall is not None else None,
        "avg_latency_ms": round(avg_latency) if avg_latency is not None else None,
        "results": results,
    }

    out_dir = ROOT_DIR / "eval"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "RAGEVAL_PRODUCTION_LIVE_REPORT.json"
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n{'='*70}")
    print(f"Scored {len(scored)}/{len(results)} cases against LIVE production")
    print(f"Avg groundedness:   {summary['avg_groundedness']}")
    print(f"Avg overall quality:{summary['avg_overall_quality']}")
    print(f"Avg latency:        {summary['avg_latency_ms']}ms")
    print(f"Full report: {out_path}")
    return summary


if __name__ == "__main__":
    run()
