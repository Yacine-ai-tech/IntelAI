#!/usr/bin/env python3
"""
Showcase of the `omnismart-rageval` PyPI PACKAGE's own capabilities — NOT a RAG-quality
benchmark of IntelAI itself.

eval/RAGEVAL_PRODUCTION_LIVE_REPORT.json (scripts/evaluate_production_live.py) is the
report for "how good is IntelAI's live production RAG" (N=50, against the real deployed
API). This script answers a different question: "what does the RAGeval package actually
do for you, mechanically, when you drop it into a RAG pipeline?" — and demonstrates each
of its differentiating features (see RAGeval's own README's feature table) with real
calls, not a description:

  1. The `@track` decorator — the package's actual "60-second pitch" integration path
     (`from rageval import track; @track(...)`), run against a local, isolated demo
     store (never RAGeval's real production Postgres) so this is real, working
     instrumentation, not a mocked example.
  2. Multi-judge consensus with disagreement detection — every case's full judge panel
     breakdown (which judges responded, their individual scores, the stdev across them,
     whether that stdev crossed the JUDGE_DISAGREEMENT threshold) is recorded, not just
     the averaged number.
  3. Cost + latency tracking, computed from the RAG pipeline's REAL reported token usage.
  4. Persona-awareness — `PERSONA_SCOPE_VIOLATION` flag occurrences, grouped by persona.

Answer generation calls the same live gateway scripts/evaluate_production_live.py uses
(POST /api/v1/chat/async + poll), rather than instantiating IntelAI's RAG pipeline
in-process — deliberately: this script's job is to exercise the RAGeval PACKAGE (the
decorator, the evaluator, the judge panel), which all run genuinely in-process either
way, and pulling real, correct answers from a warm production backend is more reliable
than a cold local retrieval stack for that purpose (same reasoning
evaluate_production_live.py's own docstring gives for calling the deployed API rather
than instantiating the pipeline locally).

Two separate LLM credential sets are in play — IntelAI's own (implicitly, on the
production side, serving the chat calls) and RAGeval's own (driving the judge calls in
THIS process) — RAGeval's .env is loaded explicitly for the judge credentials, mirroring
scripts/evaluate_production_live.py's module docstring on why that separation matters
(a bulk eval run's judge calls must not compete with real chat traffic for the same
provider quota).

Install: pip install omnismart-rageval
(not a core requirements.txt dependency — this script is illustrative/optional tooling)
"""
from __future__ import annotations

import asyncio
import json
import os
import sqlite3
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

import httpx
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Judge LLM calls are RAGeval's job, not IntelAI's — load RAGeval's own .env for judge
# credentials (a separate quota from IntelAI's own), same rationale as
# scripts/evaluate_production_live.py's module docstring.
_rageval_env_path = (Path(os.getenv("RAGEVAL_ENV_PATH", "")) if os.getenv("RAGEVAL_ENV_PATH")
                      else ROOT_DIR.parent / "RAGeval" / ".env")
if _rageval_env_path.exists():
    load_dotenv(_rageval_env_path)
else:
    print(f"Warning: RAGeval .env not found at {_rageval_env_path} — falling back to "
          f"IntelAI's own .env for judge credentials.", file=sys.stderr)
    load_dotenv(ROOT_DIR / ".env")

try:
    from rageval.evaluator import RAGEvaluator, MIN_JUDGES_REQUIRED
    from rageval import track, flush as rageval_flush
    from rageval._compat import settings as rageval_settings
except ImportError:
    print("The `rageval` package isn't installed. Run: pip install omnismart-rageval", file=sys.stderr)
    sys.exit(1)

GATEWAY = os.getenv("PROD_GATEWAY_URL", "https://intelai.ysiddo-ai-projects.app").rstrip("/")
# Best-effort model for RAGeval's cost_usd pricing lookup — the live gateway's response
# has no field naming which model actually answered (see the identical note in
# scripts/evaluate_production_live.py); this is production's configured default.
COST_ESTIMATE_MODEL = os.getenv("PROD_COST_ESTIMATE_MODEL", os.getenv("LLM_DEFAULT", "groq/openai/gpt-oss-120b"))

# Isolated local demo store for the @track decorator run — deliberately NOT RAGeval's
# real production Postgres store, so this demo can never write fake rows into real
# telemetry. Deleted and recreated fresh on each run.
_DEMO_DB_PATH = ROOT_DIR / "eval" / ".rageval_package_demo.db"

# Eval cases use domain-flavored persona tags that don't all match the real routing
# keys (ceo/cfo/cto/coo/chro/esg/risk/analyst/general) — map to the closest real one.
PERSONA_MAP = {
    "esg": "esg", "finance": "cfo", "hr": "chro", "it": "cto",
    "logistics": "coo", "operations": "coo", "growth": "ceo", "analyst": "analyst",
}

DEFAULT_N_CASES = int(os.getenv("RAGEVAL_PACKAGE_N_CASES", "12"))
N_DECORATOR_CASES = min(3, DEFAULT_N_CASES)  # first N cases go through @track specifically
CALL_DELAY_SECONDS = float(os.getenv("RAGEVAL_CALL_DELAY_SECONDS", "2"))
# How many times to retry a case whose judge panel didn't reach MIN_JUDGES_REQUIRED —
# each attempt is bounded by JUDGE_TIMEOUT per judge, so this multiplies real wall-clock
# time; default 1 (no retry) since a judge provider's DAILY quota being exhausted (a
# real condition hit while developing this script — see run_direct_evaluator_demo's
# docstring) doesn't clear on retry, unlike a transient network blip.
JUDGE_RETRY_ATTEMPTS = int(os.getenv("RAGEVAL_JUDGE_RETRY_ATTEMPTS", "1"))


def load_eval_cases(n: int) -> List[Dict[str, Any]]:
    eval_file = ROOT_DIR / "tests" / "rag_eval.jsonl"
    if not eval_file.exists():
        raise FileNotFoundError(f"eval set not found: {eval_file}")
    with open(eval_file) as f:
        all_cases = [json.loads(line) for line in f if line.strip()]
    # Stride across the file rather than always taking the first N, so a small demo
    # subset still spans multiple kinds/personas instead of one cluster.
    step = max(1, len(all_cases) // n)
    return all_cases[::step][:n]


def _persona_for(case: Dict[str, Any]) -> str:
    raw = case.get("persona", "analyst")
    return PERSONA_MAP.get(raw, raw if raw in
                            {"ceo", "cfo", "cto", "coo", "chro", "esg", "risk", "analyst", "general"}
                            else "analyst")


def _retry(fn, attempts: int = 3, base_delay: float = 3.0):
    """Same transient-failure retry as scripts/evaluate_production_live.py — see that
    module for the full rationale (429s get their own longer, Retry-After-aware backoff)."""
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
    resp = _retry(lambda: client.post(f"{GATEWAY}/api/v1/auth/demo-login",
                                       params={"role": "admin"}, timeout=30.0))
    resp.raise_for_status()
    return resp.json()["access_token"]


def fetch_real_answers(cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Real generation material for this demo: each case's actual answer, sources, and
    reported token usage from the live production gateway (see module docstring for why
    generation happens here rather than via an in-process pipeline call)."""
    fetched: List[Dict[str, Any]] = []
    with httpx.Client(timeout=120.0) as client:
        token = get_admin_token(client)
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        for i, case in enumerate(cases, 1):
            query = case["query"]
            persona = _persona_for(case)
            t0 = time.monotonic()

            def _call():
                r = client.post(f"{GATEWAY}/api/v1/chat/async", headers=headers,
                                 json={"message": query, "persona": persona})
                r.raise_for_status()
                job_id = r.json()["job_id"]
                return _poll_chat_job(client, headers, job_id)

            try:
                out = _retry(_call)
                latency_ms = (time.monotonic() - t0) * 1000
                answer = out.get("response", "")
                contexts = [f"{s.get('title', '')}: {s.get('snippet') or s.get('preview') or ''}"
                            for s in out.get("sources", [])]
                fetched.append({
                    "case": case, "persona": persona, "query": query, "answer": answer,
                    "chunks": contexts, "tokens_used": out.get("tokens_used", 0),
                    "latency_ms": latency_ms,
                })
                print(f"[fetch {i:02d}/{len(cases):02d}] persona={persona:<8} "
                      f"tokens={out.get('tokens_used', 0):<6} latency={latency_ms:.0f}ms "
                      f"query='{query[:45]}'")
            except Exception as e:
                print(f"[fetch {i:02d}/{len(cases):02d}] persona={persona:<8} CHAT ERROR: {e}")
    return fetched


async def run_decorator_demo(fetched: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Phase A: the package's actual drop-in-decorator integration path, for real.

    Wraps a real, already-fetched RAG answer with `@track` exactly as README.md's
    "60-Second Pitch" shows, against an isolated local SQLite store. The sync wrapper's
    evaluation runs fire-and-forget on a background thread (see rageval/decorator.py) —
    `flush()` blocks until those in-flight background evaluations land, so this can
    honestly read the store back afterward and report what's actually in it. Note the
    decorator estimates tokens from word counts (see its own docstring) rather than
    taking an exact count — a real, documented characteristic of the "zero extra
    plumbing" drop-in path, not a bug.

    A case is retried (fresh @track call) up to `attempts` times if RAGeval's judge
    panel doesn't reach MIN_JUDGES_REQUIRED — observed live in this environment as
    real, transient judge-provider unavailability (a 503 from an overloaded provider,
    a timed-out call), not a defect in the decorator itself; the decorator's own
    fire-and-forget contract has no retry of its own; this loop adds one for a cleaner
    demo run rather than reporting a false negative for the mechanism being showcased.
    """
    if _DEMO_DB_PATH.exists():
        _DEMO_DB_PATH.unlink()
    os.environ["RAGEVAL_DB_PATH"] = str(_DEMO_DB_PATH)
    # Force this demo onto the local SQLite store, never RAGeval's real Postgres — even
    # if RAGEVAL_POSTGRES_URL is set in the environment (from RAGeval's .env, loaded
    # above), `rageval.store` checks `settings.POSTGRES_URL` at call time via this same
    # _compat module, so clearing it here is what actually redirects writes.
    rageval_settings.POSTGRES_URL = ""

    @track(model=COST_ESTIMATE_MODEL)
    def _tracked_replay(query: str, context_chunks: List[str]) -> Dict[str, Any]:
        # Stands in for the caller's own RAG call in README.md's usage example — the
        # decorator only cares that the wrapped function returns {"answer", "chunks"};
        # it doesn't know or need to know this answer came from a prior HTTP call.
        return {"answer": _REPLAY_ANSWERS[query], "chunks": context_chunks}

    global _REPLAY_ANSWERS
    _REPLAY_ANSWERS = {}

    def _rows_for(query: str) -> list:
        conn = sqlite3.connect(_DEMO_DB_PATH)
        try:
            return conn.execute("SELECT id FROM rageval_log WHERE query = ?", (query,)).fetchall()
        except sqlite3.OperationalError:
            return []
        finally:
            conn.close()

    for item in fetched:
        _REPLAY_ANSWERS[item["query"]] = item["answer"]
        for attempt in range(JUDGE_RETRY_ATTEMPTS):
            _tracked_replay(item["query"], item["chunks"])
            rageval_flush(timeout=45.0)
            if _rows_for(item["query"]):
                break
            if attempt < JUDGE_RETRY_ATTEMPTS - 1:
                print(f"  (decorator eval for '{item['query'][:40]}' didn't land — "
                      f"retrying, attempt {attempt + 2}/{JUDGE_RETRY_ATTEMPTS})")
        time.sleep(CALL_DELAY_SECONDS)

    conn = sqlite3.connect(_DEMO_DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        rows = [dict(r) for r in conn.execute(
            "SELECT query, persona, model, relevance, groundedness, faithfulness, "
            "cost_usd, latency_ms, tokens_used, flags FROM rageval_log ORDER BY id"
        ).fetchall()]
    except sqlite3.OperationalError:
        rows = []
    conn.close()

    return {
        "cases_instrumented": len(fetched),
        "rows_persisted_after_flush": len(rows),
        "store_path": "eval/.rageval_package_demo.db (local, isolated — never RAGeval's production store)",
        "tokens_estimated_by_decorator": True,
        "rows": rows,
    }


async def run_direct_evaluator_demo(fetched: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Phase B: direct calls into `RAGEvaluator`'s scoring methods — the "independent
    library, no server" side of the package. Used (rather than the decorator) for the
    bulk of cases here because it can report the full judge-consensus breakdown
    (per-judge scores, stdev, flag_for_review) and takes the REAL reported token count
    directly — the decorator's fire-and-forget path only persists the averaged
    consensus score against its own word-count token estimate, which is enough to
    prove the decorator works (phase A) but not enough to report exact cost or
    disagreement detail.

    Calls relevance/faithfulness/groundedness as three separate calls rather than via
    `score_interaction()`'s single all-or-nothing gather (which re-raises if ANY of the
    three fails, discarding the two that succeeded) — relevance and faithfulness don't
    depend on the judge panel at all, so a real, external judge-provider outage
    shouldn't blank out data that never needed a judge in the first place. This surfaced
    live during this report's own generation: RAGeval's judge providers hit genuine
    external constraints mid-run (Anthropic account low on credit, Gemini's free-tier
    daily quota exhausted by this same session's testing) — `groundedness` on any
    affected case is reported as unavailable with the real reason, not silently dropped
    or backfilled.
    """
    evaluator = RAGEvaluator()
    results: List[Dict[str, Any]] = []
    for i, item in enumerate(fetched, 1):
        query, persona, answer, chunks = item["query"], item["persona"], item["answer"], item["chunks"]
        relevance = evaluator.score_retrieval_relevance(query, chunks)
        faithfulness = evaluator.score_faithfulness(answer, chunks)
        cost_usd = RAGEvaluator.calculate_cost(item["tokens_used"], COST_ESTIMATE_MODEL)
        scope_violations = RAGEvaluator._persona_scope_flags(answer, persona)

        result: Dict[str, Any] = {
            "case_id": i, "query": query, "persona": persona, "kind": item["case"].get("kind"),
            "contexts_retrieved": len(chunks), "latency_ms": round(item["latency_ms"]),
            "tokens_used": item["tokens_used"], "relevance": relevance,
            "faithfulness": faithfulness, "cost_usd": cost_usd,
            "persona_scope_violations": scope_violations,
        }

        groundedness = None
        for attempt in range(JUDGE_RETRY_ATTEMPTS):
            try:
                # Outer safety timeout on top of RAGeval's own per-judge JUDGE_TIMEOUT —
                # defensive: a hung call with no bounded timeout anywhere in the chain
                # (litellm/genai SDK internals) has been observed live to stall a run for
                # hours (see RAGeval's own decorator.py module docstring for the exact
                # precedent), which a demo script generating a small, bounded report
                # cannot tolerate.
                consensus = await asyncio.wait_for(
                    evaluator.score_groundedness_consensus(answer, "\n".join(chunks)),
                    timeout=float(os.getenv("JUDGE_TIMEOUT", "30")) * 2 + 15,
                )
                groundedness = consensus.get("consensus")
                result.update({
                    "groundedness": groundedness,
                    "judge_consensus_stdev": consensus.get("stdev"),
                    "judges_used": consensus.get("judges_used"),
                    "judge_scores": consensus.get("judges"),
                    "judge_disagreement": bool(consensus.get("flag_for_review")),
                })
                break
            except Exception as e:
                if attempt < JUDGE_RETRY_ATTEMPTS - 1:
                    print(f"  (judge panel unavailable for '{query[:40]}' — retrying, "
                          f"attempt {attempt + 2}/{JUDGE_RETRY_ATTEMPTS}: {e})")
                    continue
                result["groundedness_unavailable_reason"] = str(e)

        if groundedness is not None:
            result["overall_quality"] = round(0.4 * relevance + 0.4 * groundedness + 0.2 * faithfulness, 5)
            print(f"[score {i:02d}/{len(fetched):02d}] persona={persona:<8} "
                  f"groundedness={groundedness!s:<6} judges={result.get('judges_used')} "
                  f"stdev={result.get('judge_consensus_stdev')!s:<6} "
                  f"cost=${cost_usd:.6f} query='{query[:45]}'")
        else:
            print(f"[score {i:02d}/{len(fetched):02d}] persona={persona:<8} "
                  f"relevance={relevance:.3f} faithfulness={faithfulness:.3f} "
                  f"GROUNDEDNESS UNAVAILABLE (judge panel) cost=${cost_usd:.6f} query='{query[:45]}'")

        results.append(result)
        if CALL_DELAY_SECONDS and i < len(fetched):
            time.sleep(CALL_DELAY_SECONDS)

    return results


def _package_version() -> str:
    try:
        from importlib.metadata import version
        return version("omnismart-rageval")
    except Exception:
        return "unknown"


async def run_async() -> Dict[str, Any]:
    all_cases = load_eval_cases(DEFAULT_N_CASES)
    print(f"RAGeval package capability demo — {len(all_cases)} case(s) from tests/rag_eval.jsonl, "
          f"answers pulled from live production ({GATEWAY}) ...\n")

    fetched = fetch_real_answers(all_cases)
    decorator_material = fetched[:N_DECORATOR_CASES]
    direct_material = fetched[N_DECORATOR_CASES:]

    print(f"\n── Phase A: @track decorator ({len(decorator_material)} case(s), isolated local store) ──")
    decorator_demo = await run_decorator_demo(decorator_material)
    print(f"{decorator_demo['rows_persisted_after_flush']}/{decorator_demo['cases_instrumented']} "
          f"decorator-instrumented interactions persisted to {decorator_demo['store_path']}\n")

    print(f"── Phase B: direct RAGEvaluator scoring "
          f"({len(direct_material)} case(s), full judge-panel detail) ──")
    direct_results = await run_direct_evaluator_demo(direct_material)

    scored = [r for r in direct_results if r.get("groundedness") is not None]
    n_errors = len(direct_results) - len(scored)
    avg_groundedness = (sum(r["groundedness"] for r in scored) / len(scored)) if scored else None
    avg_overall = (sum(r["overall_quality"] for r in scored) / len(scored)) if scored else None
    # Relevance/faithfulness/cost don't depend on the judge panel, so they're always
    # computed (see run_direct_evaluator_demo's docstring) — averaged over every case,
    # not just the judge-scored subset.
    avg_relevance = (sum(r["relevance"] for r in direct_results) / len(direct_results)) if direct_results else None
    avg_faithfulness = (sum(r["faithfulness"] for r in direct_results) / len(direct_results)) if direct_results else None
    avg_latency = (sum(r["latency_ms"] for r in direct_results) / len(direct_results)) if direct_results else None
    costed = [r for r in direct_results if r.get("cost_usd") is not None]
    total_cost_usd = sum(r["cost_usd"] for r in costed) if costed else None
    avg_cost_usd_per_case = (total_cost_usd / len(costed)) if costed else None
    disagreements = [r for r in scored if r.get("judge_disagreement")]
    scope_violations = [r for r in direct_results if r.get("persona_scope_violations")]
    judge_dropout = [r for r in scored if (r.get("judges_used") or 0) < len(rageval_settings.JUDGE_MODELS)]

    summary = {
        "service_evaluated": "omnismart-rageval package capabilities (using real IntelAI production answers)",
        "purpose": (
            "Demonstrates the omnismart-rageval package's own differentiating features "
            "(drop-in decorator, multi-judge consensus with disagreement detection, real "
            "cost/latency tracking, persona-awareness) — not a RAG-quality benchmark. "
            "See eval/RAGEVAL_PRODUCTION_LIVE_REPORT.json for IntelAI's live production "
            "RAG quality at N=50."
        ),
        "package_version_installed": _package_version(),
        "answer_source": f"live production gateway ({GATEWAY}), POST /api/v1/chat/async + poll",
        "judge_models_configured": rageval_settings.JUDGE_MODELS,
        "min_judges_required": MIN_JUDGES_REQUIRED,
        "decorator_demo": decorator_demo,
        "total_cases": len(fetched),
        "direct_evaluator_cases": len(direct_results),
        "direct_evaluator_scored": len(scored),
        "direct_evaluator_judge_unavailable": n_errors,
        "avg_groundedness": round(avg_groundedness, 4) if avg_groundedness is not None else None,
        "avg_overall_quality": round(avg_overall, 4) if avg_overall is not None else None,
        "avg_latency_ms": round(avg_latency) if avg_latency is not None else None,
        "total_cost_usd": round(total_cost_usd, 6) if total_cost_usd is not None else None,
        "avg_cost_usd_per_case": round(avg_cost_usd_per_case, 6) if avg_cost_usd_per_case is not None else None,
        "cases_with_judge_dropout": len(judge_dropout),
        "cases_flagged_judge_disagreement": len(disagreements),
        "cases_flagged_persona_scope_violation": len(scope_violations),
        "results": direct_results,
    }

    out_dir = ROOT_DIR / "eval"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "RAGEVAL_PACKAGE_REPORT.json"
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)

    # Demo store is local, disposable scratch — remove it so re-runs start clean and
    # nothing binary/runtime lands in the repo.
    if _DEMO_DB_PATH.exists():
        _DEMO_DB_PATH.unlink()

    print(f"\n{'='*70}")
    print(f"Decorator demo: {decorator_demo['rows_persisted_after_flush']} interactions logged via @track")
    print(f"Direct evaluator: {len(scored)}/{len(direct_results)} scored, "
          f"{len(disagreements)} flagged JUDGE_DISAGREEMENT, {len(judge_dropout)} with judge dropout")
    print(f"Avg groundedness: {summary['avg_groundedness']}   Avg overall quality: {summary['avg_overall_quality']}")
    print(f"Total cost: ${summary['total_cost_usd']}   Avg cost/case: ${summary['avg_cost_usd_per_case']}")
    print(f"Report written to {out_path}")
    return summary


def run() -> Dict[str, Any]:
    return asyncio.run(run_async())


if __name__ == "__main__":
    run()
