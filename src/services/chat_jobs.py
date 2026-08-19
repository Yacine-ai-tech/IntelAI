"""
Chat job store — durable job tracking for POST /api/v1/chat/async + GET /api/v1/chat/{job_id}.

Same reasoning and pattern as DocIntel's services/batch_processor.py: a real chat turn
under cold retrieval (see BENCHMARK.md) can take 60-100s+, long enough that a reverse
proxy in front of this service (Cloudflare, in production) can cut the connection
before an otherwise-successful synchronous response comes back. Returning a job_id
immediately and polling in short, fast requests means no single request can ever run
long enough to hit that ceiling.

Postgres-backed (not in-memory) so a job survives this process restarting mid-run —
this app is a single free-tier instance that does restart (deploys, OOM, host
recycling), and an in-memory-only job store would silently drop every in-flight job
on any of those, leaving a polling client with "unknown job" and no explanation.

Unlike DocIntel's batch processor, this has no fan-out/concurrency to manage — one job
is exactly one chat turn, not N files — so it's deliberately smaller: no semaphore, no
per-item result list, just pending -> running -> done|error on a single row.
"""
from __future__ import annotations

import json
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional

log = logging.getLogger(__name__)

# How long a finished job's result stays retrievable after it last changed. Default
# 1h — long enough for a slow-to-poll client, short enough that this doesn't become
# its own unbounded-growth problem in the DB.
JOB_TTL_SECONDS = 3600

# How long a job may sit in 'running' with no update before it's treated as orphaned.
# run_job() executes via FastAPI's BackgroundTasks on the SAME worker process that
# handled the original POST /chat/async request — if that process restarts mid-run
# (a real risk on this single free-tier instance: deploys, OOM, host recycling, all
# explicitly called out in this module's own docstring above), nothing is left to
# ever write 'done' or 'error' for that job, and a polling client sees 'running'
# forever. Confirmed live: a real job sat in 'running' for 650+s (see BENCHMARK.md
# §5) with no sign of progress, well past the 50-150s real chat turns actually take.
# Set well above that real-world ceiling so a merely slow turn is never mistaken for
# an orphan.
STALE_RUNNING_SECONDS = 600


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _evict_expired(conn) -> None:
    """Best-effort, lazy eviction — checked on every new_job() call rather than a
    dedicated background loop, matching batch_processor.py's own approach."""
    try:
        conn.execute(
            "DELETE FROM chat_jobs WHERE updated_at < NOW() - make_interval(secs => %s)",
            (JOB_TTL_SECONDS,),
        )
        conn.commit()
    except Exception as e:
        log.debug("chat_jobs eviction skipped (non-fatal): %s", e)


def new_job(request: Dict[str, Any], owner_user_id: Optional[str] = None) -> str:
    from src.services.pg_store import _get_conn
    job_id = str(uuid.uuid4())
    conn = _get_conn()
    try:
        _evict_expired(conn)
        conn.execute(
            "INSERT INTO chat_jobs (id, status, request, owner_user_id) VALUES (%s, 'pending', %s, %s)",
            (job_id, json.dumps(request), owner_user_id),
        )
        conn.commit()
    finally:
        conn.close()
    return job_id


async def run_job(job_id: str, fn: Callable[[], Any]) -> None:
    """Runs `fn` (the actual chat call — an async callable, awaited here) and persists
    the outcome. Passed to FastAPI's BackgroundTasks.add_task, which awaits it after
    the HTTP response for POST /chat/async has already gone out — that's the entire
    point: the request that created the job never waits on this."""
    from src.services.pg_store import _get_conn
    conn = _get_conn()
    try:
        conn.execute("UPDATE chat_jobs SET status='running', updated_at=NOW() WHERE id=%s", (job_id,))
        conn.commit()
    finally:
        conn.close()

    t0 = time.monotonic()
    try:
        result = await fn()
        conn = _get_conn()
        try:
            conn.execute(
                "UPDATE chat_jobs SET status='done', result=%s, updated_at=NOW() WHERE id=%s",
                (json.dumps(result), job_id),
            )
            conn.commit()
        finally:
            conn.close()
    except Exception as e:
        log.error("chat job %s failed after %.1fs: %s", job_id, time.monotonic() - t0, e)
        conn = _get_conn()
        try:
            conn.execute(
                "UPDATE chat_jobs SET status='error', error=%s, updated_at=NOW() WHERE id=%s",
                (str(e)[:2000], job_id),
            )
            conn.commit()
        finally:
            conn.close()


def _reap_if_stale(conn, job_id: str) -> None:
    """Flip an orphaned 'running' job to 'error', lazily, on poll — same lazy-check
    style as _evict_expired() above rather than a dedicated background loop. Scoped
    to status='running' in the WHERE clause so this is a no-op (and safe to call on
    every poll) once a job has legitimately finished or already been reaped."""
    try:
        conn.execute(
            "UPDATE chat_jobs SET status='error', "
            "error=%s, updated_at=NOW() "
            "WHERE id=%s AND status='running' "
            "AND updated_at < NOW() - make_interval(secs => %s)",
            (
                f"job orphaned: no progress for over {STALE_RUNNING_SECONDS}s — the "
                "worker process handling it most likely restarted mid-run (deploy, "
                "OOM, or host recycling). Retry the request.",
                job_id, STALE_RUNNING_SECONDS,
            ),
        )
        conn.commit()
    except Exception as e:
        log.debug("stale-job reap skipped for %s (non-fatal): %s", job_id, e)


def get_job(job_id: str, owner_user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Returns the job row, or None if it doesn't exist / TTL-expired / owned by
    someone else. Scoping by owner_user_id (when the caller has one) keeps one user's
    chat job from being pollable by another — same privacy reasoning DocIntel's
    session-scoped batch endpoints use.

    Before reading, reaps the job if it's been stuck in 'running' past
    STALE_RUNNING_SECONDS (see that constant) — without this, a client polling an
    orphaned job gets 'running' forever with no way to know its request was lost
    rather than merely slow."""
    from src.services.pg_store import _get_conn
    conn = _get_conn()
    try:
        _reap_if_stale(conn, job_id)
        row = conn.execute(
            "SELECT id, status, result, error, owner_user_id, created_at, updated_at "
            "FROM chat_jobs WHERE id = %s",
            (job_id,),
        ).fetchone()
    finally:
        conn.close()
    if not row:
        return None
    if owner_user_id and row.get("owner_user_id") and row["owner_user_id"] != owner_user_id:
        return None
    return dict(row)
