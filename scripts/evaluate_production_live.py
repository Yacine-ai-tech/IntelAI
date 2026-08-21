#!/usr/bin/env python3
"""
IntelAI RAG evaluation against the REAL, LIVE production deployment.

Unlike scripts/evaluate_with_rageval.py — which calls UltraFastRAG.answer() in-process,
so retrieval (embed + rerank, dozens of remote HTTP round trips) runs on whatever machine
executes the script — this script calls the live production POST /api/v1/chat/async +
GET /api/v1/chat/{job_id} endpoints for every case (not the synchronous POST
/api/v1/chat) — a cold-retrieval case can take 60-100s+, long enough to risk Cloudflare's
free-tier proxy cutting the connection (HTTP 524) on a single blocking request; polling
in short requests avoids that entirely. All retrieval work happens inside the real
deployed service itself; the machine running this script only ever sends/receives small
JSON payloads, plus makes the (also small, non-embedding) LLM judge calls to score each
answer. evaluate_with_rageval_package.py takes the same gateway-polling approach for
generation, for the same reliability reason — its own focus is the RAGeval PACKAGE's
mechanics (decorator, judge consensus), not retrieval, so it doesn't need in-process
retrieval either.

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
import re
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

GATEWAY = os.getenv("PROD_GATEWAY_URL", "[YOUR_APP]").rstrip("/")

# Best-effort model for RAGeval's cost_usd pricing lookup (see the comment at its use
# below) — production's own configured default, not a per-case exact match.
COST_ESTIMATE_MODEL = os.getenv("PROD_COST_ESTIMATE_MODEL", os.getenv("LLM_DEFAULT", "groq/openai/gpt-oss-120b"))


def load_eval_cases() -> List[Dict[str, Any]]:
    eval_file = ROOT_DIR / "tests" / "rag_eval.jsonl"
    with open(eval_file) as f:
        return [json.loads(line) for line in f if line.strip()]


def _retry(fn, attempts: int = 3, base_delay: float = 3.0):
    """Retries transient failures from THIS machine's own flaky connection (DNS
    resolution failures, TLS handshake timeouts) — distinct from a real error from the
    service being tested, which still fails after all attempts, honestly.

    A 429 gets its own, longer backoff (respecting Retry-After when the service sends
    one): three quick retries on a rate limit just add three more requests to an
    already-throttled window, which was observed live to poison every case for the
    rest of the run (the window never got a chance to clear). This does not raise the
    retry COUNT, only how long each 429-triggered wait is."""
    last_exc = None
    for attempt in range(attempts):
        try:
            return fn()
        except Exception as e:
            last_exc = e
            if attempt < attempts - 1:
                resp = getattr(e, "response", None)
                if resp is not None and resp.status_code == 429:
                    retry_after = resp.headers.get("Retry-After")
                    delay = float(retry_after) if retry_after else 30.0 * (attempt + 1)
                else:
                    delay = base_delay * (attempt + 1)
                time.sleep(delay)
    raise last_exc


def _poll_chat_job(client: httpx.Client, headers: Dict[str, str], job_id: str,
                    timeout: float = 180.0, interval: float = 3.0) -> Dict[str, Any]:
    """Polls GET /api/v1/chat/{job_id} until it's done|error, or raises after `timeout`
    seconds — generous relative to the ~50-60s a real cold-retrieval turn takes, since a
    poll request itself can never 524 (each one is small and fast; only the underlying
    chat turn is slow, and that now runs server-side without any client connection open)."""
    t0 = time.monotonic()
    while time.monotonic() - t0 < timeout:
        r = client.get(f"{GATEWAY}/api/v1/chat/{job_id}", headers=headers, timeout=30.0)
        r.raise_for_status()
        data = r.json()
        status = data.get("status")
        if status == "done":
            return data
        if status == "error":
            raise RuntimeError(f"chat job {job_id} failed: {data.get('error')}")
        time.sleep(interval)
    raise TimeoutError(f"chat job {job_id} did not complete within {timeout}s")


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


def _number_variants(value: float) -> List[str]:
    """Every plausible way an LLM might render `value` in prose — exact, 1/2-decimal
    rounding, comma-grouped, and K/M-abbreviated for large numbers — so a match
    isn't defeated by harmless formatting differences. Deliberately does NOT
    include a bare round-to-nearest-integer variant: for a value like 99.6, that
    would be "100", which is short and common enough to false-positive-match
    against unrelated text (confirmed: "roughly 100%" wrongly matched 99.6 in
    testing). Every variant here stays within ~0.05 of the true value."""
    variants = set()
    for v in (value, round(value, 1), round(value, 2)):
        variants.add(f"{v:g}")
    if abs(value) >= 1000:
        # A comma-grouped whole-number form ("4,378,004") is standard business
        # reporting for anything this large, and long/specific enough that a
        # coincidental match in unrelated text is effectively impossible — unlike
        # the short bare integers a small value like 99.6 would round to (see
        # module docstring above: that's exactly what "100" false-matched).
        variants.add(f"{value:,.0f}")
    if abs(value) >= 1_000_000:
        variants.add(f"{value / 1_000_000:.1f}M")
        variants.add(f"{value / 1_000_000:.2f}M")
    elif abs(value) >= 1_000:
        variants.add(f"{value / 1_000:.1f}K")
    return [v for v in variants if v]


def _check_ground_truth(answer: str, expected_value, expected_unit) -> "bool | None":
    """Objective correctness check: does the answer actually contain the real,
    known value from the live database — not a subjective LLM-judge opinion.
    Independent of any judge API being available, unlike groundedness_consensus.
    Returns None when the case has no ground-truth value to check (documents,
    glossary terms, cross-domain questions).

    Word-boundary matching, not plain substring — "100" must not match inside
    "1,100" or "10000", and a trailing "%"/unit character counts as a boundary."""
    if expected_value is None:
        return None
    try:
        value = float(expected_value)
    except (TypeError, ValueError):
        return None
    for variant in _number_variants(value):
        pattern = r"(?<![\d.,])" + re.escape(variant) + r"(?![\d])"
        if re.search(pattern, answer):
            return True
    return False


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

            def _call():
                r = client.post(f"{GATEWAY}/api/v1/chat/async", headers=headers,
                                 json={"message": query, "persona": persona})
                r.raise_for_status()  # inside the retried call, so 429/502/503 actually retry+backoff
                job_id = r.json()["job_id"]
                return _poll_chat_job(client, headers, job_id)

            try:
                out = _retry(_call)
                latency_ms = (time.monotonic() - t0) * 1000
                answer = out.get("response", "")
                contexts = [
                    f"{s.get('title', '')}: {s.get('snippet') or s.get('preview') or ''}"
                    for s in out.get("sources", [])
                ]
            except Exception as e:
                results.append({"case_id": i, "query": query, "persona": persona, "error": f"chat_call_failed: {e}"})
                print(f"[{i:02d}/{len(cases):02d}] persona={persona:<9} CHAT ERROR: {e}")
                resp_obj = getattr(e, "response", None)
                if resp_obj is not None and resp_obj.status_code == 429:
                    # Observed live: back-to-back 429s with no gap between cases kept the
                    # rate-limit window from ever clearing, poisoning every remaining case
                    # in the run. A short cooldown here costs little against 44 cases and
                    # gives the window an actual chance to reset before the next request.
                    print(f"           cooling down 45s after a 429 before the next case ...")
                    time.sleep(45.0)
                continue

            # Objective correctness — does the answer contain the real, known value
            # from the live DB? Always computed, independent of judge availability.
            ground_truth_match = _check_ground_truth(
                answer, case.get("expected_value"), case.get("expected_unit"))

            result = {
                "case_id": i, "query": query, "persona": persona, "kind": case.get("kind"),
                "contexts_retrieved": len(contexts), "latency_ms": round(latency_ms),
                "ground_truth_match": ground_truth_match,
            }

            # Judge-based groundedness is best-effort on top of the ground-truth check
            # above, not a precondition for recording a result — an unavailable judge
            # panel (e.g. no API credit) shouldn't discard a case that otherwise
            # produced a real, checkable answer.
            try:
                scores = asyncio.run(evaluator.score_interaction(
                    query=query, answer=answer, chunks=contexts,
                    tokens_used=out.get("tokens_used", 0), latency_ms=latency_ms,
                    # The live gateway response has no field naming which model actually
                    # answered this case, so cost_usd can only be estimated against the
                    # production default rather than the exact per-case model (a handful
                    # of personas' reasoning tier can differ — see BENCHMARK.md §3b). A
                    # literal sentinel like "intelai-production-live" here would silently
                    # price every case at $0 (RAGeval's cost table has no such entry) — this
                    # is a labeled best-effort estimate instead of a wrong-by-construction one.
                    model=COST_ESTIMATE_MODEL, persona=persona,
                ))
                g = scores.get("groundedness_consensus", {}).get("consensus", scores.get("groundedness"))
                result.update({
                    "groundedness": g, "relevance": scores.get("relevance"),
                    "faithfulness": scores.get("faithfulness"),
                    "overall_quality": scores.get("overall_quality"),
                    "cost_usd": scores.get("cost_usd"),
                    "flags": scores.get("flags", []),
                })
                print(f"[{i:02d}/{len(cases):02d}] persona={persona:<9} "
                      f"gt_match={ground_truth_match!s:<5} groundedness={g!s:<6} "
                      f"latency={latency_ms:.0f}ms query='{query[:50]}'")
            except Exception as e:
                result["judge_error"] = f"scoring_failed: {e}"
                print(f"[{i:02d}/{len(cases):02d}] persona={persona:<9} "
                      f"gt_match={ground_truth_match!s:<5} JUDGE UNAVAILABLE "
                      f"latency={latency_ms:.0f}ms query='{query[:50]}'")

            results.append(result)

    scored = [r for r in results if "error" not in r]
    n_errors = len(results) - len(scored)
    gt_applicable = [r for r in scored if r.get("ground_truth_match") is not None]
    gt_correct = [r for r in gt_applicable if r["ground_truth_match"]]
    ground_truth_accuracy = (len(gt_correct) / len(gt_applicable)) if gt_applicable else None
    judged = [r for r in scored if r.get("groundedness") is not None]
    avg_groundedness = sum(r["groundedness"] for r in judged) / len(judged) if judged else None
    overall_scored = [r for r in scored if r.get("overall_quality") is not None]
    avg_overall = sum(r["overall_quality"] for r in overall_scored) / len(overall_scored) if overall_scored else None
    avg_latency = sum(r["latency_ms"] for r in scored) / len(scored) if scored else None
    costed = [r for r in scored if r.get("cost_usd") is not None]
    total_cost_usd = sum(r["cost_usd"] for r in costed) if costed else None
    avg_cost_usd_per_case = (total_cost_usd / len(costed)) if costed else None

    summary = {
        "service_evaluated": "IntelAI production (live /api/v1/chat)",
        "gateway_url": GATEWAY,
        "total_cases": len(results),
        "scored_cases": len(scored),
        "failed_cases": n_errors,
        "ground_truth_applicable_cases": len(gt_applicable),
        "ground_truth_correct_cases": len(gt_correct),
        "ground_truth_accuracy": round(ground_truth_accuracy, 4) if ground_truth_accuracy is not None else None,
        "judged_cases": len(judged),
        "avg_groundedness": round(avg_groundedness, 4) if avg_groundedness is not None else None,
        "avg_overall_quality": round(avg_overall, 4) if avg_overall is not None else None,
        "avg_latency_ms": round(avg_latency) if avg_latency is not None else None,
        "total_cost_usd": round(total_cost_usd, 6) if total_cost_usd is not None else None,
        "avg_cost_usd_per_case": round(avg_cost_usd_per_case, 6) if avg_cost_usd_per_case is not None else None,
        "results": results,
    }

    out_dir = ROOT_DIR / "eval"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "RAGEVAL_PRODUCTION_LIVE_REPORT.json"
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n{'='*70}")
    print(f"Scored {len(scored)}/{len(results)} cases against LIVE production")
    print(f"Ground-truth accuracy: {summary['ground_truth_accuracy']} "
          f"({len(gt_correct)}/{len(gt_applicable)} applicable cases)")
    print(f"Avg groundedness (judged): {summary['avg_groundedness']} ({len(judged)} cases judged)")
    print(f"Avg overall quality:{summary['avg_overall_quality']}")
    print(f"Avg latency:        {summary['avg_latency_ms']}ms")
    print(f"Total cost:         ${summary['total_cost_usd']}")
    print(f"Avg cost/case:      ${summary['avg_cost_usd_per_case']}")
    print(f"Full report: {out_path}")
    return summary


if __name__ == "__main__":
    run()
