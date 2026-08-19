"""Unit coverage for chat_jobs.py's stale-job reaper (see BENCHMARK.md §5 — a real
job was observed stuck in 'running' for 650+s live, well past any real chat turn's
50-150s, because run_job() executes via FastAPI BackgroundTasks on the same worker
process that handled the original request: if that process restarts mid-run, nothing
is left to ever mark the job done or errored).

Pure in-memory (no real Postgres): a fake connection records what SQL/params
_reap_if_stale() issues, so this verifies the reaper targets exactly a stuck
'running' row past STALE_RUNNING_SECONDS without needing a live DB.
"""
import pytest

from src.services import chat_jobs


class _FakeConn:
    """Records every execute() call; .commit()/.close() are no-ops."""

    def __init__(self):
        self.calls = []
        self.committed = False

    def execute(self, sql, params=None):
        self.calls.append((sql, params))
        return self  # .fetchone() not needed by _reap_if_stale itself

    def commit(self):
        self.committed = True

    def close(self):
        pass


@pytest.mark.unit
def test_reap_if_stale_issues_scoped_update():
    conn = _FakeConn()
    chat_jobs._reap_if_stale(conn, "job-123")

    assert len(conn.calls) == 1
    sql, params = conn.calls[0]

    # Only ever targets a row that is BOTH still 'running' AND stale — never a
    # job that already finished (done/error), so this is safe to call on every
    # single poll with no risk of clobbering a real result.
    assert "status='running'" in sql
    assert "status='error'" in sql
    assert "updated_at < NOW()" in sql

    # The job id and the staleness threshold are the real bound parameters, not
    # baked into the SQL string (avoids injection and keeps the threshold in one
    # place: STALE_RUNNING_SECONDS).
    assert params[1] == "job-123"
    assert params[2] == chat_jobs.STALE_RUNNING_SECONDS
    assert conn.committed


@pytest.mark.unit
def test_reap_if_stale_never_raises_on_a_broken_connection():
    """A DB hiccup here must never break GET /chat/{job_id} for an otherwise-healthy
    job — same lazy-best-effort contract as _evict_expired() elsewhere in this
    module."""

    class _BrokenConn:
        def execute(self, *a, **k):
            raise RuntimeError("connection lost")

    # Must not raise.
    chat_jobs._reap_if_stale(_BrokenConn(), "job-456")


@pytest.mark.unit
def test_stale_threshold_is_well_above_a_real_chat_turn():
    # BENCHMARK.md's live production eval (§3) measured real chat turns at
    # 50-150s; the reaper threshold must stay well clear of that so a merely
    # slow — not orphaned — turn is never misdiagnosed as stuck.
    assert chat_jobs.STALE_RUNNING_SECONDS >= 300
