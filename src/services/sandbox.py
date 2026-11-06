"""Personal data sandbox — scoped, temporary visitor workspaces.

A sandbox is a demo-scoped user (same ``owner_user_id`` contract as demo_login's
``X-Demo-Session-Id`` isolation) wrapped with quotas, a wipe guarantee and a
capability token that can only reach sandbox routes. Global/seeded knowledge
(``owner_user_id IS NULL``) is never touched by sandbox operations.
"""
from __future__ import annotations

import hashlib
import os
import time
import uuid
from typing import Any, Dict, List, Optional

from src.core.logger import get_logger

log = get_logger(__name__)

# Quotas — deliberately modest for the free OSS tier; override via env.
MAX_DOCS = int(os.getenv("SANDBOX_MAX_DOCS", "10"))
MAX_TEXT_BYTES = int(os.getenv("SANDBOX_MAX_TEXT_BYTES", str(25 * 1024 * 1024)))
MAX_MEDIA_BYTES = int(os.getenv("SANDBOX_MAX_MEDIA_BYTES", str(50 * 1024 * 1024)))
MAX_JOB_AGE_S = int(os.getenv("SANDBOX_MAX_JOB_AGE_S", str(90 * 24 * 3600)))
SESSION_TTL_S = int(os.getenv("SANDBOX_SESSION_TTL_S", str(24 * 3600)))
MAX_JOBS_PER_HOUR = int(os.getenv("SANDBOX_MAX_JOBS_PER_HOUR", "20"))

_MEDIA_EXT = {".mp3", ".wav", ".m4a", ".ogg", ".webm", ".flac", ".mp4", ".mov"}
_IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tiff"}
_DOC_EXT = {".pdf", ".docx", ".doc", ".pptx", ".xlsx", ".odt", ".rtf"}
_TEXT_EXT = {".txt", ".md", ".csv", ".json", ".log", ".xml", ".yaml", ".yml", ".tsv"}

_SCHEMA = """
CREATE TABLE IF NOT EXISTS sandbox_sessions (
    id              TEXT PRIMARY KEY,
    owner_user_id   TEXT NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at      TIMESTAMPTZ NOT NULL,
    wiped_at        TIMESTAMPTZ,
    docs_count      INT NOT NULL DEFAULT 0,
    bytes_used      BIGINT NOT NULL DEFAULT 0,
    media_bytes     BIGINT NOT NULL DEFAULT 0,
    ip_hash         TEXT,
    user_agent_hash TEXT
);
CREATE INDEX IF NOT EXISTS sandbox_sessions_expires_idx
    ON sandbox_sessions (expires_at) WHERE wiped_at IS NULL;
CREATE INDEX IF NOT EXISTS sandbox_sessions_owner_idx ON sandbox_sessions (owner_user_id);

CREATE TABLE IF NOT EXISTS sandbox_ingest_jobs (
    id              TEXT PRIMARY KEY,
    session_id      TEXT NOT NULL REFERENCES sandbox_sessions(id) ON DELETE CASCADE,
    filename        TEXT NOT NULL,
    media_type      TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'queued',
    chunks_written  INT NOT NULL DEFAULT 0,
    error           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at     TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS sandbox_ingest_jobs_session_idx ON sandbox_ingest_jobs (session_id);
"""

_ready = False


def _ensure_schema() -> None:
    global _ready
    if _ready:
        return
    from src.services.pg_store import _get_conn
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(_SCHEMA)
        conn.commit()
    finally:
        conn.close()
    _ready = True


def classify_filename(filename: str) -> str:
    """-> 'text' | 'document' | 'audio' | 'image' | 'unsupported'"""
    lower = (filename or "").lower()
    if lower.endswith(tuple(_TEXT_EXT)):
        return "text"
    if lower.endswith(tuple(_MEDIA_EXT)):
        return "audio"
    if lower.endswith(tuple(_IMAGE_EXT)):
        return "image"
    if lower.endswith(tuple(_DOC_EXT)):
        return "document"
    return "unsupported"


def hash_ip(ip: Optional[str]) -> Optional[str]:
    if not ip:
        return None
    salt = os.getenv("SANDBOX_IP_SALT") or settings_secret()
    return hashlib.sha256(f"{salt}:{ip}".encode()).hexdigest()[:16]


def settings_secret() -> str:
    from src.core.config import settings
    return getattr(settings, "SECRET_KEY", "") or "intelai-sandbox"


def create_session(ip: Optional[str] = None, user_agent: Optional[str] = None) -> Dict[str, Any]:
    """Create a sandbox: demo-scoped owner_user_id + registry row + capability JWT."""
    _ensure_schema()
    from src.services.pg_store import get_or_create_demo_user, _get_conn
    from src.core.jwt_auth import TokenData, create_access_token

    sid = f"sbx_{uuid.uuid4().hex[:20]}"
    owner_user_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"intelai-sandbox:{sid}"))
    username = f"sandbox-{sid[-6:]}"
    created = get_or_create_demo_user(owner_user_id, username, "viewer", "Sandbox Visitor")
    owner_user_id = created.get("id", owner_user_id)

    expires_at = time.time() + SESSION_TTL_S
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO sandbox_sessions (id, owner_user_id, expires_at, ip_hash, user_agent_hash)
                   VALUES (%s, %s, to_timestamp(%s), %s, %s)""",
                [sid, owner_user_id, expires_at, hash_ip(ip),
                 hashlib.sha256((user_agent or "")[:200].encode()).hexdigest()[:16] if user_agent else None],
            )
        conn.commit()
    finally:
        conn.close()

    token = create_access_token(TokenData(user_id=owner_user_id, username=username, role="viewer", language="en"))
    return {
        "session_id": sid,
        "owner_user_id": owner_user_id,
        "token": token,
        "token_type": "bearer",
        "expires_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(expires_at)),
        "quota": {"docs": MAX_DOCS, "text_bytes": MAX_TEXT_BYTES, "media_bytes": MAX_MEDIA_BYTES,
                  "jobs_per_hour": MAX_JOBS_PER_HOUR, "retention_days": 90},
    }


def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    _ensure_schema()
    from src.services.pg_store import _get_conn
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT id, owner_user_id, expires_at, wiped_at, docs_count, bytes_used, media_bytes, created_at
                   FROM sandbox_sessions WHERE id = %s""",
                [session_id],
            )
            row = cur.fetchone()
            if not row:
                return None
            cols = ["id", "owner_user_id", "expires_at", "wiped_at", "docs_count", "bytes_used",
                    "media_bytes", "created_at"]
            return dict(zip(cols, row))
    finally:
        conn.close()


def is_wiped_or_expired(session: Dict[str, Any]) -> bool:
    if session.get("wiped_at"):
        return True
    exp = session.get("expires_at")
    if hasattr(exp, "timestamp"):
        return exp.timestamp() < time.time()
    return False


def quota_status(session: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "docs_used": session.get("docs_count") or 0,
        "docs_max": MAX_DOCS,
        "bytes_used": session.get("bytes_used") or 0,
        "bytes_max": MAX_TEXT_BYTES,
        "media_bytes_used": session.get("media_bytes") or 0,
        "media_bytes_max": MAX_MEDIA_BYTES,
    }


def check_quota(session: Dict[str, Any], size_bytes: int, kind: str) -> Optional[str]:
    """Returns an error string or None."""
    q = quota_status(session)
    if q["docs_used"] >= MAX_DOCS:
        return "quota_docs_exceeded"
    if kind in ("audio", "image", "document"):
        if (q["media_bytes_used"] or 0) + size_bytes > MAX_MEDIA_BYTES:
            return "quota_media_bytes_exceeded"
    elif (q["bytes_used"] or 0) + size_bytes > MAX_TEXT_BYTES:
        return "quota_bytes_exceeded"
    return jobs_rate_limited(session["id"])


def jobs_rate_limited(session_id: str) -> Optional[str]:
    _ensure_schema()
    from src.services.pg_store import _get_conn
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT COUNT(*) FROM sandbox_ingest_jobs
                   WHERE session_id = %s AND created_at > now() - interval '1 hour'""",
                [session_id],
            )
            if (cur.fetchone() or [0])[0] >= MAX_JOBS_PER_HOUR:
                return "rate_limited"
    finally:
        conn.close()
    return None


def create_job(session_id: str, filename: str, media_type: str) -> str:
    _ensure_schema()
    job_id = f"sbj_{uuid.uuid4().hex[:20]}"
    from src.services.pg_store import _get_conn
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO sandbox_ingest_jobs (id, session_id, filename, media_type)
                   VALUES (%s, %s, %s, %s)""",
                [job_id, session_id, filename, media_type],
            )
        conn.commit()
    finally:
        conn.close()
    return job_id


def finish_job(job_id: str, status: str, chunks: int = 0, error: Optional[str] = None) -> None:
    _ensure_schema()
    from src.services.pg_store import _get_conn
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """UPDATE sandbox_ingest_jobs SET status=%s, chunks_written=%s, error=%s, finished_at=now()
                   WHERE id=%s""",
                [status, chunks, error, job_id],
            )
        conn.commit()
    finally:
        conn.close()


def get_job(job_id: str, session_id: str) -> Optional[Dict[str, Any]]:
    _ensure_schema()
    from src.services.pg_store import _get_conn
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT id, session_id, filename, media_type, status, chunks_written, error, created_at, finished_at
                   FROM sandbox_ingest_jobs WHERE id = %s AND session_id = %s""",
                [job_id, session_id],
            )
            row = cur.fetchone()
            if not row:
                return None
            cols = ["id", "session_id", "filename", "media_type", "status", "chunks_written",
                    "error", "created_at", "finished_at"]
            return dict(zip(cols, row))
    finally:
        conn.close()


def bump_usage(session_id: str, docs: int = 0, text_bytes: int = 0, media_bytes: int = 0) -> None:
    _ensure_schema()
    from src.services.pg_store import _get_conn
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """UPDATE sandbox_sessions
                   SET docs_count = docs_count + %s, bytes_used = bytes_used + %s, media_bytes = media_bytes + %s
                   WHERE id = %s""",
                [docs, text_bytes, media_bytes, session_id],
            )
        conn.commit()
    finally:
        conn.close()


def list_docs(owner_user_id: str) -> List[Dict[str, Any]]:
    from src.services.pg_store import _get_conn
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT doc_id, title, source, language, created_at, length(content) AS chars
                   FROM knowledge_base WHERE owner_user_id = %s ORDER BY created_at DESC""",
                [owner_user_id],
            )
            cols = ["doc_id", "title", "source", "language", "created_at", "chars"]
            return [dict(zip(cols, r)) for r in cur.fetchall()]
    finally:
        conn.close()


def wipe_session(session: Dict[str, Any]) -> Dict[str, int]:
    """Delete everything the sandbox owns: knowledge rows, Qdrant points, blobs.
    Idempotent — safe to call twice."""
    _ensure_schema()
    owner = session["owner_user_id"]
    sid = session["id"]

    # 1. Collect doc_ids for vector cleanup BEFORE deleting rows.
    from src.services.pg_store import _get_conn
    conn = _get_conn()
    doc_ids: List[str] = []
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT doc_id FROM knowledge_base WHERE owner_user_id = %s", [owner])
            doc_ids = [r[0] for r in cur.fetchall()]
            # 2. Delete knowledge rows + job/file bookkeeping.
            cur.execute("DELETE FROM knowledge_base WHERE owner_user_id = %s", [owner])
            cur.execute("DELETE FROM sandbox_ingest_jobs WHERE session_id = %s", [sid])
            cur.execute("UPDATE sandbox_sessions SET wiped_at = now() WHERE id = %s", [sid])
        conn.commit()
    finally:
        conn.close()

    # 3. Qdrant payload-filter delete (best-effort — the payload field is stamped
    #    at ingest time; doc_ids also map to point ids where the store uses them).
    vectors_deleted = 0
    try:
        from src.services.vector_store import get_vector_store
        vs = get_vector_store()
        deleter = getattr(vs, "delete_by_doc_ids", None) or getattr(vs, "delete", None)
        if deleter and doc_ids:
            try:
                deleter(doc_ids)
            except TypeError:
                for d in doc_ids:
                    try:
                        deleter([d])
                    except Exception:
                        pass
            vectors_deleted = len(doc_ids)
    except Exception as e:
        log.warning("sandbox wipe: vector cleanup failed (rows already gone): %s", e)

    log.info("sandbox wiped session=%s docs=%d", sid, len(doc_ids))
    return {"docs_deleted": len(doc_ids), "vectors_deleted": vectors_deleted}


def sweep_expired() -> int:
    """Hourly: wipe sessions past expiry+grace or older than MAX_JOB_AGE_S."""
    _ensure_schema()
    from src.services.pg_store import _get_conn
    conn = _get_conn()
    sids: List[str] = []
    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT id FROM sandbox_sessions
                   WHERE wiped_at IS NULL AND (expires_at < now() - interval '1 day'
                        OR created_at < now() - make_interval(secs => %s))""",
                [MAX_JOB_AGE_S],
            )
            sids = [r[0] for r in cur.fetchall()]
    finally:
        conn.close()
    wiped = 0
    for sid in sids:
        s = get_session(sid)
        if s:
            try:
                wipe_session(s)
                wiped += 1
            except Exception as e:
                log.warning("sandbox sweep failed for %s: %s", sid, e)
    return wiped
