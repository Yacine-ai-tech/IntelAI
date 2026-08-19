"""
Admin job store — durable job tracking for POST /api/v1/admin/scenario/async +
GET /api/v1/admin/scenario/{job_id}.

Same pattern as chat_jobs.py (see that module's docstring for the full reasoning):
switching an Admin scenario writes thousands of KPI rows, extracts GraphRAG-lite
entities for each, and generates + embeds knowledge docs — confirmed live to take
80s+, long enough that Cloudflare's proxy in front of production cut the connection
with a 502 even though the operation completed successfully server-side seconds
later. Returning a job_id immediately and polling in short, fast requests means no
single request can ever run long enough to hit that ceiling.

A separate table from chat_jobs (not a shared one) on purpose: different request/
result shapes, different TTL reasoning isn't worth entangling, and this keeps the
already-shipped, working chat job path untouched by this fix.
"""
from __future__ import annotations

import json
import logging
import time
import uuid
from typing import Any, Callable, Dict, Optional

log = logging.getLogger(__name__)

JOB_TTL_SECONDS = 3600

# Same orphan risk as chat_jobs.py (see that module for the full reasoning): run_job()
# executes on the same worker process that handled the original POST /async request —
# if that process restarts mid-run, nothing is left to ever write 'done' or 'error',
# and a polling client sees 'running' forever. Confirmed live: a declining_financial
# scenario-switch job sat in 'running' for 30+ minutes with repeated polling and never
# self-healed, because this module never got the poll-time reaper chat_jobs.py has.
STALE_RUNNING_SECONDS = 600


def _evict_expired(conn) -> None:
    try:
        conn.execute(
            "DELETE FROM admin_jobs WHERE updated_at < NOW() - make_interval(secs => %s)",
            (JOB_TTL_SECONDS,),
        )
        conn.commit()
    except Exception as e:
        log.debug("admin_jobs eviction skipped (non-fatal): %s", e)


def new_job(request: Dict[str, Any], owner_user_id: Optional[str] = None) -> str:
    from src.services.pg_store import _get_conn
    job_id = str(uuid.uuid4())
    conn = _get_conn()
    try:
        _evict_expired(conn)
        conn.execute(
            "INSERT INTO admin_jobs (id, status, request, owner_user_id) VALUES (%s, 'pending', %s, %s)",
            (job_id, json.dumps(request), owner_user_id),
        )
        conn.commit()
    finally:
        conn.close()
    return job_id


def run_job(job_id: str, fn: Callable[[], Dict[str, Any]]) -> None:
    """Runs `fn` (the actual scenario switch — a sync callable, called here) and
    persists the outcome. Passed to FastAPI's BackgroundTasks.add_task, which runs it
    after the HTTP response for POST /admin/scenario/async has already gone out."""
    from src.services.pg_store import _get_conn
    conn = _get_conn()
    try:
        conn.execute("UPDATE admin_jobs SET status='running', updated_at=NOW() WHERE id=%s", (job_id,))
        conn.commit()
    finally:
        conn.close()

    t0 = time.monotonic()
    try:
        result = fn()
        conn = _get_conn()
        try:
            conn.execute(
                "UPDATE admin_jobs SET status='done', result=%s, updated_at=NOW() WHERE id=%s",
                (json.dumps(result), job_id),
            )
            conn.commit()
        finally:
            conn.close()
    except Exception as e:
        log.error("admin job %s failed after %.1fs: %s", job_id, time.monotonic() - t0, e)
        conn = _get_conn()
        try:
            conn.execute(
                "UPDATE admin_jobs SET status='error', error=%s, updated_at=NOW() WHERE id=%s",
                (str(e)[:2000], job_id),
            )
            conn.commit()
        finally:
            conn.close()


def _reap_if_stale(conn, job_id: str) -> None:
    """Flip an orphaned 'running' job to 'error', lazily, on poll — see
    STALE_RUNNING_SECONDS above. Scoped to status='running' so this is a no-op once a
    job has legitimately finished or already been reaped."""
    try:
        conn.execute(
            "UPDATE admin_jobs SET status='error', "
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
    from src.services.pg_store import _get_conn
    conn = _get_conn()
    try:
        _reap_if_stale(conn, job_id)
        row = conn.execute(
            "SELECT id, status, request, result, error, owner_user_id, created_at, updated_at "
            "FROM admin_jobs WHERE id = %s",
            (job_id,),
        ).fetchone()
    finally:
        conn.close()
    if not row:
        return None
    if owner_user_id and row.get("owner_user_id") and row["owner_user_id"] != owner_user_id:
        return None
    return dict(row)
