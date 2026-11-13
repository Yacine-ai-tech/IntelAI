"""
IntelAI API v1 — FastAPI server with JWT auth, RBAC, multi-domain intelligence.

Persona-aware AI analytics & RAG copilot. Domains: Finance, HR, Logistics, IT,
Operations, ESG, Growth/Risk.
"""
from __future__ import annotations

import asyncio
import hmac
import os
import uuid
import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import pandas as pd
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, WebSocket, WebSocketDisconnect, Query, Request, BackgroundTasks, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from src.core.logger import get_logger
from src.core.jwt_auth import (
    TokenData, LoginRequest, RegisterRequest,
    hash_password, verify_password,
    create_access_token, get_current_user, require_role, require_page, get_user_data_categories, get_user_pages,
    ROLE_DEFINITIONS, DEFAULT_USERS,
)
from src.core.config import get_cors_allowed_origins, settings


log = get_logger(__name__)


def _env_number(name: str, default, cast=float):
    """Numeric environment value; unset, blank or malformed values use the default."""
    raw = (_os.environ.get(name) or "").strip()
    if not raw:
        return default
    try:
        return cast(raw)
    except (TypeError, ValueError):
        return default


def _chat_turn_timeout_seconds() -> float:
    return max(1.0, _env_number("CHAT_TURN_TIMEOUT", 180.0))


def _requires_persistent_database(environment: str, vector_store: str) -> bool:
    return environment.lower() == "production" or vector_store.lower() in {"qdrant", "pgvector"}

# ════════════════════════════════════════════════════════════
# APP INITIALIZATION
# ════════════════════════════════════════════════════════════

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup()
    yield

app = FastAPI(
    title="IntelAI API",
    description="Persona-Aware AI Analytics & RAG Copilot — Multi-Domain KPI Intelligence",
    version="2026.3.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)


import threading
import requests
import os
import time
import uuid


def _telemetry_instance_id() -> str:
    """
    A random, locally-generated install ID — NOT derived from MAC address or any other
    hardware fingerprint. Persisted under LOGS_DIR so repeat startups of the same install
    report the same ID (for dedup on the receiving end); delete the file to reset it.
    See README.md's Anonymous Telemetry section for why this is a random UUID rather than a hardware-derived value.
    """
    id_file = os.path.join(str(settings.LOGS_DIR), ".telemetry_instance_id")
    try:
        if os.path.exists(id_file):
            existing = open(id_file).read().strip()
            if existing:
                return existing
    except Exception:
        pass
    new_id = uuid.uuid4().hex[:16]
    try:
        with open(id_file, "w") as f:
            f.write(new_id)
    except Exception:
        pass
    return new_id


DEFAULT_TELEMETRY_URL = "https://gateway.ysiddo-ai-projects.app/telemetry"


def _send_telemetry():
    """
    One anonymous startup ping per ~6h to TELEMETRY_URL to count distinct installations
    and track active usage. Sends only {service, event, version, instance_id} — no request
    data, document/KPI content, or credentials. Fully controllable: disable entirely
    with TELEMETRY_OPT_OUT=true or DO_NOT_TRACK=1, or point TELEMETRY_URL at your own collector.
    """
    if os.environ.get("TELEMETRY_OPT_OUT", "").strip().lower() in ("true", "1", "yes") or os.environ.get("DO_NOT_TRACK", "").strip() == "1":
        return

    telemetry_url = (os.environ.get("TELEMETRY_URL") or DEFAULT_TELEMETRY_URL).strip()
    if not telemetry_url:
        return

    lock_file = os.path.join(str(settings.LOGS_DIR), ".telemetry_last_ping")
    try:
        if os.path.exists(lock_file) and time.time() - os.path.getmtime(lock_file) < 30:
            return
        with open(lock_file, "w") as f:
            f.write(str(time.time()))
    except Exception:
        pass

    payload = {
        "service": "IntelAI",
        "event": "startup",
        "version": "2026.3.0",
        "instance_id": _telemetry_instance_id(),
    }
    for attempt in range(3):
        try:
            requests.post(telemetry_url, json=payload, timeout=3)
            break
        except Exception:
            time.sleep(2 * (attempt + 1))


def _license_beacon():
    """Opt-out-able license/install ping — counts real self-hosted deployments.
    LICENSE_BEACON_URL overrides the endpoint; LICENSE_BEACON_DISABLE=true opts out."""
    beacon_url = os.environ.get("LICENSE_BEACON_URL", "https://gateway.ysiddo-ai-projects.app/license/verify").strip()
    if not beacon_url or os.environ.get("LICENSE_BEACON_DISABLE", "").lower() in ("1", "true", "yes"):
        return
    try:
        import json, urllib.request
        payload = json.dumps({
            "project": os.environ.get("LICENSE_BEACON_PROJECT", "intelai"),
            "instance_id": _telemetry_instance_id(),
            "license_key": os.environ.get("LICENSE_KEY", ""),
            "version": os.environ.get("APP_VERSION", ""),
        }).encode()
        req = urllib.request.Request(beacon_url, data=payload,
                                     headers={"Content-Type": "application/json"}, method="POST")
        urllib.request.urlopen(req, timeout=5).read()
    except Exception:
        pass

threading.Thread(target=_send_telemetry, daemon=True).start()
threading.Thread(target=_license_beacon, daemon=True).start()
# -------------------------


from fastapi import Request
from fastapi.responses import JSONResponse
import os as _os

@app.middleware("http")
async def verify_internal_token(request: Request, call_next):
    # Allow health checks, public auth routes, and the public HMAC-signed
    # ingestion webhook (/api/v1/webhook/{source_name}) — its own signature
    # check IS its auth. Gating it behind X-IntelAI-Internal-Token too would
    # defeat the entire point of a machine-to-machine endpoint: no external
    # pusher (StreamPulse, a Kafka HTTP sink connector, n8n) can practically
    # obtain an IntelAI-internal secret, only the shared HMAC secret they were
    # actually given for this integration.
    if (request.url.path in ["/health", "/live", "/ready", "/api/health", "/docs", "/api/docs", "/openapi.json", "/api/openapi.json", "/redoc", "/api/redoc"]
            or request.url.path.startswith("/api/v1/auth/")
            or request.url.path.startswith("/api/v1/webhook/")
            or (request.method == "POST" and request.url.path == "/api/v1/sandbox/session")):
        return await call_next(request)

    token = (
        request.headers.get("X-IntelAI-Internal-Token")
        or request.headers.get("X-Internal-Token")
        or request.headers.get("X-OmniIntel-Internal-Token")
        or (request.headers.get("Authorization", "").replace("Bearer ", "") if request.headers.get("Authorization", "").startswith("Bearer ") else "")
    )
    expected_tokens = [
        t for t in (
            _os.environ.get("INTELAI_INTERNAL_TOKEN"),
            _os.environ.get("INTERNAL_TOKEN"),
            _os.environ.get("OMNIINTEL_INTERNAL_TOKEN"),
        ) if t
    ]

    if expected_tokens and _os.environ.get("REQUIRE_INTERNAL_TOKEN", "true").lower() == "true":
        # A Bearer JWT that decodes as a real user token is NOT an internal-token
        # credential — but it IS valid auth for every user-facing route, which
        # enforces its own Depends(get_current_user)/require_role downstream.
        # Gating those routes behind the internal secret broke all browser API
        # calls (user JWT != internal token). Service-to-service callers never
        # send user JWTs, so they still hit the internal-token check below.
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            try:
                from src.core.jwt_auth import decode_access_token
                decode_access_token(auth[len("Bearer "):])
                return await call_next(request)
            except Exception:
                pass
        if not token or not any(token == exp for exp in expected_tokens):
            return JSONResponse(status_code=403, content={"detail": "Missing or invalid X-IntelAI-Internal-Token"})

    return await call_next(request)


@app.middleware("http")
async def demo_scope_middleware(request: Request, call_next):
    """Decodes the caller's JWT (if any) up front so pg_store's KPI reads/writes can scope
    to the current visitor without every one of their ~30 call sites needing a parameter.
    Anonymous demo isolation, not production auth — see get_or_create_demo_user / demo_login."""
    from src.services.pg_store import set_request_scope_user
    scope_user = None
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        try:
            from src.core.jwt_auth import decode_access_token
            token_data = decode_access_token(auth_header[len("Bearer "):])
            scope_user = token_data.user_id
        except Exception:
            scope_user = None
    # NOT asyncio.to_thread: this is a trivial in-memory contextvars.ContextVar.set(),
    # no blocking I/O to offload. to_thread runs the target in a COPY of the current
    # context (contextvars.copy_context().run(...)), so a set() made inside it is
    # thrown away with that copy — every later get_request_scope_user() in THIS
    # request's real context silently saw the ContextVar's default (None), not the
    # user just decoded from the JWT. That silently broke demo-session data scoping
    # on every request: KPI reads fell back to "owner_user_id IS NULL" only, so a
    # visitor's own ingested rows never matched their own scope filter.
    set_request_scope_user(scope_user)
    return await call_next(request)


app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Serve static files (logo, etc.)
import os as _os
_static_dir = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.dirname(__file__))), "static")
if _os.path.isdir(_static_dir):
    app.mount("/static", StaticFiles(directory=_static_dir), name="static")

try:
    _assets_dir = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.dirname(__file__))), "frontend", "dist", "assets")
    if _os.path.exists(_assets_dir):
        app.mount("/assets", StaticFiles(directory=_assets_dir), name="assets")
except Exception as e:
    import logging
    logging.warning("assets mount failed: %s", e)

@app.get("/", include_in_schema=False)
async def serve_spa():
    import os
    spa = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "dist", "index.html")
    if os.path.exists(spa):
        from fastapi.responses import FileResponse
        return FileResponse(spa)
    return {"status": "ok", "service": "intelai"}

# ════════════════════════════════════════════════════════════
# REQUEST / RESPONSE MODELS
# ════════════════════════════════════════════════════════════

class ChatRequest(BaseModel):
    message: str
    persona: Optional[str] = None
    session_id: Optional[str] = None
    context: Optional[str] = ""
    language: Optional[str] = None
    sandbox_only: bool = False  # restrict retrieval to the caller's own docs (no global corpus)

class ChatResponse(BaseModel):
    response: str
    persona_used: str
    persona_display: str = ""
    tokens_used: int = 0
    latency_ms: int = 0
    session_id: str = ""
    blocks: List[Dict[str, Any]] = []


def _structure_answer(text: str) -> List[Dict[str, Any]]:
    """Parse a Markdown-flavoured LLM response into typed answer-blocks.

    Each block is a dict with at least ``{"type": ..., "content": ...}``.
    Supported types:
    - ``heading``   — ``# …`` / ``## …`` / ``### …``
    - ``list``      — ``- …`` / ``* …`` / ``1. …`` lines; ``items`` key holds the list
    - ``kpi``       — ``**Label:** value`` lines (KPI pill pattern)
    - ``quote``     — ``> …`` blockquotes
    - ``code``      — fenced ``` blocks
    - ``table``     — GFM ``| a | b |`` pipe tables; ``rows`` key holds ``[[cell, ...], ...]``
    - ``text``      — everything else

    Tables are emitted as ``table`` blocks: ``FormattedContent`` prefers these
    server-sent ``blocks[]`` when present, so a GFM pipe table has to be structured
    here to render as a table instead of literal pipe syntax.
    """
    import re as _re
    lines = (text or "").replace("\r\n", "\n").split("\n")
    blocks: List[Dict[str, Any]] = []
    buf: List[str] = []
    in_code = False
    code_buf: List[str] = []
    list_buf: List[str] = []
    list_ordered = False

    def _is_table_row(s: str) -> bool:
        return bool(_re.match(r"^\|.*\|$", s))

    def _is_table_separator(s: str) -> bool:
        return bool(_re.match(r"^\|[\s:|-]+\|$", s))

    def flush_text():
        t = " ".join(buf).strip()
        if t:
            blocks.append({"type": "text", "content": t})
        buf.clear()

    def flush_list():
        if list_buf:
            blocks.append({"type": "list", "ordered": list_ordered, "items": list(list_buf)})
            list_buf.clear()

    table_buf: List[str] = []

    def flush_table():
        if not table_buf:
            return
        rows = [r for r in table_buf if not _is_table_separator(r)]
        parsed = [
            [c.strip() for c in _re.sub(r"^\||\|$", "", r).split("|")]
            for r in rows
        ]
        if parsed:
            blocks.append({"type": "table", "rows": parsed})
        table_buf.clear()

    for line in lines:
        stripped = line.strip()

        # GFM pipe table: consume consecutive `|...|` rows (header, separator, body rows)
        # as one block, same shape the frontend's own client-side parser already produces
        # (ChatPage.jsx::parseBlocks) so both code paths render an actual <table>.
        if _is_table_row(stripped) and not in_code:
            flush_list()
            flush_text()
            table_buf.append(stripped)
            continue
        elif table_buf:
            flush_table()

        # Fenced code block toggle
        if stripped.startswith("```"):
            if in_code:
                flush_list()
                flush_text()
                blocks.append({"type": "code", "content": "\n".join(code_buf)})
                code_buf.clear()
                in_code = False
            else:
                flush_list()
                flush_text()
                in_code = True
            continue
        if in_code:
            code_buf.append(line)
            continue

        # Heading
        h = _re.match(r"^(#{1,3})\s+(.*)", stripped)
        if h:
            flush_list()
            flush_text()
            level = len(h.group(1))
            blocks.append({"type": "heading", "level": level, "content": h.group(2)})
            continue

        # Blockquote
        if stripped.startswith("> "):
            flush_list()
            flush_text()
            blocks.append({"type": "quote", "content": stripped[2:]})
            continue

        # KPI pill: **Label:** value  or  **Label**: value
        kpi = _re.match(r"^\*\*([^*]+)\*\*:?\s*(.+)$", stripped)
        if kpi and not stripped.startswith("- ") and not stripped.startswith("* "):
            flush_list()
            flush_text()
            blocks.append({"type": "kpi", "label": kpi.group(1).strip(":. "), "value": kpi.group(2).strip()})
            continue

        # Unordered list item
        ul = _re.match(r"^[-*•]\s+(.*)", stripped)
        if ul:
            flush_text()
            if list_buf and list_ordered:
                flush_list()
            list_ordered = False
            list_buf.append(ul.group(1))
            continue

        # Ordered list item
        ol = _re.match(r"^\d+[.):]\s+(.*)", stripped)
        if ol:
            flush_text()
            if list_buf and not list_ordered:
                flush_list()
            list_ordered = True
            list_buf.append(ol.group(1))
            continue

        # Blank line → flush both lists and accumulate paragraph text
        if not stripped:
            flush_list()
            flush_text()
            continue

        flush_list()
        buf.append(stripped)

    flush_table()
    flush_list()
    flush_text()
    if code_buf:
        blocks.append({"type": "code", "content": "\n".join(code_buf)})

    return blocks

class IngestMetricsRequest(BaseModel):
    data: List[Dict[str, Any]]
    source_name: str = "api"
    replace: bool = True

class WebhookPayload(BaseModel):
    source: str
    schema_type: str
    data: Any

class FinancialRequest(BaseModel):
    company_id: Optional[str] = None
    period: Optional[str] = None
    statement_type: str = "income_statement"

class AgentToolRequest(BaseModel):
    tool: str
    persona: Optional[str] = None
    args: Optional[Dict[str, Any]] = None

class ScenarioRequest(BaseModel):
    scenario: str

class UserUpdateRequest(BaseModel):
    role: Optional[str] = None
    is_active: Optional[bool] = None
    preferred_language: Optional[str] = None


# ════════════════════════════════════════════════════════════
# IN-MEMORY USER STORE (no PostgreSQL dependency)
# ════════════════════════════════════════════════════════════

_users_db: Dict[str, Dict[str, Any]] = {}


def _pg_users_enabled() -> bool:
    """Postgres is the authoritative user store whenever POSTGRES_URL is configured;
    _users_db then serves only as a fallback for no-database deployments and as a
    read cache. Without this split, admin role changes and registrations written to
    Postgres were invisible to login (which read only the in-memory dict) and vice
    versa."""
    return bool((getattr(settings, "POSTGRES_URL", "") or "").strip())


_PG_USERS_DOWN_UNTIL = 0.0
_PG_USERS_BACKOFF_S = 60.0


def _pg_users_healthy() -> bool:
    """Circuit breaker: after a failed PG user lookup, skip Postgres for a short
    window instead of paying its connect-retry latency on every login attempt."""
    return time.time() >= _PG_USERS_DOWN_UNTIL


def _note_pg_users_failure() -> None:
    global _PG_USERS_DOWN_UNTIL
    _PG_USERS_DOWN_UNTIL = time.time() + _PG_USERS_BACKOFF_S


async def _lookup_user_record(username: str) -> Optional[Dict[str, Any]]:
    if _pg_users_enabled() and _pg_users_healthy():
        try:
            from src.services.pg_store import get_user
            row = await asyncio.to_thread(get_user, username)
            if row:
                return row
        except Exception as e:
            _note_pg_users_failure()
            log.warning("PG user lookup failed for %s (falling back to cache): %s", username, e)
    return _users_db.get(username)


async def _user_exists(username: str) -> bool:
    if _pg_users_enabled() and _pg_users_healthy():
        try:
            from src.services.pg_store import user_exists
            return bool(await asyncio.to_thread(user_exists, username))
        except Exception as e:
            _note_pg_users_failure()
            log.warning("PG user_exists failed for %s (falling back to cache): %s", username, e)
    return username in _users_db


def _json_safe(value: Any) -> Any:
    """Recursively convert NaN/Inf values to None for JSON compatibility."""
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_safe(v) for v in value]
    return value


def _init_default_users():
    """Seed default users into PostgreSQL store."""
    global _users_db
    if not DEFAULT_USERS:
        log.warning("No default users configured. Use /api/v1/auth/register for first account or set BOOTSTRAP_ADMIN_* env vars.")
        return
    try:
        from src.services.pg_store import get_user, create_user, update_user
        for username, info in DEFAULT_USERS.items():
            existing = get_user(username)
            if not existing:
                create_user(username, hash_password(info["password"]), info["role"])
            else:
                # Sync password + role to the configured value so the documented credentials
                # always work (create-if-absent alone would keep a stale password). Update the
                # in-memory copy directly to avoid a second (cross-region) DB round-trip.
                try:
                    new_hash = hash_password(info["password"])
                    update_user(existing["id"], password_hash=new_hash, role=info["role"])
                    existing = {**existing, "password_hash": new_hash, "role": info["role"]}
                except Exception as e:
                    log.warning("could not sync default user %s: %s", username, e)
            # Also keep in-memory for fast lookups
            if existing:
                _users_db[username] = existing
            else:
                _users_db[username] = get_user(username) or {
                    "id": str(uuid.uuid4()),
                    "username": username,
                    "password_hash": hash_password(info["password"]),
                    "role": info["role"],
                    "is_active": True,
                    "preferred_language": "en",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
        log.info("Initialized %d default users (PostgreSQL + cache)", len(_users_db))
    except Exception as e:
        log.warning("PostgreSQL unavailable, falling back to in-memory: %s", e)
        for username, info in DEFAULT_USERS.items():
            if username not in _users_db:
                _users_db[username] = {
                    "id": str(uuid.uuid4()),
                    "username": username,
                    "password_hash": hash_password(info["password"]),
                    "role": info["role"],
                    "is_active": True,
                    "preferred_language": "en",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
        log.info("Initialized %d default users (in-memory fallback)", len(_users_db))


# ════════════════════════════════════════════════════════════
# STARTUP
# ════════════════════════════════════════════════════════════

async def startup():
    """Validate required keys, initialize database, seed default data, start cleanup tasks."""
    log.info("IntelAI API starting...")

    # Fail fast — required API keys must be present
    from src.core.config import validate_required_keys
    validate_required_keys()

    # Warm up LiteLLM modules eagerly on the main thread to prevent thread import lock deadlocks
    try:
        import litellm
        litellm.suppress_debug_info = True
        litellm.set_verbose = False
        from litellm import completion, acompletion  # noqa: F401
        try:
            import litellm.types.secret_managers.main  # noqa: F401
        except Exception:
            pass
        log.info("✅ LiteLLM pre-warmed successfully")
    except Exception as e:
        log.warning("LiteLLM pre-warm notice: %s", e)

    # Initialize PostgreSQL (users, chat sessions, monitoring)
    try:
        from src.services.pg_store import init_pg_tables
        await asyncio.to_thread(init_pg_tables)
        log.info("✅ PostgreSQL initialized")
    except Exception as e:
        if _requires_persistent_database(settings.ENVIRONMENT, settings.VECTOR_STORE):
            log.exception("Required PostgreSQL bootstrap or migration failed")
            raise RuntimeError("Required PostgreSQL bootstrap or migration failed") from e
        log.warning("⚠️ PostgreSQL init failed (will use in-memory fallback): %s", e)

    # Seed default users
    _init_default_users()

    # Seed multi-domain data if empty
    try:
        from src.services.pg_store import get_kpi_metrics, seed_all_domains
        df = await asyncio.to_thread(get_kpi_metrics)
        if df.empty:
            count = await asyncio.to_thread(seed_all_domains)
            log.info("✅ Seeded %d multi-domain KPI rows", count)
        else:
            log.info("✅ KPI data already present: %d rows", len(df))
    except Exception as e:
        log.warning("Data seeding skipped: %s", e)

    # Self-heal the persistent vector store WITHOUT blocking startup: embedding-model load +
    # (re)indexing are heavy, so run them in a background thread. The API serves /health, login,
    # dashboards and chat immediately; knowledge search lights up once the index finishes. This
    # keeps large deps/models from blocking the UI/UX.
    def _vector_selfheal():
        try:
            from src.services.vector_store import get_vector_store, reindex
            vs = get_vector_store()
            if vs is None:
                return
            try:
                cnt = vs.count()
            except Exception:
                cnt = 0
            if cnt == 0:
                log.info("Vector store empty — background reindex: %d docs", reindex())
            else:
                try:
                    vs.query("healthcheck probe", n=1)
                    log.info("✅ Vector store populated: %d docs", cnt)
                except Exception as e:
                    if "dimension" in str(e).lower():
                        log.info("Vector store dim mismatch — background rebuild: %d docs", reindex(force=True))
                    else:
                        log.warning("Vector store probe error: %s", e)
        except Exception as e:
            log.error("Required vector-store self-heal failed: %s", e)

    import asyncio as _asyncio
    _asyncio.create_task(_asyncio.to_thread(_vector_selfheal))
    log.info("Vector store self-heal scheduled (background)")

    async def _sandbox_sweeper():
        """Hourly: wipe sandbox sessions past expiry+grace or the 90-day hard cap."""
        from src.services import sandbox as sbx
        while True:
            await _asyncio.sleep(3600)
            try:
                wiped = await _asyncio.to_thread(sbx.sweep_expired)
                if wiped:
                    log.info("Sandbox sweeper wiped %d expired session(s)", wiped)
            except Exception as e:
                log.warning("Sandbox sweeper failed: %s", e)

    _asyncio.create_task(_sandbox_sweeper())
    log.info("Sandbox sweeper scheduled (hourly)")

    # In memory mode, warm the in-process dense+sparse index. With Qdrant configured,
    # retrieval must use its persistent dense index and must not construct a duplicate
    # document-vector index in this process.
    def _rag_prewarm():
        try:
            from src.core.config import settings
            if settings.VECTOR_STORE == "qdrant" and os.getenv("USE_RERANKER", "true").strip().lower() not in (
                "1", "true", "yes", "on"
            ):
                # Reranking is off: warm the embedder, the lexical index and the store
                # connection with one real query so the first request is not the slow one.
                from src.services.vector_store import vector_store_retrieve
                vector_store_retrieve("startup retrieval warmup", 1)
                _RETRIEVAL_WARM.set()
                log.info("Persistent Qdrant retrieval (dense + BM25/RRF) pre-warmed")
                return
            if settings.VECTOR_STORE == "qdrant":
                from src.services.hybrid_retrieval import rerank
                import time as _time
                probe_ok = False
                for _attempt in range(1, 4):
                    if rerank("startup retrieval readiness probe", ["readiness probe"]):
                        probe_ok = True
                        break
                    log.warning("Reranker readiness probe attempt %d/3 failed; retrying", _attempt)
                    _time.sleep(5 * _attempt)
                if not probe_ok:
                    raise RuntimeError("Local BGE reranker failed its readiness probe")
                log.info("Persistent Qdrant retrieval and local BGE reranker pre-warmed")
                return
            from src.services.omnismart_chatbot import _get_shared_rag
            _get_shared_rag()
            from src.services import hybrid_retrieval as retrieval
            if not retrieval.hybrid_enabled():
                log.warning("Hybrid retrieval disabled; local RAG pipeline was not warmed")
                return
            from src.services.pg_store import get_knowledge_docs
            docs = get_knowledge_docs()
            records = list(zip(
                docs["title"].tolist(),
                docs["content"].fillna("").tolist(),
            )) if not docs.empty else []
            if not records:
                log.warning("No knowledge documents available to warm local RAG")
                return
            hits = retrieval.hybrid_doc_retrieve("startup retrieval warmup", records, top_k=1)
            if (
                not hits
                or retrieval._HYBRID is None
                or retrieval._HYBRID._chunk_vecs is None
                or retrieval._HYBRID._bm25 is None
            ):
                raise RuntimeError("Local BGE-M3, BM25, or RRF retrieval did not initialize")
            if (
                os.getenv("USE_RERANKER", "true").strip().lower() in ("1", "true", "yes", "on")
                and os.getenv("RERANK_PROVIDER", "local").strip().lower() == "local"
                and (
                    retrieval._RERANK_RETRIEVER is None
                    or retrieval._RERANK_RETRIEVER._reranker is None
                )
            ):
                raise RuntimeError("Local BGE reranker did not initialize")
            log.info("✅ Local BGE-M3 + BM25/RRF + BGE reranker pipeline pre-warmed")
        except Exception as e:
            log.warning("Chat retrieval pre-warm skipped: %s", e)

    _asyncio.create_task(_asyncio.to_thread(_rag_prewarm))
    log.info("Chat retrieval pre-warm scheduled (background)")

    log.info("✅ IntelAI API ready")


# ════════════════════════════════════════════════════════════
# HEALTH & STATUS
# ════════════════════════════════════════════════════════════

def _health_db_check() -> str:
    try:
        from src.services.pg_store import _get_conn
        conn = _get_conn()
        try:
            conn.execute("SELECT 1")
            return "ok"
        finally:
            conn.close()
    except Exception as e:
        return f"unreachable: {e}"


def _health_vector_store_check() -> str:
    try:
        from src.services.vector_store import get_vector_store
        from src.core.config import settings
        vs = get_vector_store()
        if vs is None:
            if settings.VECTOR_STORE in ("", "memory"):
                return "memory (no persistent store configured)"
            return f"unavailable (configured {settings.VECTOR_STORE})"
        count = vs.count()
        if count <= 0:
            return f"empty (configured {settings.VECTOR_STORE})"
        vs.query("healthcheck probe", n=1)
        return f"ok ({count} points)"
    except Exception as e:
        return f"unreachable: {e}"


_RETRIEVAL_WARM = threading.Event()


def _health_hybrid_retrieval_check() -> str:
    try:
        from src.core.config import settings
        if settings.VECTOR_STORE == "qdrant":
            from src.services.hybrid_retrieval import _RERANK_RETRIEVER
            if os.getenv("USE_HYBRID_RETRIEVAL", "true").strip().lower() not in (
                "1", "true", "yes", "on"
            ):
                return "unavailable: hybrid retrieval is disabled"
            if os.getenv("USE_RERANKER", "true").strip().lower() not in ("1", "true", "yes", "on"):
                if _RETRIEVAL_WARM.is_set():
                    return "ready: Qdrant dense + BM25/RRF (reranker disabled)"
                return "warming: retrieval pipeline has not completed its warm-up query"
            if os.getenv("RERANK_PROVIDER", "local").strip().lower() != "local":
                return "unavailable: local BGE reranker is not required/configured"
            if _RERANK_RETRIEVER is None or _RERANK_RETRIEVER._reranker is None:
                return "warming: local BGE reranker has not passed its readiness probe"
            return "ready: Qdrant dense + BM25/RRF + local BGE reranker"
        from src.services.hybrid_retrieval import hybrid_status
        return hybrid_status()
    except Exception as e:
        return f"unavailable: {e}"


@app.get("/live")
async def liveness_check():
    """Pure process liveness probe for Docker/container orchestrators. Zero database calls."""
    return {"status": "alive", "service": "intelai"}


_HEALTH_CACHE_LOCK = threading.Lock()
_HEALTH_CACHE_TIME = 0.0
_HEALTH_CACHE_DATA = None


@app.get("/health")
async def health_check():
    global _HEALTH_CACHE_TIME, _HEALTH_CACHE_DATA
    now = time.time()
    with _HEALTH_CACHE_LOCK:
        if _HEALTH_CACHE_DATA is not None and (now - _HEALTH_CACHE_TIME) < 5.0:
            return _HEALTH_CACHE_DATA

    try:
        db_status, vs_status, retrieval_status = await asyncio.wait_for(
            asyncio.gather(
                asyncio.to_thread(_health_db_check),
                asyncio.to_thread(_health_vector_store_check),
                asyncio.to_thread(_health_hybrid_retrieval_check),
            ),
            timeout=5.0,
        )
    except asyncio.TimeoutError:
        db_status = vs_status = retrieval_status = "timeout"
    store_ready = vs_status == "ok" or vs_status.startswith(("ok (", "memory "))
    retrieval_ready = not retrieval_status.startswith(("warming", "unavailable", "timeout"))
    result = {
        "status": "healthy" if db_status == "ok" and store_ready and retrieval_ready else "degraded",
        "service": "IntelAI API",
        "version": "2026.3.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": db_status,
        "vector_store": vs_status,
        "retrieval": retrieval_status,
    }
    with _HEALTH_CACHE_LOCK:
        _HEALTH_CACHE_TIME = now
        _HEALTH_CACHE_DATA = result
    return result


@app.get("/ready")
async def readiness_check():
    result = await health_check()
    if result["status"] != "healthy":
        raise HTTPException(status_code=503, detail=result)
    return result


@app.get("/api/v1/status")
async def get_status(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics, get_available_periods, get_available_categories
    df = await asyncio.to_thread(get_kpi_metrics)
    return {
        "status": "operational",
        "user": user.username,
        "role": user.role,
        "total_kpis": len(df),
        "periods": await asyncio.to_thread(get_available_periods),
        "categories": await asyncio.to_thread(get_available_categories),
        "domains": ["Finance", "Growth", "People", "Operations", "IT", "ESG"],
    }


# ════════════════════════════════════════════════════════════
# AUTHENTICATION
# ════════════════════════════════════════════════════════════

# ── Credential-login throttle ──────────────────────────────────────────────
# Per (IP, username) failure counter: 5 failures → 15-minute lockout. In-memory
# is safe here (WEB_CONCURRENCY=1, same as _DEMO_LOGIN_HITS). Prevents online
# brute-force against the public admin login without hiding the form.
_LOGIN_FAILS: Dict[str, List[float]] = {}
_LOGIN_MAX_FAILS = int(os.environ.get("LOGIN_MAX_FAILURES", "5"))
_LOGIN_LOCKOUT_S = float(os.environ.get("LOGIN_LOCKOUT_SECONDS", "900"))


def _login_key(request: Request, username: str) -> str:
    ip = request.headers.get("X-Forwarded-For", "").split(",")[0].strip() or (request.client.host if request.client else "unknown")
    return f"{ip}:{(username or '').lower()[:64]}"


def _login_locked(key: str) -> bool:
    now = time.time()
    fails = [t for t in _LOGIN_FAILS.get(key, []) if now - t < _LOGIN_LOCKOUT_S]
    _LOGIN_FAILS[key] = fails
    return len(fails) >= _LOGIN_MAX_FAILS


def _record_login_fail(key: str) -> None:
    _LOGIN_FAILS.setdefault(key, []).append(time.time())


def _clear_login_fails(key: str) -> None:
    _LOGIN_FAILS.pop(key, None)


@app.post("/api/v1/auth/login")
async def login(req: LoginRequest, request: Request):
    key = _login_key(request, req.username)
    if _login_locked(key):
        raise HTTPException(status_code=429, detail="Too many failed login attempts. Try again later.")
    user_data = await _lookup_user_record(req.username)
    if not user_data or not verify_password(req.password, user_data["password_hash"]):
        _record_login_fail(key)
        try:
            from src.services.pg_store import log_audit_event
            await asyncio.to_thread(log_audit_event, req.username or "?", "LOGIN_FAILED", "Failed credential login attempt")
        except Exception:
            pass
        # Uniform message — never reveal whether the username exists.
        raise HTTPException(status_code=401, detail="Invalid username or password")
    _clear_login_fails(key)
    if not user_data.get("is_active", True):
        raise HTTPException(status_code=403, detail="Account deactivated")

    role = user_data["role"]
    token_data = TokenData(
        user_id=user_data["id"],
        username=user_data["username"],
        role=role,
        language=user_data.get("preferred_language", "en"),
    )
    token = create_access_token(token_data)

    try:
        from src.services.pg_store import log_audit_event
        await asyncio.to_thread(log_audit_event, req.username, "LOGIN", f"User {req.username} logged in")
    except Exception:
        import logging; logging.error('Unhandled exception', exc_info=True)
        pass

    from src.services.pg_store import get_available_categories
    all_categories = await asyncio.to_thread(get_available_categories)

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user_data["id"],
            "username": user_data["username"],
            "role": role,
            "full_name": user_data["username"].replace("_", " ").title(),
            "language": user_data.get("preferred_language", "en"),
            "pages": get_user_pages(role),
            "data_access": get_user_data_categories(role, all_categories),
            "actions": __import__('src.core.jwt_auth').core.jwt_auth.ROLE_DEFINITIONS.get(role, {}).get("actions", []),
        },
    }


_DEMO_LOGIN_HITS: Dict[str, List[float]] = {}
_DEMO_LOGIN_LIMIT = int(os.environ.get("DEMO_LOGIN_RATE_LIMIT", "20"))
_DEMO_LOGIN_WINDOW_S = 300.0


def _check_demo_login_rate_limit(request: Request) -> None:
    """Fixed-window limiter, per client IP: WEB_CONCURRENCY=1 means an in-memory dict is
    safe (no cross-worker consistency issue). Without this, demo-login — no password, no
    auth — hands out a real JWT (including role=admin, full data_access) to anyone who
    calls it, as many times as they like."""
    ip = request.headers.get("X-Forwarded-For", "").split(",")[0].strip() or (request.client.host if request.client else "unknown")
    now = time.time()
    hits = [t for t in _DEMO_LOGIN_HITS.get(ip, []) if now - t < _DEMO_LOGIN_WINDOW_S]
    if len(hits) >= _DEMO_LOGIN_LIMIT:
        raise HTTPException(status_code=429, detail="Too many demo-login attempts. Please wait a few minutes.")
    hits.append(now)
    _DEMO_LOGIN_HITS[ip] = hits


@app.post("/api/v1/auth/demo-login")
async def demo_login(role: str, request: Request):
    """One-click 'try as persona' for the demo — issues a token for the role WITHOUT exposing
    any password in the frontend. Gated by an explicit DEMO_MODE opt-in. Administrator access
    is never granted through this endpoint; real logins require configured credentials.

    Demo-session scoping (default on, DEMO_SESSION_SCOPING): when the caller sends
    X-Demo-Session-Id, each browser gets its own ephemeral identity per role — deterministic
    from (role, session id), so the same visitor keeps their chat history/uploads across
    requests, but two visitors who both pick "cfo" no longer share one user_id and can't see
    each other's chat sessions or uploaded files. Persona behavior (prompts, RBAC, page/data
    access) stays keyed by role either way. Falls back to the old shared-per-role identity
    when no session header is sent or scoping is disabled — not a production auth model."""
    import os as _os
    if _os.getenv("DEMO_MODE", "false").lower() != "true":
        raise HTTPException(status_code=403, detail="Demo mode disabled")
    _check_demo_login_rate_limit(request)
    from src.core.jwt_auth import ROLE_DEFINITIONS
    role = (role or "").lower()
    if role not in ROLE_DEFINITIONS:
        raise HTTPException(status_code=404, detail=f"Unknown role: {role}")
    if role == "admin":
        raise HTTPException(status_code=403, detail="Administrator access is not available through demo login")

    demo_session_id = request.headers.get("X-Demo-Session-Id") or request.query_params.get("session_id")
    from src.services.pg_store import get_or_create_demo_user, _demo_session_scoping_enabled
    if _demo_session_scoping_enabled() and demo_session_id:
        user_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"intelai-demo:{role}:{demo_session_id}"))
        username = f"{role}-{user_id[:8]}"
    else:
        # Deterministic per role, NOT a fresh uuid4 each call. When no bootstrap
        # users are configured _users_db is empty, so the old fallback minted a new
        # random id on every request while keeping username == role, which collided
        # on users_username_key from the second call onward.
        ud = _users_db.get(role)
        user_id = ud["id"] if ud else str(uuid.uuid5(uuid.NAMESPACE_URL, f"intelai-demo-role:{role}"))
        username = role
    # Use the id the database actually settled on — if a row already owned this
    # username, that row's id is the one the foreign keys point at.
    created = await asyncio.to_thread(get_or_create_demo_user, user_id, username, role, role.upper())
    user_id = created.get("id", user_id)

    token = create_access_token(TokenData(user_id=user_id, username=username, role=role, language="en"))
    from src.services.pg_store import get_available_categories
    all_categories = await asyncio.to_thread(get_available_categories)

    return {
        "access_token": token, "token_type": "bearer",
        "user": {
            "id": user_id, "username": username, "role": role,
            "full_name": role.upper(), "language": "en",
            "pages": get_user_pages(role), "data_access": get_user_data_categories(role, all_categories),
            "actions": ROLE_DEFINITIONS.get(role, {}).get("actions", []),
        },
    }


@app.post("/api/v1/auth/register")
async def register(req: RegisterRequest):
    if req.role not in {"viewer", "analyst"}:
        raise HTTPException(status_code=403, detail="Public registration is limited to viewer or analyst roles")
    if await _user_exists(req.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    user_id = str(uuid.uuid4())
    pw_hash = hash_password(req.password)
    # Keep the in-memory entry as a cache/fallback only — Postgres below is
    # authoritative when configured (login resolves through _lookup_user_record).
    _users_db[req.username] = {
        "id": user_id,
        "username": req.username,
        "password_hash": pw_hash,
        "role": req.role,
        "is_active": True,
        "preferred_language": req.preferred_language,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    # Persist to PostgreSQL — authoritative when configured; its generated id is
    # the one foreign keys (chat_sessions etc.) actually point at, so keep the
    # cache entry consistent with it.
    try:
        from src.services.pg_store import create_user
        created = await asyncio.to_thread(create_user, req.username, pw_hash, req.role, req.preferred_language)
        pg_id = (created or {}).get("id")
        if pg_id:
            user_id = pg_id
            _users_db[req.username]["id"] = pg_id
    except Exception as e:
        log.warning("PG user creation failed: %s", e)
    return {"status": "registered", "user_id": user_id, "username": req.username}


@app.get("/api/v1/auth/me")
async def get_me(user: TokenData = Depends(get_current_user)):
    user_data = await _lookup_user_record(user.username) or {}
    from src.services.pg_store import get_available_categories
    all_categories = await asyncio.to_thread(get_available_categories)
    return {
        "id": user.user_id,
        "username": user.username,
        "role": user.role,
        "full_name": user.username.replace("_", " ").title(),
        "language": user.language,
        "pages": get_user_pages(user.role),
        "data_access": get_user_data_categories(user.role, all_categories),
        "preferred_language": user_data.get("preferred_language", user.language),
        "actions": __import__('src.core.jwt_auth').core.jwt_auth.ROLE_DEFINITIONS.get(user.role, {}).get("actions", []),
    }


# ════════════════════════════════════════════════════════════
# CHAT & PERSONAS
# ════════════════════════════════════════════════════════════

class EmbedRequest(BaseModel):
    texts: List[str] = Field(..., min_length=1, max_length=256)
    model: Optional[str] = None


_embed_slots = asyncio.Semaphore(2)


@app.post("/embed")
async def embed_texts(req: EmbedRequest) -> Dict[str, Any]:
    """Embedding service for the other services in the ecosystem (internal token required).

    Lets RAGeval and StreamPulse share this process's already-loaded embedding model
    instead of each loading its own copy. Contract: ``{"texts": [...]}`` in,
    ``{"embeddings": [[...], ...]}`` out. Concurrency is bounded so embedding work cannot
    starve chat retrieval.
    """
    from src.services.vector_store import _embed

    texts = [t[:8000] for t in req.texts]
    async with _embed_slots:
        vecs = await asyncio.to_thread(_embed, texts)
    arr = vecs.tolist() if hasattr(vecs, "tolist") else [list(map(float, v)) for v in vecs]
    return {"embeddings": arr, "model": settings.EMBEDDING_MODEL, "dim": len(arr[0]) if arr else 0}


class ChatProviderError(RuntimeError):
    """The model provider failed to produce an answer for a chat turn."""


async def _run_chat_turn(req: "ChatRequest", user: TokenData, emit=None) -> Dict[str, Any]:
    """The actual chat pipeline — retrieval + LLM completion + persistence. Shared by
    the synchronous POST /api/v1/chat and the async POST /api/v1/chat/async + GET
    /api/v1/chat/{job_id} pair, so both paths produce identical results; only how the
    caller receives them differs."""
    import json as _json
    from src.services.omnismart_chatbot import get_persona_factory
    from src.services.pg_store import set_request_scope_strict, get_request_scope_user, get_request_scope_strict
    set_request_scope_strict(bool(req.sandbox_only))
    log.info("chat turn sandbox_only=%s strict=%s scope_user=%s", req.sandbox_only, get_request_scope_strict(), get_request_scope_user())

    session_id = req.session_id or str(uuid.uuid4())

    # Ensure session exists in PostgreSQL
    try:
        from src.services.pg_store import ensure_session_exists, store_message
        await asyncio.to_thread(ensure_session_exists, session_id, user.user_id)
    except Exception:
        pass  # Fallback — still works without PG

    # Prior turns in this session, so follow-up questions have continuity. The WebSocket
    # handler keeps this in memory per connection; REST has no persistent connection, so
    # it is loaded from Postgres instead.
    history = await asyncio.to_thread(_load_chat_history, user.user_id, session_id)

    # Persona-routed RAG copilot: factory.chat auto-retrieves a role-scoped KPI
    # snapshot + knowledge docs and returns grounded answers with source citations.
    # (Same path as the WebSocket handler, so REST and the WS fallback behave identically.)
    factory = get_persona_factory()
    # factory.chat is the expensive part of this request — retrieval + an LLM completion,
    # typically seconds — and is synchronous throughout (sync retrieval, sync LLM client
    # calls). Off the event loop so one in-flight chat can't stall every other request.
    try:
        result = await asyncio.wait_for(
            asyncio.to_thread(
                factory.chat,
                message=req.message,
                user_role=user.role,
                persona_override=req.persona,
                language=req.language or user.language,
                context=req.context or "",
                history=history,
                emit=emit,
            ),
            timeout=_chat_turn_timeout_seconds(),
        )
    except asyncio.TimeoutError as e:
        raise TimeoutError(
            f"chat turn exceeded CHAT_TURN_TIMEOUT={int(_chat_turn_timeout_seconds())}s"
        ) from e

    if result.get("error"):
        # A failed model call is a failed turn: surface it as an error status and do not
        # store the apology text as if it were an answer.
        raise ChatProviderError(str(result["error"]))

    response_text = result.get("response", "")
    sources = result.get("sources", [])

    # Persist both messages to PostgreSQL
    try:
        await asyncio.to_thread(store_message, session_id, "user", req.message)
        await asyncio.to_thread(store_message,
            session_id, "assistant", response_text,
            sources=_json.dumps(sources) if sources else "[]",
            tokens_used=result.get("tokens_used", 0),
            latency_ms=result.get("latency_ms", 0),
        )
    except Exception as e:
        log.warning("PG message store failed: %s", e)

    return {
        "response": response_text,
        "persona_used": result.get("persona_used"),
        "persona_display": result.get("persona_display"),
        "tokens_used": result.get("tokens_used", 0),
        "latency_ms": result.get("latency_ms", 0),
        "session_id": session_id,
        "sources": sources,
        "blocks": _structure_answer(response_text),
    }


@app.post("/api/v1/chat")
async def chat(req: ChatRequest, user: TokenData = Depends(get_current_user)):
    try:
        return await _run_chat_turn(req, user)
    except TimeoutError as e:
        raise HTTPException(status_code=504, detail=str(e))
    except ChatProviderError as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.post("/api/v1/chat/async")
async def chat_async(req: ChatRequest, background: BackgroundTasks,
                      user: TokenData = Depends(get_current_user)):
    """Same pipeline as POST /api/v1/chat, but returns a job_id immediately and runs
    the actual chat turn as a background task instead of blocking the request until
    it's done.

    Exists because a real chat turn under cold retrieval (see BENCHMARK.md) can take
    60-100s+ — long enough that a reverse proxy in front of this service (Cloudflare,
    in production) risks cutting the connection before an otherwise-successful
    response comes back. Confirmed live: repeated 524s on POST /api/v1/chat under
    exactly this condition. Polling in short, fast requests instead means no single
    request can ever run long enough to hit that ceiling — same pattern DocIntel's
    POST /batch/upload + GET /batch/{job_id} already uses for the identical reason.
    """
    from src.services.chat_jobs import new_job, run_job
    from src.services import retrieval_progress as _rp
    job_id = new_job(req.model_dump(), owner_user_id=user.user_id)

    async def _turn_with_progress():
        # Retrieval stages report under this job id; the threads the turn spawns
        # inherit the binding, and the poll endpoint below reads it back.
        token = _rp.set_progress_key(job_id)
        _rp.board.update(job_id, stage="starting")
        stages: Dict[str, Dict[str, Any]] = {}

        def _emit(ev: Dict[str, Any]) -> None:
            if ev.get("type") == "stage":
                stages[ev["stage"]] = {k: v for k, v in ev.items() if k != "type"}
                _rp.board.update(job_id, turn_stages=list(stages.values()))
            elif ev.get("type") == "sources":
                prev = (_rp.board.get(job_id) or {}).get("turn_sources", [])
                _rp.board.update(job_id, turn_sources=prev + list(ev.get("sources") or []))

        try:
            return await _run_chat_turn(req, user, emit=_emit)
        finally:
            _rp.reset_progress_key(token)

    background.add_task(run_job, job_id, _turn_with_progress)
    return {"job_id": job_id}


@app.post("/api/v1/chat/stream")
async def chat_stream(req: ChatRequest, user: TokenData = Depends(get_current_user)):
    """Server-sent events for one chat turn: ``stage`` events as the pipeline progresses,
    ``sources`` as soon as they are known (knowledge base first, then web), ``chunk``
    events with the answer as it is generated, and a final ``done`` event carrying the
    persisted result. Clients that cannot read the stream fall back to /chat/async."""
    import json as _json
    import time as _time
    from fastapi.responses import StreamingResponse
    from src.services.omnismart_chatbot import get_persona_factory, llm_stream

    queue: "asyncio.Queue[Optional[Dict[str, Any]]]" = asyncio.Queue()
    loop = asyncio.get_running_loop()

    def emit(ev: Dict[str, Any]) -> None:
        loop.call_soon_threadsafe(queue.put_nowait, ev)

    async def produce() -> None:
        try:
            session_id = req.session_id or str(uuid.uuid4())
            try:
                from src.services.pg_store import ensure_session_exists
                await asyncio.to_thread(ensure_session_exists, session_id, user.user_id)
            except Exception:
                pass
            history = await asyncio.to_thread(_load_chat_history, user.user_id, session_id)
            factory = get_persona_factory()
            started = _time.time()
            try:
                prepared = await asyncio.wait_for(
                    asyncio.to_thread(
                        factory.chat_prepare,
                        message=req.message, user_role=user.role, persona_override=req.persona,
                        language=req.language or user.language, history=history,
                        context=req.context or "", emit=emit,
                    ),
                    timeout=_chat_turn_timeout_seconds(),
                )
            except asyncio.TimeoutError:
                await queue.put({"type": "error", "error": "The search took too long. Please try again."})
                return
            await queue.put({"type": "meta", "persona": prepared.get("persona_name"),
                             "persona_display": prepared.get("persona_display"),
                             "session_id": session_id})
            await queue.put({"type": "stage", "stage": "generating", "status": "running"})
            text, first_token_ms = "", None
            gen_started = _time.time()
            try:
                async for piece in llm_stream(
                    messages=prepared["messages"], temperature=prepared.get("temperature", 0.3),
                    max_tokens=2048, persona_name=prepared.get("persona_name"),
                ):
                    if first_token_ms is None:
                        first_token_ms = int((_time.time() - gen_started) * 1000)
                    text += piece
                    await queue.put({"type": "chunk", "text": piece})
            except Exception as exc:
                log.error("chat stream generation failed: %s", exc)
                if not text:
                    await queue.put({"type": "error", "error": "The model provider did not respond. Please try again."})
                    return
            await queue.put({"type": "stage", "stage": "generating", "status": "done",
                             "ms": int((_time.time() - gen_started) * 1000), "first_token_ms": first_token_ms})
            sources = prepared.get("sources", [])
            try:
                from src.services.pg_store import store_message
                await asyncio.to_thread(store_message, session_id, "user", req.message)
                await asyncio.to_thread(store_message, session_id, "assistant", text,
                                        sources=_json.dumps(sources) if sources else "[]",
                                        tokens_used=0, latency_ms=int((_time.time() - started) * 1000))
            except Exception as exc:
                log.warning("PG message store failed: %s", exc)
            await queue.put({
                "type": "done", "response": text, "session_id": session_id,
                "persona_used": prepared.get("persona_name"), "persona_display": prepared.get("persona_display"),
                "latency_ms": int((_time.time() - started) * 1000), "sources": sources,
                "blocks": _structure_answer(text), "web": prepared.get("web_state"),
            })
        except Exception as exc:  # never leave the client hanging
            log.error("chat stream failed: %s", exc)
            await queue.put({"type": "error", "error": "The request failed. Please try again."})
        finally:
            await queue.put(None)

    async def events():
        task = asyncio.create_task(produce())
        try:
            yield ": open\n\n"
            while True:
                try:
                    ev = await asyncio.wait_for(queue.get(), timeout=10)
                except asyncio.TimeoutError:
                    yield ": keep-alive\n\n"
                    continue
                if ev is None:
                    break
                yield f"data: {_json.dumps(ev, ensure_ascii=False)}\n\n"
        finally:
            if not task.done():
                task.cancel()

    return StreamingResponse(events(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache, no-transform", "X-Accel-Buffering": "no"})


@app.get("/api/v1/chat/sessions")
async def get_chat_sessions(
    request: Request,
    user: TokenData = Depends(get_current_user),
    x_admin_token: Optional[str] = Header(default=None, alias="X-Admin-Token"),
    x_intelai_token: Optional[str] = Header(default=None, alias="X-IntelAI-Internal-Token"),
):
    """Registered here, ahead of GET /api/v1/chat/{job_id}, on purpose: Starlette matches
    routes in registration order, and a single-segment path-param route matches literally
    anything in that slot. Defined after chat_job_status, GET /api/v1/chat/sessions would
    be captured by it with job_id="sessions". Keep this ahead of chat_job_status."""
    try:
        from src.services.pg_store import get_user_sessions
        admin_secret = os.getenv("ADMIN_TOKEN")
        is_admin = bool(
            (x_admin_token and admin_secret and hmac.compare_digest(x_admin_token, admin_secret)) or
            (user.role == "admin" and request.headers.get("X-Scope-All", "").lower() == "true")
        )
        target_user = "*" if is_admin else user.user_id
        sessions = await asyncio.to_thread(get_user_sessions, target_user, limit=50)
        return {"sessions": sessions}
    except Exception as e:
        return {"sessions": [], "error": str(e)}


@app.get("/api/v1/chat/{job_id}")
async def chat_job_status(job_id: str, user: TokenData = Depends(get_current_user)):
    """Poll target for POST /api/v1/chat/async. Returns {status: pending|running} while
    in flight, or {status: done, ...same shape as POST /api/v1/chat...} /
    {status: error, error: "..."} once finished. 404 if the job doesn't exist, has
    expired (1h TTL), or belongs to a different user."""
    from src.services.chat_jobs import get_job
    job = await asyncio.to_thread(get_job, job_id, user.user_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")
    out = {"job_id": job_id, "status": job["status"]}
    if job["status"] == "done":
        out.update(job.get("result") or {})
    elif job["status"] == "error":
        out["error"] = job.get("error")
    else:
        from src.services.retrieval_progress import board
        state = board.get(job_id)
        if state:
            out["progress"] = {k: state[k] for k in ("stage", "done", "total", "candidates")
                               if k in state}
            if state.get("preliminary"):
                out["preliminary_sources"] = state["preliminary"]
            if state.get("turn_stages"):
                out["stages"] = state["turn_stages"]
            if state.get("turn_sources"):
                out["turn_sources"] = state["turn_sources"]
    return out


@app.get("/api/v1/personas")
async def list_personas(user: TokenData = Depends(get_current_user)):
    from src.services.omnismart_chatbot import get_persona_factory
    factory = get_persona_factory()
    return {"personas": factory.list_personas(user_role=user.role)}


# In-memory cache of French-translated glossary entries (term -> translated dict).
_GLOSSARY_FR_CACHE: Dict[str, Dict[str, Any]] = {}
_GLOSSARY_TEXT_FIELDS = ("definition", "benchmark", "interpretation", "why_it_matters", "example")


async def _localize_glossary_entry(entry: Dict[str, Any], lang: str) -> Dict[str, Any]:
    """Return the entry with its prose fields in ``lang`` (fr). Prefers the static,
    pre-generated ``GLOSSARY_FR`` (complete + instant + LLM-independent) and only falls
    back to on-the-fly LLM translation for any field it doesn't cover. Numbers/formulas
    are left untouched; English is the final fallback."""
    if lang != "fr" or not entry:
        return entry
    term = entry.get("term")
    # 1) Static French overlay — the authoritative, complete source.
    try:
        from data.glossary_fr import GLOSSARY_FR
        static = GLOSSARY_FR.get(str(term)) or {}
    except Exception:
        static = {}
    entry = {**entry, **{k: v for k, v in static.items()
                         if k in _GLOSSARY_TEXT_FIELDS and isinstance(v, str) and v.strip()}}
    key = str(term or entry.get("definition", ""))[:80]
    if key in _GLOSSARY_FR_CACHE:
        return _GLOSSARY_FR_CACHE[key]
    # 2) LLM only for any text field the static set didn't cover (rare).
    remaining = {k: entry[k] for k in _GLOSSARY_TEXT_FIELDS
                 if isinstance(entry.get(k), str) and entry[k].strip() and k not in static}
    if not remaining:
        _GLOSSARY_FR_CACHE[key] = entry
        return entry
    try:
        import json as _json
        from src.services.llm_router import llm_call
        prompt = (
            "Translate the string VALUES of this JSON object to French. Keep the keys unchanged, "
            "keep numbers, %, currency and formulas as-is, and return ONLY the JSON object:\n"
            + _json.dumps(remaining, ensure_ascii=False)
        )
        resp = await llm_call([{"role": "user", "content": prompt}], tier="default",
                              temperature=0.0, max_tokens=500)
        txt = resp["choices"][0]["message"]["content"]
        txt = txt[txt.find("{"): txt.rfind("}") + 1]
        translated = _json.loads(txt)
        out = {**entry, **{k: v for k, v in translated.items() if k in remaining}}
    except Exception as e:
        log.warning("glossary fr translation failed (%s) — serving English", e)
        out = entry
    _GLOSSARY_FR_CACHE[key] = out
    return out


@app.get("/api/v1/glossary")
async def get_glossary(
    domain: Optional[str] = None,
    term: Optional[str] = None,
    lang: Optional[str] = None,
    user: TokenData = Depends(get_current_user),
):
    """Authoritative, sourced domain glossary — powers the per-page contextual
    explainer and grounds term definitions (no hallucination). ``lang=fr`` returns
    French definitions (LLM-translated + cached; numbers/formulas preserved)."""
    import asyncio
    from data.glossary import for_domain, get_term
    lang = (lang or getattr(user, "language", None) or "en").lower()
    if term:
        entry = get_term(term)
        if not entry:
            raise HTTPException(status_code=404, detail=f"Term not found: {term}")
        return await _localize_glossary_entry(entry, lang)
    terms = for_domain(domain)
    if lang == "fr":
        terms = await asyncio.gather(*[_localize_glossary_entry(t, lang) for t in terms])
    return {"terms": list(terms)}


# ════════════════════════════════════════════════════════════
# VOICE (TTS / STT)
# ════════════════════════════════════════════════════════════

# OCR extraction is out of IntelAI's scope — it belongs to the DocIntel project.

# ════════════════════════════════════════════════════════════
# FILE MANAGEMENT
# ════════════════════════════════════════════════════════════

@app.get("/api/v1/files")
async def get_user_files(
    request: Request,
    user: TokenData = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    x_admin_token: Optional[str] = Header(default=None, alias="X-Admin-Token"),
    x_intelai_token: Optional[str] = Header(default=None, alias="X-IntelAI-Internal-Token"),
):
    """Get user's uploaded files."""
    from src.services.pg_store import get_user_files
    admin_secret = os.getenv("ADMIN_TOKEN")
    is_admin = bool(
        (x_admin_token and admin_secret and hmac.compare_digest(x_admin_token, admin_secret)) or
        (user.role == "admin" and request.headers.get("X-Scope-All", "").lower() == "true")
    )
    target_user = "*" if is_admin else user.username
    files = await asyncio.to_thread(get_user_files, target_user, limit=limit, offset=offset)
    return files

@app.get("/api/v1/files/{file_id}/preview")
async def get_file_preview(
    file_id: str,
    user: TokenData = Depends(get_current_user)
):
    """Get file preview content."""
    from src.services.pg_store import get_file_content
    content = await asyncio.to_thread(get_file_content, file_id, user.username)
    if not content:
        raise HTTPException(status_code=404, detail="File not found")
    return {"content": content[:10000]}  # Limit preview size

@app.delete("/api/v1/files/{file_id}")
async def delete_file_endpoint(
    file_id: str,
    user: TokenData = Depends(get_current_user)
):
    """Delete an uploaded file."""
    from src.services.pg_store import delete_file, get_file_path
    import os

    path = await asyncio.to_thread(get_file_path, file_id, user.username)
    if not path:
        raise HTTPException(status_code=404, detail="File not found")

    success = await asyncio.to_thread(delete_file, file_id, user.username)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete file from DB")

    if os.path.exists(path):
        try:
            os.remove(path)
        except Exception:
            import logging; logging.error('Unhandled exception', exc_info=True)
            pass

    # Trigger background reindex to remove from vector store if necessary
    try:
        pass
        # Not using background tasks here to avoid import issues, just doing it synchronously or let it be
    except:
        pass

    return {"status": "ok"}

@app.get("/api/v1/files/{file_id}/download")
async def download_file(
    file_id: str,
    user: TokenData = Depends(get_current_user)
):
    """Download file."""
    from src.services.pg_store import get_file_path
    file_path = await asyncio.to_thread(get_file_path, file_id, user.username)
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        file_path,
        media_type='application/octet-stream',
        filename=os.path.basename(file_path)
    )


# Voice (TTS/STT) is out of IntelAI's scope — it belongs to the VoiceFlow project.

# ════════════════════════════════════════════════════════════
# DATA INGESTION
# ════════════════════════════════════════════════════════════

@app.post("/api/v1/ingest/metrics")
async def ingest_metrics(
    req: IngestMetricsRequest,
    user: TokenData = Depends(get_current_user),
):
    from src.services.pg_store import store_kpi_metrics, log_audit_event
    df = pd.DataFrame(req.data)
    if df.empty:
        raise HTTPException(status_code=400, detail="No data provided")
    await asyncio.to_thread(store_kpi_metrics, df, source_name=req.source_name, replace=req.replace, owner_user_id=user.user_id)
    await asyncio.to_thread(log_audit_event, user.username, "DATA_INGEST", f"Ingested {len(df)} metrics from {req.source_name}")
    return {"status": "ingested", "rows": len(df), "source": req.source_name}

async def _process_webhook_payload(payload: WebhookPayload, actor: str) -> Dict[str, Any]:
    """Shared ingestion logic for both the JWT-gated /api/v1/ingest/webhook
    (internal/authenticated use) and the HMAC-signed public
    /api/v1/webhook/{source_name} (external system-to-system use — StreamPulse,
    a Kafka HTTP sink connector, n8n, or VoiceFlow's own signed relay).
    Implements Strict Schema Enforcement and Background Auto-Categorization."""
    from src.services.pg_store import log_audit_event
    import asyncio

    if payload.schema_type == "kpi_metrics":
        if not isinstance(payload.data, list):
            raise HTTPException(status_code=422, detail="data must be a list of metrics")
        df = pd.DataFrame(payload.data)
        if df.empty or "metric_name" not in df.columns or "value" not in df.columns:
            raise HTTPException(status_code=422, detail="Strict schema violation: Missing metric_name or value fields")
        # store_kpi_metrics() reads the "metric" column, not "metric_name".
        df = df.rename(columns={"metric_name": "metric"})

        from src.services.pg_store import store_kpi_metrics
        # owner_user_id=None: external system-to-system feeds are real ingested
        # data, not one visitor's private demo scratch space — same as an
        # authenticated ingest with no specific owner.
        await asyncio.to_thread(store_kpi_metrics, df, source_name=payload.source, replace=False, owner_user_id=None)
        await asyncio.to_thread(log_audit_event, actor, "WEBHOOK_INGEST", f"Ingested {len(df)} metrics from {payload.source}")
        return {"status": "success", "processed": len(df), "type": "kpi_metrics"}

    elif payload.schema_type == "knowledge_doc":
        if not isinstance(payload.data, dict) or "content" not in payload.data:
            raise HTTPException(status_code=422, detail="Strict schema violation: content field missing")

        content_text = payload.data["content"]
        await asyncio.to_thread(log_audit_event, actor, "WEBHOOK_INGEST", f"Received knowledge doc from {payload.source}")

        # Auto-Categorization Pipeline (reusing same backend functions as UI upload)
        def _process_background():
            try:
                from src.services.pg_store import store_knowledge_docs
                from src.services.vector_store import get_vector_store
                from src.services.llm_router import llm_call
                import pandas as _pd

                # 1. LLM Auto-Categorization
                try:
                    resp = asyncio.run(llm_call([{"role": "user", "content": f"Classify this text into a domain (Finance, HR, Operations, ESG, IT, Growth). Reply with 1 word.\n\nText: {content_text[:500]}"}]))
                    domain = resp["choices"][0]["message"]["content"].strip()
                except Exception:
                    domain = "General"

                # 2. Persist to knowledge_base — the single source of truth every
                # retrieval path reads from (vector store, hybrid, in-process). Global/
                # shared, same as an external system-to-system KPI feed above.
                doc_id = str(uuid.uuid4())
                title = f"{payload.source} — {domain}"
                docs_df = _pd.DataFrame([{
                    "doc_id": doc_id, "title": title, "content": content_text,
                    "source": payload.source, "embedding": "",
                }])
                store_knowledge_docs(docs_df, owner_user_id=None)

                # 3. Index it immediately. The vector-store backends
                # (ChromaVectorStore/PgVectorStore/QdrantVectorStore) implement
                # upsert/query/count/reset.
                vs = get_vector_store()
                if vs:
                    vs.upsert([{"doc_id": doc_id, "title": title, "content": content_text[:4000],
                                "source": payload.source, "category": domain,
                                "owner_user_id": None}])
                log.info(f"Webhook doc successfully auto-categorized as {domain} and indexed.")
            except Exception as e:
                log.error(f"Background webhook processing failed: {e}")

        # Fire and forget
        asyncio.create_task(asyncio.to_thread(_process_background))
        return {"status": "success", "message": "Document accepted for background processing and categorization", "type": "knowledge_doc"}

    else:
        raise HTTPException(status_code=422, detail=f"Unsupported schema_type: {payload.schema_type}")


@app.post("/api/v1/ingest/webhook")
async def generic_webhook_ingest(
    payload: WebhookPayload,
    user: TokenData = Depends(get_current_user),
):
    """Authenticated (JWT) generic webhook for internal/UI-driven ingestion."""
    return await _process_webhook_payload(payload, actor=user.username)


def _verify_webhook_signature(body: bytes, signature: str) -> bool:
    """HMAC-SHA256 of the raw body against INGEST_WEBHOOK_SECRET — same
    `sha256=<hex>` convention StreamPulse's own webhook_receiver.py verifies
    against, so anything that can sign a request for StreamPulse can sign one
    for this endpoint with zero changes beyond the URL and secret."""
    import hashlib
    import hmac as _hmac
    if not settings.INGEST_WEBHOOK_SECRET or not signature:
        return False
    expected = _hmac.new(settings.INGEST_WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()
    sig = signature.replace("sha256=", "")
    return _hmac.compare_digest(expected, sig)


@app.post("/api/v1/webhook/{source_name}")
async def public_signed_webhook_ingest(source_name: str, request: Request):
    """Public, HMAC-signed ingestion endpoint for external systems that can't
    do an interactive JWT login — StreamPulse, a Kafka HTTP sink connector,
    n8n, or VoiceFlow's own signed /integrations/relay. No user session
    required; authenticity comes entirely from the signature.

    Body: {"source": "...", "schema_type": "kpi_metrics"|"knowledge_doc", "data": ...}
    Header: X-Signature-256: sha256=<hmac-sha256 hex of the raw body>

    501 if INGEST_WEBHOOK_SECRET isn't configured — this endpoint refuses all
    requests rather than silently accepting unauthenticated data. 401 on a
    missing/invalid signature.
    """
    if not settings.INGEST_WEBHOOK_SECRET:
        raise HTTPException(status_code=501, detail="INGEST_WEBHOOK_SECRET not configured — public webhook ingestion is disabled")
    body = await request.body()
    signature = request.headers.get("X-Signature-256", "")
    if not _verify_webhook_signature(body, signature):
        raise HTTPException(status_code=401, detail="invalid_signature")
    try:
        import json as _json
        raw = _json.loads(body or b"{}")
    except Exception:
        raise HTTPException(status_code=400, detail="invalid_json")
    raw.setdefault("source", source_name)
    payload = WebhookPayload(**raw)
    return await _process_webhook_payload(payload, actor=f"webhook:{source_name}")


@app.post("/api/v1/ingest/csv")
async def ingest_csv_file(
    file: UploadFile = File(...),
    source_name: str = Form("csv_upload"),
    global_scope: bool = Form(False),
    user: TokenData = Depends(get_current_user),
):
    """Upload a CSV file with metrics (metric_name, value, period, category, segment).

    Rows are scoped to the uploader by default, so one visitor's upload never shows
    up on another's dashboard. Seeding the shared baseline is the deliberate
    exception: `global_scope=true` writes rows with a NULL owner, visible to
    everyone, and is restricted to admins because it edits what every visitor sees.
    Without this the documented "seed through the official API" path could only ever
    produce data private to whoever ran it.

    A per-row `source` column is preserved as each row's provenance; `source_name`
    labels rows that don't carry one.
    """
    import io
    from src.services.pg_store import store_kpi_metrics, log_audit_event
    content = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid CSV: {e}")
    if df.empty:
        raise HTTPException(status_code=400, detail="CSV file is empty")
    # store_kpi_metrics() reads the "metric" column — the docstring above documents
    # "metric_name" as the CSV header, so without this rename a correctly-formatted
    # upload would silently store every row with metric='' (same bug as the webhook
    # path, fixed there too; found via live verification).
    df = df.rename(columns={"metric_name": "metric"})

    if global_scope and (user.role or "").lower() != "admin":
        raise HTTPException(status_code=403, detail="global_scope requires an admin role")
    owner = None if global_scope else user.user_id

    await asyncio.to_thread(store_kpi_metrics, df, source_name=source_name, replace=False, owner_user_id=owner)
    await asyncio.to_thread(log_audit_event,
        user.username, "CSV_INGEST",
        f"Ingested {len(df)} rows from {file.filename}"
        f"{' (global baseline)' if global_scope else ''}",
    )
    return {
        "status": "ingested", "rows_inserted": len(df), "filename": file.filename,
        "scope": "global" if global_scope else "user",
    }


async def _delegate_to_doc_processor(content: bytes, filename: str) -> str:
    """Extract document/image text via the external document processor.

    By design, each tool in this project family is standalone and must not do
    another tool's job. Document/image/vision understanding is DocIntel's domain,
    so IntelAI does **zero** local PDF/image processing — no pypdf, no vision model.
    This is the ONLY extraction path; there is deliberately no local fallback, because
    a silent fallback both violates that boundary and hides a broken processor behind
    lower-quality output (exactly what happened before: a misconfigured processor
    returned 80 characters for a 60-page report and the inline path masked it).

    Contract — the processor must implement ONE of these (tried in this order, first
    that yields text wins; every one is a *different endpoint on the same processor*,
    not a different processor, so this is not a cross-vendor fallback chain):
      1. POST {url}/extract/text  -> {"text": "..."}          full document text
      2. POST {url}/extract/marker-> {"markdown": "..."}      PDF -> Markdown (Marker)
      3. POST {url}/process       -> {"raw_text"|"fields"}    structured extraction
    DocIntel speaks all three natively; any compliant processor can too.

    The two route-taking endpoints do NOT share a route vocabulary, so they get one
    setting each. Sending one value to both meant whichever endpoint didn't recognise
    it quietly fell back to its weakest path — a 1.2MB report came back as 32
    characters that way, and the caller had no way to tell that from a short document.
      DOC_PROCESSOR_TEXT_ROUTE -> /extract/text: auto | marker | ocr
          "auto" prefers Marker (structured Markdown), the better choice for text
          destined for a RAG index, and falls back to the native text layer when
          Marker is not installed.
      DOC_PROCESSOR_ROUTE      -> /process: vision_route_a (Claude Sonnet Vision,
          paid per page) | vision_route_b (self-hosted Ollama, $0) | ocr_fallback
          (Tesseract, $0).

    A result that is non-empty but implausibly short is treated as a miss rather than
    a success: extraction continues to the next endpoint and the longest result wins.
    Accepting the first non-empty string let a near-empty extraction mask a good one.

    Raises RuntimeError on failure — the caller turns that into a 502 so the operator
    sees a real error instead of a silently degraded ingest.
    """
    if not settings.DOC_PROCESSOR_URL:
        raise RuntimeError(
            "DOC_PROCESSOR_URL not configured — IntelAI does not process documents "
            "itself, by design. Point it at a document "
            "processor (e.g. a DocIntel instance) to enable document ingestion."
        )
    import httpx
    headers = {}
    if settings.DOC_PROCESSOR_TOKEN:
        headers["Authorization"] = f"Bearer {settings.DOC_PROCESSOR_TOKEN}"
    vision_route = _os.environ.get("DOC_PROCESSOR_ROUTE", "ocr_fallback")
    text_route = _os.environ.get("DOC_PROCESSOR_TEXT_ROUTE", "auto")
    timeout = _env_number("DOC_PROCESSOR_TIMEOUT", 180.0)
    min_yield = _env_number("DOC_PROCESSOR_MIN_CHARS", 200, int)

    async def _extract_via_batch(client, content, filename, route):
        """Async path for documents too slow for a synchronous call (edge ~100s
        timeouts). POST /extract/text/batch -> poll /batch/{id} -> results."""
        resp = await client.post(
            f"{settings.DOC_PROCESSOR_URL}/extract/text/batch",
            files={"file": (filename, content)},
            data={"route": route},
            headers=headers,
        )
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        job_id = resp.json().get("job_id")
        if not job_id:
            return None
        deadline = _os.environ.get("DOC_PROCESSOR_BATCH_TIMEOUT", "600")
        import time as _t
        end = _t.time() + float(deadline)
        while _t.time() < end:
            st = await client.get(f"{settings.DOC_PROCESSOR_URL}/batch/{job_id}", headers=headers)
            if st.status_code == 200:
                status = (st.json() or {}).get("status", "")
                if status in ("completed", "done", "finished", "failed"):
                    break
            await asyncio.sleep(3)
        res = await client.get(f"{settings.DOC_PROCESSOR_URL}/batch/{job_id}/results", headers=headers)
        if res.status_code != 200:
            return None
        results = (res.json() or {}).get("results") or []
        if results and isinstance(results[0], dict):
            return results[0].get("text") or results[0].get("markdown")
        return None

    attempts = [
        ("/extract/text", {"route": text_route}, ("text",)),
        ("/extract/marker", None, ("markdown",)),
        ("/process", {"route": vision_route}, ("raw_text",)),
    ]
    best = ""
    errors = []
    async with httpx.AsyncClient(timeout=timeout) as client:
        for path, data, keys in attempts:
            try:
                resp = await client.post(
                    f"{settings.DOC_PROCESSOR_URL}{path}",
                    files={"file": (filename, content)},
                    data=data,
                    headers=headers,
                )
                if resp.status_code == 404:
                    errors.append(f"{path}: not implemented by processor")
                    continue
                resp.raise_for_status()
                result = resp.json()
                for k in keys:
                    val = result.get(k)
                    if isinstance(val, str) and val.strip():
                        if len(val.strip()) >= min_yield:
                            return val
                        # Too little to be a real extraction of this document: hold
                        # it as a floor and let the next endpoint try to beat it.
                        if len(val.strip()) > len(best):
                            best = val
                        errors.append(
                            f"{path}: only {len(val.strip())} chars (< {min_yield})")
                # /process may only return typed fields (invoice-shaped) — usable, but
                # it is NOT full document text, so it is the last thing we accept.
                if path == "/process":
                    fields = result.get("fields")
                    if isinstance(fields, dict):
                        flat = "\n".join(f"{k}: {v}" for k, v in fields.items()
                                         if not k.startswith("_") and v not in (None, "", [], {}))
                        if flat.strip():
                            log.warning(
                                "Document processor returned only structured fields for %s "
                                "(no full text) — RAG quality will be poor. Enable "
                                "/extract/text or /extract/marker on the processor.", filename)
                            return flat
                errors.append(f"{path}: returned no usable text ({result.get('error') or 'empty'})")
            except Exception as e:
                errors.append(f"{path}: {e}")
                if path == "/extract/text":
                    try:
                        batched = await _extract_via_batch(client, content, filename, text_route)
                        if isinstance(batched, str) and batched.strip():
                            if len(batched.strip()) >= min_yield:
                                return batched
                            if len(batched.strip()) > len(best):
                                best = batched
                    except Exception as be:
                        errors.append(f"{path} (batch): {be}")

    if best.strip():
        # Every endpoint came in under the yield floor. Some text beats none, but say
        # so loudly — this is the signature of a document the processor cannot really
        # read (a malformed or scanned-only PDF), not of a short document.
        log.warning(
            "Document processor returned only %d chars for %s — below the %d-char "
            "floor on every route. Tried: %s", len(best.strip()), filename, min_yield,
            "; ".join(errors))
        return best

    # Log the internal detail server-side; the client gets a generic message —
    # upstream URLs and internal route paths must never leak to visitors.
    log.warning("Document extraction failed for %s. Processor: %s. Tried: %s",
                filename, settings.DOC_PROCESSOR_URL, "; ".join(errors))
    raise RuntimeError(
        f"could not extract text from {filename} — the file may be unsupported, "
        "scanned-only, or too complex. Try a different format or a clearer scan."
    )


@app.post("/api/v1/ingest/document")
async def ingest_document(
    file: UploadFile = File(...),
    category: str = Form("Misc"),
    global_scope: bool = Form(False),
    user: TokenData = Depends(get_current_user),
):
    from src.services.pg_store import store_knowledge_docs, log_audit_event
    # Default private: an uploaded document belongs to its uploader only, never the
    # shared corpus every visitor's chat can retrieve — the same owner_user_id contract
    # as the CSV KPI endpoint below. global_scope=true (admin-only) is how seed_data.py's
    # digest/corpus stage seeds the real shared baseline through this same endpoint.
    if global_scope and (user.role or "").lower() != "admin":
        raise HTTPException(status_code=403, detail="global_scope requires an admin role")
    owner = None if global_scope else user.user_id
    content = await file.read()
    filename_lower = (file.filename or "").lower()

    # Anything that needs parsing/OCR/vision to read (PDF, image, Office doc) is the
    # document processor's job, not IntelAI's — a project must not do another
    # project's work. IntelAI keeps zero PDF/image processing code
    # and no local fallback; a failing processor surfaces as a 502, not as silently
    # degraded text. Plain-text formats are read directly because that needs no document
    # intelligence at all — it's just a decode, not extraction.
    PLAIN_TEXT_EXT = (".txt", ".md", ".csv", ".json", ".log", ".xml", ".yaml", ".yml", ".tsv")
    if filename_lower.endswith(PLAIN_TEXT_EXT):
        text = content.decode("utf-8", errors="ignore")
    else:
        try:
            text = await _delegate_to_doc_processor(content, file.filename or "upload")
        except RuntimeError as e:
            raise HTTPException(status_code=502, detail=f"doc_processor_failed: {e}")

    # Off the event loop: some of SecurityScanner's DLP patterns (DOTALL private-key
    # blocks, the credit-card catch-all) are backtracking-prone, and this is a
    # WEB_CONCURRENCY=1 deployment — a multi-second scan on a large document would
    # otherwise hold up every other in-flight request.
    from src.services.security import SecurityScanner
    text = await asyncio.to_thread(SecurityScanner.redact_text, text)

    doc_id = str(uuid.uuid4())
    # Store the extracted text in full: hybrid_retrieval.chunk_text() splits documents
    # into passages at index time, so a whole document is the correct unit to persist
    # and a character cap would silently discard the tail of long documents.
    docs_df = pd.DataFrame([{
        "doc_id": doc_id, "title": file.filename, "content": text,
        "source": category, "embedding": "",
    }])
    await asyncio.to_thread(store_knowledge_docs, docs_df, owner_user_id=owner)
    # Index into the vector store immediately — without this the doc lives in
    # Postgres but is invisible to dense retrieval until the next full reindex
    # (same divergence the webhook and sandbox ingest paths already avoid).
    try:
        from src.services.vector_store import get_vector_store
        vs = get_vector_store()
        if vs:
            await asyncio.to_thread(vs.upsert, [{"doc_id": doc_id, "title": file.filename,
                                                 "content": text[:4000], "source": category,
                                                 "category": "", "owner_user_id": owner}])
    except Exception as e:
        log.warning("document ingest vector upsert failed for %s: %s", doc_id, e)
    await asyncio.to_thread(log_audit_event, user.username, "DOC_INGEST", f"Uploaded {file.filename}")
    return {
        "status": "ingested", "doc_id": doc_id, "filename": file.filename, "chars": len(text),
        "scope": "global" if global_scope else "user",
    }


@app.post("/api/v1/ingest/audio")
async def ingest_audio(
    file: UploadFile = File(...),
    category: str = Form("Misc"),
    analysis_type: str = Form("meeting"),
    global_scope: bool = Form(False),
    user: TokenData = Depends(get_current_user),
):
    """Audio → knowledge base, via a pluggable external audio processor —
    IntelAI's ingestion pipeline calling out to any tool that can make audio
    processing for its audio data, the same generic shape as
    _delegate_to_doc_processor() above for documents. Not hardcoded to
    VoiceFlow: AUDIO_PROCESSOR_URL is any base URL implementing
    POST {url}/pipeline (multipart `file` in, {"transcript", "analysis"} JSON
    out) — VoiceFlow speaks this contract natively, but so could anything
    else. 501 if AUDIO_PROCESSOR_URL isn't configured — never a fake
    transcript."""
    if global_scope and (user.role or "").lower() != "admin":
        raise HTTPException(status_code=403, detail="global_scope requires an admin role")
    owner = None if global_scope else user.user_id
    if not settings.AUDIO_PROCESSOR_URL:
        raise HTTPException(
            status_code=501,
            detail="AUDIO_PROCESSOR_URL not configured — set it to a running audio "
                   "processor (e.g. a VoiceFlow instance) to enable audio ingestion.",
        )
    from src.services.pg_store import store_knowledge_docs, log_audit_event
    from src.services.security import SecurityScanner

    content = await file.read()
    try:
        import httpx
        headers = {}
        if settings.AUDIO_PROCESSOR_TOKEN:
            headers["Authorization"] = f"Bearer {settings.AUDIO_PROCESSOR_TOKEN}"
        # Be explicit about the transcription engine rather than inheriting the
        # processor's own default — VoiceFlow's /pipeline defaults to LOCAL_WHISPERX,
        # which needs whisperx + a GPU on *its* host and is the wrong choice for a
        # small cloud instance. AUDIO_PROCESSOR_PROVIDER is passed straight through,
        # so it's whatever engine names your processor understands (VoiceFlow:
        # groq | deepgram | assemblyai | remote | local).
        data = {"analysis_type": analysis_type}
        provider = _os.environ.get("AUDIO_PROCESSOR_PROVIDER", "").strip()
        if provider:
            data["provider"] = provider
        timeout = _env_number("AUDIO_PROCESSOR_TIMEOUT", 300.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(
                f"{settings.AUDIO_PROCESSOR_URL}/pipeline",
                files={"file": (file.filename or "audio", content)},
                data=data,
                headers=headers,
            )
            resp.raise_for_status()
            result = resp.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"audio_processor_failed: {e}")

    transcript = result.get("transcript", {})
    analysis = result.get("analysis", {})
    transcript_text = transcript.get("text", "") if isinstance(transcript, dict) else str(transcript)
    if not transcript_text.strip():
        raise HTTPException(status_code=502, detail="audio_processor_returned_no_transcript")

    text = await asyncio.to_thread(SecurityScanner.redact_text, transcript_text)
    summary_fields = "\n".join(f"{k}: {v}" for k, v in analysis.items() if v not in (None, "", [], {})) if isinstance(analysis, dict) else ""
    full_content = f"{text}\n\n[ANALYSIS]\n{summary_fields}" if summary_fields else text

    doc_id = str(uuid.uuid4())
    docs_df = pd.DataFrame([{
        # Full transcript — see the note on document ingestion above; a long recording's
        # transcript is chunked at index time, not truncated at write time.
        "doc_id": doc_id, "title": file.filename or "audio upload", "content": full_content,
        "source": category, "embedding": "",
    }])
    await asyncio.to_thread(store_knowledge_docs, docs_df, owner_user_id=owner)
    # Same Postgres/vector divergence fix as /ingest/document above.
    try:
        from src.services.vector_store import get_vector_store
        vs = get_vector_store()
        if vs:
            await asyncio.to_thread(vs.upsert, [{"doc_id": doc_id, "title": file.filename or "audio upload",
                                                 "content": full_content[:4000], "source": category,
                                                 "category": "", "owner_user_id": owner}])
    except Exception as e:
        log.warning("audio ingest vector upsert failed for %s: %s", doc_id, e)
    await asyncio.to_thread(log_audit_event, user.username, "AUDIO_INGEST", f"Processed {file.filename} via {settings.AUDIO_PROCESSOR_URL}")
    return {
        "status": "ingested", "doc_id": doc_id, "filename": file.filename,
        "chars": len(text), "transcript": transcript, "analysis": analysis,
        "scope": "global" if global_scope else "user",
    }


# ════════════════════════════════════════════════════════════
_INTELAI_MEDIA_ROOT = _os.environ.get("INTELAI_MEDIA_DIR") or _os.environ.get("FILE_STORAGE_DIR") or "/data/intelai_media"
_INTELAI_S3 = None

def _intelai_s3():
    """S3-compatible store (Garage/MinIO/S3) when MEDIA_S3_* envs are set."""
    global _INTELAI_S3
    if _INTELAI_S3 is None:
        ep = _os.environ.get("MEDIA_S3_ENDPOINT", "").strip()
        if not ep:
            return None
        try:
            import boto3
            from botocore.client import Config
            _INTELAI_S3 = boto3.client("s3", endpoint_url=ep,
                aws_access_key_id=_os.environ.get("MEDIA_S3_ACCESS_KEY", ""),
                aws_secret_access_key=_os.environ.get("MEDIA_S3_SECRET_KEY", ""),
                region_name=_os.environ.get("MEDIA_S3_REGION", "garage"),
                config=Config(signature_version="s3v4"))
        except Exception as e:
            log.warning("S3 client init failed: %s", e)
            return None
    return _INTELAI_S3

def _store_upload(content: bytes, filename: Optional[str]) -> Optional[str]:
    """Persist an uploaded file for admin review under INTELAI_MEDIA_DIR.
    Returns path relative to the media root; never blocks the request."""
    if not content:
        return None
    try:
        import time, uuid
        fname = filename or "upload"
        ext = fname.rsplit(".", 1)
        ext = ("." + ext[1][:16]) if len(ext) == 2 and ext[1].replace("-", "").isalnum() else ""
        rel = f"{time.strftime('%Y/%m')}/{uuid.uuid4().hex}{ext}"
        s3 = _intelai_s3()
        if s3:
            s3.put_object(Bucket=_os.environ.get("MEDIA_S3_BUCKET", "oss-media"), Key=rel, Body=content)
            return rel
        dest = _os.path.join(_INTELAI_MEDIA_ROOT, rel)
        _os.makedirs(_os.path.dirname(dest), exist_ok=True)
        with open(dest, "wb") as f:
            f.write(content)
        return rel
    except Exception as e:
        log.warning("upload persistence failed: %s", e)
        return None


@app.get("/admin/media")
async def admin_media_list():
    """List persisted uploads for omni-admin review (internal-token gated)."""
    out = []
    s3 = _intelai_s3()
    if s3:
        try:
            import time as _t2
            paginator = s3.get_paginator("list_objects_v2")
            for page in paginator.paginate(Bucket=_os.environ.get("MEDIA_S3_BUCKET", "oss-media")):
                for obj in page.get("Contents", []):
                    out.append({"path": obj["Key"], "size": obj["Size"], "modified": obj["LastModified"].timestamp()})
            out.sort(key=lambda x: x["modified"], reverse=True)
            return {"files": out[:500]}
        except Exception:
            pass
    try:
        for dirpath, _dirs, files in _os.walk(_INTELAI_MEDIA_ROOT):
            for fn in files:
                p = _os.path.join(dirpath, fn)
                rel = _os.path.relpath(p, _INTELAI_MEDIA_ROOT)
                out.append({"path": rel, "size": _os.path.getsize(p),
                            "modified": _os.path.getmtime(p)})
        out.sort(key=lambda x: x["modified"], reverse=True)
    except Exception:
        pass
    return {"files": out[:500]}


@app.get("/admin/media/{media_path:path}")
async def admin_media_file(media_path: str):
    """Stream a persisted upload. Path traversal guarded; internal-token gated."""
    import mimetypes
    s3 = _intelai_s3()
    if s3:
        try:
            obj = s3.get_object(Bucket=_os.environ.get("MEDIA_S3_BUCKET", "oss-media"), Key=media_path)
            body = obj["Body"].read()
            ctype = obj.get("ContentType") or mimetypes.guess_type(media_path)[0] or "application/octet-stream"
            return Response(content=body, media_type=ctype)
        except Exception:
            raise HTTPException(status_code=404, detail="media_not_found")
    norm = _os.path.normpath(_os.path.join(_INTELAI_MEDIA_ROOT, media_path))
    root = _os.path.normpath(_INTELAI_MEDIA_ROOT)
    if not norm.startswith(root + _os.sep) or not _os.path.isfile(norm):
        raise HTTPException(status_code=404, detail="media_not_found")
    ctype = mimetypes.guess_type(norm)[0] or "application/octet-stream"
    return FileResponse(norm, media_type=ctype, filename=_os.path.basename(norm))


# PERSONAL DATA SANDBOX — scoped visitor workspaces
# ════════════════════════════════════════════════════════════

class SandboxSessionResponse(BaseModel):
    session_id: str
    token: str
    token_type: str = "bearer"
    expires_at: str
    quota: Dict[str, Any]


def _sandbox_session_or_404(session_id: str) -> Dict[str, Any]:
    from src.services import sandbox as sbx
    session = sbx.get_session(session_id)
    if not session or sbx.is_wiped_or_expired(session):
        raise HTTPException(status_code=404, detail="sandbox_not_found_or_expired")
    return session


@app.post("/api/v1/sandbox/session", response_model=SandboxSessionResponse)
async def sandbox_create_session(request: Request):
    """Create a personal sandbox — a demo-scoped owner plus quota registry.
    Public but IP-rate-limited; returns a viewer-scoped JWT that can only reach
    sandbox routes and the chat sandbox_session field."""
    from src.services import sandbox as sbx
    from src.services.pg_store import _demo_session_scoping_enabled
    if not _demo_session_scoping_enabled():
        raise HTTPException(status_code=503, detail="sandbox_requires_demo_scoping")
    client_ip = request.client.host if request.client else None
    # Per-IP throttle: count sessions created from this ip_hash in 24h.
    sbx._ensure_schema()
    from src.services.pg_store import _get_conn
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) AS c FROM sandbox_sessions WHERE ip_hash = %s AND created_at > now() - interval '1 day'",
                [sbx.hash_ip(client_ip)],
            )
            row = cur.fetchone() or {}
            if int(row.get("c", row.get("count", 0)) if isinstance(row, dict) else (row[0] if row else 0)) >= 5:
                raise HTTPException(status_code=429, detail="sandbox_rate_limited")
    finally:
        conn.close()
    result = sbx.create_session(ip=client_ip, user_agent=request.headers.get("user-agent"))
    return SandboxSessionResponse(**{k: result[k] for k in ("session_id", "token", "token_type", "expires_at", "quota")})


@app.get("/api/v1/sandbox/session")
async def sandbox_get_session(x_sandbox_session: Optional[str] = Header(default=None, alias="X-Sandbox-Session")):
    from src.services import sandbox as sbx
    if not x_sandbox_session:
        raise HTTPException(status_code=401, detail="X-Sandbox-Session header required")
    session = _sandbox_session_or_404(x_sandbox_session)
    docs = await asyncio.to_thread(sbx.list_docs, session["owner_user_id"])
    return {"session": {k: str(v) if hasattr(v, "isoformat") else v for k, v in session.items() if k != "owner_user_id"},
            "quota": sbx.quota_status(session), "docs": docs}


@app.post("/api/v1/sandbox/ingest")
async def sandbox_ingest(
    request: Request,
    file: UploadFile = File(...),
    x_sandbox_session: Optional[str] = Header(default=None, alias="X-Sandbox-Session"),
):
    """Upload one file into the sandbox. Same extraction pipeline as
    /ingest/document (plain-text decode or DocIntel delegation) plus audio via
    AUDIO_PROCESSOR_URL; quota + rate limits enforced per session."""
    from src.services import sandbox as sbx
    from src.services.pg_store import store_knowledge_docs, log_audit_event
    if not x_sandbox_session:
        raise HTTPException(status_code=401, detail="X-Sandbox-Session header required")
    session = _sandbox_session_or_404(x_sandbox_session)
    content = await file.read()
    filename = file.filename or "upload"
    media_path = _store_upload(content, filename)
    kind = sbx.classify_filename(filename)
    if kind == "unsupported":
        raise HTTPException(status_code=415, detail="unsupported_file_type")

    err = sbx.check_quota(session, len(content), kind)
    if err == "quota_docs_exceeded":
        raise HTTPException(status_code=429, detail="quota_docs_exceeded")
    if err == "quota_bytes_exceeded" or err == "quota_media_bytes_exceeded":
        raise HTTPException(status_code=429, detail=err)
    if err == "rate_limited":
        raise HTTPException(status_code=429, detail="rate_limited")

    job_id = sbx.create_job(x_sandbox_session, filename, kind)
    if media_path:
        try:
            sbx.attach_media_path(job_id, media_path)
        except Exception:
            pass
    owner = session["owner_user_id"]

    async def _run():
        try:
            if kind == "audio":
                text = await _sandbox_audio_text(content, filename)
            elif kind in ("text",):
                text = content.decode("utf-8", errors="ignore")
            else:  # document | image
                if not settings.DOC_PROCESSOR_URL:
                    sbx.finish_job(job_id, "failed", error="doc_processor_not_configured")
                    return
                text = await _delegate_to_doc_processor(content, filename)
            from src.services.security import SecurityScanner
            text = await asyncio.to_thread(SecurityScanner.redact_text, text)
            if not text.strip():
                sbx.finish_job(job_id, "failed", error="empty_extraction")
                return
            doc_id = str(uuid.uuid4())
            docs_df = pd.DataFrame([{
                "doc_id": doc_id, "title": filename, "content": text,
                "source": "sandbox", "embedding": "",
            }])
            await asyncio.to_thread(store_knowledge_docs, docs_df, owner_user_id=owner)
            # Index into the vector store immediately — without this the doc is in
            # Postgres but invisible to dense retrieval (same pattern as the webhook path).
            try:
                from src.services.vector_store import get_vector_store
                vs = get_vector_store()
                if vs:
                    await asyncio.to_thread(vs.upsert, [{"doc_id": doc_id, "title": filename,
                                                         "content": text[:4000], "source": "sandbox",
                                                         "category": "", "owner_user_id": owner}])
            except Exception as e:
                log.warning("sandbox ingest vector upsert failed for %s: %s", job_id, e)
            await asyncio.to_thread(log_audit_event, f"sandbox:{x_sandbox_session[-6:]}", "SANDBOX_INGEST", f"{filename} ({kind})")
            sbx.bump_usage(x_sandbox_session, docs=1,
                           text_bytes=len(text.encode()) if kind == "text" else 0,
                           media_bytes=len(content) if kind != "text" else 0)
            sbx.finish_job(job_id, "done", chunks=1)
        except HTTPException as e:
            sbx.finish_job(job_id, "failed", error=str(e.detail)[:300])
        except Exception as e:
            log.warning("sandbox ingest job %s failed: %s", job_id, e)
            sbx.finish_job(job_id, "failed", error=str(e)[:300])

    asyncio.create_task(_run())
    return {"status": "queued", "job_id": job_id, "kind": kind}


async def _sandbox_audio_text(content: bytes, filename: str) -> str:
    """Audio → transcript via the same AUDIO_PROCESSOR_URL contract as /ingest/audio."""
    if not settings.AUDIO_PROCESSOR_URL:
        raise HTTPException(status_code=501, detail="audio_processor_not_configured")
    import httpx
    from src.services.security import SecurityScanner
    headers = {}
    token = getattr(settings, "AUDIO_PROCESSOR_TOKEN", "") or ""
    if token:
        headers["X-Internal-Token"] = token
    async with httpx.AsyncClient(timeout=300) as client:
        resp = await client.post(
            f"{settings.AUDIO_PROCESSOR_URL}/pipeline",
            files={"file": (filename, content)},
            data={"analysis_type": "general"},
            headers=headers,
        )
        resp.raise_for_status()
        result = resp.json()
    transcript = result.get("transcript", {})
    text = transcript.get("text", "") if isinstance(transcript, dict) else str(transcript)
    if not text.strip():
        raise HTTPException(status_code=502, detail="audio_processor_returned_no_transcript")
    return await asyncio.to_thread(SecurityScanner.redact_text, text)


@app.get("/api/v1/sandbox/ingest/{job_id}")
async def sandbox_ingest_status(job_id: str, x_sandbox_session: Optional[str] = Header(default=None, alias="X-Sandbox-Session")):
    from src.services import sandbox as sbx
    if not x_sandbox_session:
        raise HTTPException(status_code=401, detail="X-Sandbox-Session header required")
    _sandbox_session_or_404(x_sandbox_session)
    job = sbx.get_job(job_id, x_sandbox_session)
    if not job:
        raise HTTPException(status_code=404, detail="job_not_found")
    return {k: str(v) if hasattr(v, "isoformat") else v for k, v in job.items()}


@app.delete("/api/v1/sandbox/session")
async def sandbox_wipe(x_sandbox_session: Optional[str] = Header(default=None, alias="X-Sandbox-Session")):
    """Wipe everything the sandbox owns — knowledge rows, vectors, jobs. Idempotent."""
    from src.services import sandbox as sbx
    if not x_sandbox_session:
        raise HTTPException(status_code=401, detail="X-Sandbox-Session header required")
    session = _sandbox_session_or_404(x_sandbox_session)
    result = await asyncio.to_thread(sbx.wipe_session, session)
    return {"status": "wiped", **result}


@app.get("/api/v1/sandbox/docs/{doc_id}/entities")
async def sandbox_doc_entities(doc_id: str, x_sandbox_session: Optional[str] = Header(default=None, alias="X-Sandbox-Session")):
    from src.services import sandbox as sbx
    if not x_sandbox_session:
        raise HTTPException(status_code=401, detail="X-Sandbox-Session header required")
    session = _sandbox_session_or_404(x_sandbox_session)
    entities = await asyncio.to_thread(sbx.doc_entities, session["owner_user_id"], doc_id)
    return {"doc_id": doc_id, "entities": entities}


@app.get("/api/v1/sandbox/docs")
async def sandbox_list_docs(x_sandbox_session: Optional[str] = Header(default=None, alias="X-Sandbox-Session")):
    from src.services import sandbox as sbx
    if not x_sandbox_session:
        raise HTTPException(status_code=401, detail="X-Sandbox-Session header required")
    session = _sandbox_session_or_404(x_sandbox_session)
    docs = await asyncio.to_thread(sbx.list_docs, session["owner_user_id"])
    return {"docs": [{k: str(v) if hasattr(v, "isoformat") else v for k, v in d.items()} for d in docs]}


# ── Admin visibility ──────────────────────────────────────────

@app.get("/api/v1/admin/sandboxes")
async def admin_list_sandboxes(user: TokenData = Depends(require_role("admin"))):
    from src.services import sandbox as sbx
    sbx._ensure_schema()
    from src.services.pg_store import _get_conn
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT id, owner_user_id, created_at, expires_at, wiped_at, docs_count, bytes_used, media_bytes, ip_hash
                   FROM sandbox_sessions ORDER BY created_at DESC LIMIT 200"""
            )
            cols = ["id", "owner_user_id", "created_at", "expires_at", "wiped_at", "docs_count",
                    "bytes_used", "media_bytes", "ip_hash"]
            rows = [r if isinstance(r, dict) else dict(zip(cols, r)) for r in cur.fetchall()]
            cur.execute(
                """SELECT COUNT(*) FILTER (WHERE wiped_at IS NULL AND expires_at > now()) AS active,
                          COUNT(*) AS total, COALESCE(SUM(docs_count),0) AS docs, COALESCE(SUM(bytes_used),0) AS bytes
                   FROM sandbox_sessions"""
            )
            stats = cur.fetchone() or {}
    finally:
        conn.close()
    for r in rows:
        for k, v in list(r.items()):
            r[k] = str(v) if hasattr(v, "isoformat") else v
    return {"stats": stats, "sessions": rows}


@app.get("/api/v1/admin/sandboxes/{session_id}")
async def admin_sandbox_detail(session_id: str, user: TokenData = Depends(require_role("admin"))):
    from src.services import sandbox as sbx
    from src.services.pg_store import log_audit_event
    session = sbx.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="sandbox_not_found")
    await asyncio.to_thread(log_audit_event, user.username, "SANDBOX_ADMIN_VIEW", f"session {session_id}")
    docs = await asyncio.to_thread(sbx.list_docs, session["owner_user_id"])
    jobs = sbx._ensure_schema() or None
    from src.services.pg_store import _get_conn
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT id, filename, media_type, status, chunks_written, error, created_at, finished_at
                   FROM sandbox_ingest_jobs WHERE session_id = %s ORDER BY created_at DESC LIMIT 100""",
                [session_id],
            )
            jcols = ["id", "filename", "media_type", "status", "chunks_written", "error", "created_at", "finished_at"]
            job_rows = [r if isinstance(r, dict) else dict(zip(jcols, r)) for r in cur.fetchall()]
    finally:
        conn.close()
    for rows in (docs, job_rows):
        for r in rows:
            for k, v in list(r.items()):
                r[k] = str(v) if hasattr(v, "isoformat") else v
    return {"session": {k: str(v) if hasattr(v, "isoformat") else v for k, v in session.items()},
            "quota": sbx.quota_status(session), "docs": docs, "jobs": job_rows}


@app.get("/api/v1/admin/sandboxes/{session_id}/docs/{doc_id}/preview")
async def admin_sandbox_doc_preview(session_id: str, doc_id: str, user: TokenData = Depends(require_role("admin"))):
    """Admin preview of a sandbox doc's extracted text — audit-logged, capped."""
    from src.services import sandbox as sbx
    from src.services.pg_store import _get_conn, log_audit_event
    session = sbx.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="sandbox_not_found")
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT title, source, content FROM knowledge_base
                   WHERE doc_id = %s AND owner_user_id = %s""",
                [doc_id, session["owner_user_id"]],
            )
            row = cur.fetchone()
    finally:
        conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="doc_not_found")
    await asyncio.to_thread(log_audit_event, user.username, "SANDBOX_ADMIN_PREVIEW", f"{session_id}/{doc_id}")
    return {"doc_id": doc_id, "title": row[0], "source": row[1], "content": (row[2] or "")[:20000]}


# ════════════════════════════════════════════════════════════
# KPI QUERIES (Cross-Domain)
# ════════════════════════════════════════════════════════════

@app.get("/api/v1/kpis")
async def get_kpis(
    period: Optional[str] = None,
    category: Optional[str] = None,
    segment: Optional[str] = None,
    metric: Optional[str] = None,
    start_period: Optional[str] = None,
    end_period: Optional[str] = None,
    limit: Optional[int] = 10000,
    user: TokenData = Depends(get_current_user),
):
    from src.services.pg_store import get_kpi_metrics, get_available_categories
    periods = [period] if period else None
    metrics = [m.strip() for m in metric.split(",")] if metric else None
    categories = [category] if category else None
    segments = [segment] if segment else None
    df = await asyncio.to_thread(
        get_kpi_metrics,
        periods=periods,
        metrics=metrics,
        categories=categories,
        segments=segments,
        start_period=start_period,
        end_period=end_period,
        limit=limit,
    )

    # Filter by user's data access
    all_categories = await asyncio.to_thread(get_available_categories)
    user_categories = get_user_data_categories(user.role, all_categories)
    if "*" not in user_categories and "category" in df.columns and not df.empty:
        user_cat_lower = [c.lower() for c in user_categories]
        df = df[df["category"].str.lower().isin(user_cat_lower)]

    metrics_list = df.to_dict(orient="records") if not df.empty else []
    return {"metrics": metrics_list, "count": len(metrics_list)}


@app.get("/api/v1/kpis/periods")
async def get_kpi_periods(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_available_periods
    return {"periods": await asyncio.to_thread(get_available_periods)}


@app.get("/api/v1/kpis/metrics")
async def get_kpi_metric_names(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_available_metrics
    return {"metrics": await asyncio.to_thread(get_available_metrics)}


@app.get("/api/v1/kpis/categories")
async def get_kpi_categories(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_available_categories
    return {"categories": await asyncio.to_thread(get_available_categories)}


# ════════════════════════════════════════════════════════════
# FINANCIAL STATEMENTS
# ════════════════════════════════════════════════════════════

@app.post("/api/v1/financial/statement")
async def generate_financial_statement(
    req: FinancialRequest,
    user: TokenData = Depends(require_page("financial")),
):
    from src.services.financial import FinancialStatementEngine
    engine = FinancialStatementEngine()
    period = req.period
    if not period:
        from src.services.pg_store import get_latest_period
        period = await asyncio.to_thread(get_latest_period) or "2025-06"

    # _fetch_metrics() does an exact-string match against `period`; KPI periods are only
    # ever written as monthly "YYYY-MM" strings (get_latest_period, every ingestion path).
    # A period that matches nothing would otherwise produce an all-$0.00 statement with no
    # indication anything is wrong. Fail loudly so the user knows to pick a real period.
    from src.services.pg_store import get_available_periods
    available_periods = await asyncio.to_thread(get_available_periods)
    if available_periods and period not in available_periods:
        raise HTTPException(
            status_code=404,
            detail=f"No KPI data for period '{period}'. Available periods: {', '.join(sorted(available_periods)[-6:])}"
            + (" (showing latest 6)" if len(available_periods) > 6 else ""),
        )

    try:
        if req.statement_type in ("income_statement", "pl", "P&L", "profit_loss"):
            stmt = engine.create_pl_statement(period)
            margins = engine.analyze_margins(stmt)
            # Convert statement dict to line_items format for frontend
            line_items = [{"item_name": k, "name": k, "amount": v} for k, v in stmt.data.items()]
            return {"line_items": line_items, "margins": margins, "period": period, "statement_type": req.statement_type}
        elif req.statement_type in ("balance_sheet", "bs"):
            stmt = engine.create_balance_sheet(period)
            ratios = engine.analyze_ratios(stmt)
            line_items = [{"item_name": k, "name": k, "amount": v} for k, v in stmt.data.items()]
            return {"line_items": line_items, "ratios": ratios, "period": period, "statement_type": req.statement_type}
        elif req.statement_type in ("cash_flow", "cf"):
            stmt = engine.create_cash_flow_statement(period)
            line_items = [{"item_name": k, "name": k, "amount": v} for k, v in stmt.data.items()]
            return {"line_items": line_items, "period": period, "statement_type": req.statement_type}
        else:
            raise HTTPException(status_code=400, detail=f"Unknown statement type: {req.statement_type}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ════════════════════════════════════════════════════════════
# FORECASTING
# ════════════════════════════════════════════════════════════

async def _scope_kpi_df(df: "pd.DataFrame", user: TokenData) -> "pd.DataFrame":
    """Same role-scoping GET /api/v1/kpis already applies, factored out for the
    forecast/insights endpoints below — they called get_kpi_metrics() with no category
    filter at all, so any authenticated user got every domain's real values regardless
    of their data_access. Confirmed live: an hr-role token (data_access=[People])
    retrieved Finance anomalies (real revenue/EBITDA figures) and a composite risk
    score built from every domain via /api/v1/insights/anomalies and /insights/risk."""
    from src.services.pg_store import get_available_categories
    if df.empty or "category" not in df.columns:
        return df
    all_categories = await asyncio.to_thread(get_available_categories)
    user_categories = get_user_data_categories(user.role, all_categories)
    if "*" in user_categories:
        return df
    user_cat_lower = [c.lower() for c in user_categories]
    return df[df["category"].str.lower().isin(user_cat_lower)]


@app.post("/api/v1/forecast")
async def run_forecast(
    metric: str = Form(...),
    periods: int = Form(3),
    user: TokenData = Depends(get_current_user),
):
    from src.services.pg_store import get_kpi_metrics
    from src.services.forecasting import ForecastEngine

    target_metric = metric
    if target_metric:
        norm = target_metric.strip().lower()
        try:
            from src.services.tools import METRIC_SYNONYMS
            target_metric = METRIC_SYNONYMS.get(norm, target_metric)
        except Exception:
            pass

    df = await asyncio.to_thread(get_kpi_metrics, metrics=[target_metric])
    if df.empty and any(k in str(metric).lower() for k in ["cloud", "infra", "server"]):
        target_metric = "Capital Expenditure"
        df = await asyncio.to_thread(get_kpi_metrics, metrics=[target_metric])

    df = await _scope_kpi_df(df, user)
    if df.empty:
        return {"error": f"No data found for metric: {metric}", "forecast": []}

    forecast_df = df[["period", "value"]].rename(columns={"period": "month_tag", "value": "actual"})
    forecast_df = forecast_df.groupby("month_tag").agg({"actual": "mean"}).reset_index()
    forecast_df = forecast_df.sort_values("month_tag")

    # Some real metrics (e.g. a one-time survey stat like Attrition Rate, seeded from a
    # single CSV snapshot rather than a recurring monthly series) genuinely have too few
    # distinct periods to fit any trend. ForecastEngine already guards this (returns an
    # empty forecast / zeroed explanation rather than crashing), but returning that
    # silently reads as "the forecast is 0%", not "there isn't enough data to forecast".
    # Flag it explicitly instead.
    if len(forecast_df) < 2:
        return {
            "metric": metric,
            "historical": forecast_df.to_dict(orient="records"),
            "forecast": [],
            "explanation": None,
            "insufficient_data": True,
            "message": f"'{metric}' has only {len(forecast_df)} historical period(s) — at least 2 "
                       f"are needed to forecast a trend.",
        }

    try:
        engine = ForecastEngine()
        result = engine.time_series_forecast(forecast_df, periods=periods)
        explanation = engine.explain_forecast(forecast_df)
        return {
            "metric": metric,
            "historical": forecast_df.to_dict(orient="records"),
            "forecast": result.to_dict(orient="records") if not result.empty else [],
            "explanation": explanation,
        }
    except Exception as e:
        return {"error": str(e), "metric": metric, "forecast": []}


# ════════════════════════════════════════════════════════════
# INSIGHTS & RISK
# ════════════════════════════════════════════════════════════

@app.get("/api/v1/insights/health")
async def get_health_index(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    from src.services.insights import compute_health_index
    df = await asyncio.to_thread(get_kpi_metrics)
    df = await _scope_kpi_df(df, user)
    return _json_safe(compute_health_index(df))


@app.get("/api/v1/insights/risk")
async def get_risk_score(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    from src.services.insights import compute_risk_score
    df = await asyncio.to_thread(get_kpi_metrics)
    df = await _scope_kpi_df(df, user)
    return _json_safe(compute_risk_score(df))


@app.get("/api/v1/insights/summary")
async def get_executive_summary(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    from src.services.insights import compute_health_index, compute_risk_score, extract_key_metrics, build_executive_summary
    df = await asyncio.to_thread(get_kpi_metrics)
    df = await _scope_kpi_df(df, user)
    health = compute_health_index(df)
    risk = compute_risk_score(df)
    key_metrics = extract_key_metrics(df)
    summary = build_executive_summary(df, health, risk, key_metrics)
    return _json_safe({
        "health": health,
        "risk": risk,
        "key_metrics": key_metrics,
        "summary": " ".join(summary) if isinstance(summary, list) else summary,
    })


@app.get("/api/v1/insights/anomalies")
async def get_anomalies(
    metric: Optional[str] = None,
    user: TokenData = Depends(get_current_user),
):
    from src.services.pg_store import get_kpi_metrics
    from src.services.insights import detect_anomalies
    metrics_filter = [metric] if metric else None
    df = await asyncio.to_thread(get_kpi_metrics, metrics=metrics_filter)
    df = await _scope_kpi_df(df, user)
    anomalies = detect_anomalies(df)
    if anomalies.empty:
        return {"anomalies": [], "count": 0}
    anom_df = anomalies[anomalies["is_anomaly"] == True]
    return {
        "anomalies": anom_df.to_dict(orient="records") if not anom_df.empty else [],
        "count": len(anom_df),
    }


# ════════════════════════════════════════════════════════════
# HR / PEOPLE DOMAIN
# ════════════════════════════════════════════════════════════

def _domain_df_call(
    period: Optional[str] = None,
    start_period: Optional[str] = None,
    end_period: Optional[str] = None,
    category: Optional[str] = None,
):
    from src.services.pg_store import get_kpi_metrics
    kw: Dict[str, Any] = {}
    if category:
        kw["categories"] = [category]
    if period:
        kw["end_period"] = period
    elif end_period:
        kw["end_period"] = end_period
    if start_period:
        kw["start_period"] = start_period
    return get_kpi_metrics(**kw)


@app.get("/api/v1/hr/summary")
async def get_hr_summary(
    period: Optional[str] = None,
    start_period: Optional[str] = None,
    end_period: Optional[str] = None,
    user: TokenData = Depends(require_page("hr")),
):
    from src.services.hr import HRService
    df = await asyncio.to_thread(_domain_df_call, period=period, start_period=start_period, end_period=end_period, category="People")
    return HRService().get_workforce_summary(df)

@app.get("/api/v1/hr/departments")
async def get_hr_departments(
    period: Optional[str] = None,
    start_period: Optional[str] = None,
    end_period: Optional[str] = None,
    user: TokenData = Depends(require_page("hr")),
):
    from src.services.hr import HRService
    df = await asyncio.to_thread(_domain_df_call, period=period, start_period=start_period, end_period=end_period, category="People")
    return {"departments": HRService().get_department_analytics(df)}

@app.get("/api/v1/hr/recruitment")
async def get_hr_recruitment(
    period: Optional[str] = None,
    start_period: Optional[str] = None,
    end_period: Optional[str] = None,
    user: TokenData = Depends(require_page("hr")),
):
    from src.services.hr import HRService
    df = await asyncio.to_thread(_domain_df_call, period=period, start_period=start_period, end_period=end_period, category="People")
    return HRService().get_recruitment_pipeline(df)

@app.get("/api/v1/hr/training")
async def get_hr_training(
    period: Optional[str] = None,
    start_period: Optional[str] = None,
    end_period: Optional[str] = None,
    user: TokenData = Depends(require_page("hr")),
):
    from src.services.hr import HRService
    df = await asyncio.to_thread(_domain_df_call, period=period, start_period=start_period, end_period=end_period, category="People")
    return HRService().get_training_overview(df)

@app.get("/api/v1/hr/health")
async def get_hr_health(
    period: Optional[str] = None,
    start_period: Optional[str] = None,
    end_period: Optional[str] = None,
    user: TokenData = Depends(require_page("hr")),
):
    from src.services.hr import HRService
    df = await asyncio.to_thread(_domain_df_call, period=period, start_period=start_period, end_period=end_period, category="People")
    return HRService().compute_hr_health_score(df)


# ════════════════════════════════════════════════════════════
# LOGISTICS DOMAIN
# ════════════════════════════════════════════════════════════

@app.get("/api/v1/logistics/summary")
async def get_logistics_summary(
    period: Optional[str] = None,
    start_period: Optional[str] = None,
    end_period: Optional[str] = None,
    user: TokenData = Depends(require_page("logistics")),
):
    from src.services.logistics import LogisticsService
    df = await asyncio.to_thread(_domain_df_call, period=period, start_period=start_period, end_period=end_period, category="Logistics")
    return LogisticsService().get_supply_chain_summary(df)

@app.get("/api/v1/logistics/inventory")
async def get_logistics_inventory(
    period: Optional[str] = None,
    start_period: Optional[str] = None,
    end_period: Optional[str] = None,
    user: TokenData = Depends(require_page("logistics")),
):
    from src.services.logistics import LogisticsService
    df = await asyncio.to_thread(_domain_df_call, period=period, start_period=start_period, end_period=end_period, category="Logistics")
    return LogisticsService().get_inventory_status(df)

@app.get("/api/v1/logistics/shipping")
async def get_logistics_shipping(
    period: Optional[str] = None,
    start_period: Optional[str] = None,
    end_period: Optional[str] = None,
    user: TokenData = Depends(require_page("logistics")),
):
    from src.services.logistics import LogisticsService
    df = await asyncio.to_thread(_domain_df_call, period=period, start_period=start_period, end_period=end_period, category="Logistics")
    return LogisticsService().get_shipping_analytics(df)

@app.get("/api/v1/logistics/suppliers")
async def get_logistics_suppliers(
    period: Optional[str] = None,
    start_period: Optional[str] = None,
    end_period: Optional[str] = None,
    user: TokenData = Depends(require_page("logistics")),
):
    from src.services.logistics import LogisticsService
    df = await asyncio.to_thread(_domain_df_call, period=period, start_period=start_period, end_period=end_period, category="Logistics")
    return {"suppliers": LogisticsService().get_supplier_metrics(df)}

@app.get("/api/v1/logistics/health")
async def get_logistics_health(
    period: Optional[str] = None,
    start_period: Optional[str] = None,
    end_period: Optional[str] = None,
    user: TokenData = Depends(require_page("logistics")),
):
    from src.services.logistics import LogisticsService
    df = await asyncio.to_thread(_domain_df_call, period=period, start_period=start_period, end_period=end_period, category="Logistics")
    return LogisticsService().compute_logistics_health(df)


# ════════════════════════════════════════════════════════════
# IT OPERATIONS DOMAIN
# ════════════════════════════════════════════════════════════

@app.get("/api/v1/it/overview")
async def get_it_overview(
    period: Optional[str] = None,
    start_period: Optional[str] = None,
    end_period: Optional[str] = None,
    user: TokenData = Depends(require_page("it")),
):
    from src.services.it_ops import ITOpsService
    df = await asyncio.to_thread(_domain_df_call, period=period, start_period=start_period, end_period=end_period, category="IT")
    return ITOpsService().get_it_overview(df)

@app.get("/api/v1/it/tickets")
async def get_it_tickets(
    period: Optional[str] = None,
    start_period: Optional[str] = None,
    end_period: Optional[str] = None,
    user: TokenData = Depends(require_page("it")),
):
    from src.services.it_ops import ITOpsService
    df = await asyncio.to_thread(_domain_df_call, period=period, start_period=start_period, end_period=end_period, category="IT")
    return ITOpsService().get_ticket_analytics(df)

@app.get("/api/v1/it/security")
async def get_it_security(
    period: Optional[str] = None,
    start_period: Optional[str] = None,
    end_period: Optional[str] = None,
    user: TokenData = Depends(require_page("it")),
):
    from src.services.it_ops import ITOpsService
    df = await asyncio.to_thread(_domain_df_call, period=period, start_period=start_period, end_period=end_period, category="IT")
    return ITOpsService().get_security_dashboard(df)

@app.get("/api/v1/it/infrastructure")
async def get_it_infrastructure(
    period: Optional[str] = None,
    start_period: Optional[str] = None,
    end_period: Optional[str] = None,
    user: TokenData = Depends(require_page("it")),
):
    from src.services.it_ops import ITOpsService
    df = await asyncio.to_thread(_domain_df_call, period=period, start_period=start_period, end_period=end_period, category="IT")
    return ITOpsService().get_infrastructure_metrics(df)

@app.get("/api/v1/it/devops")
async def get_it_devops(
    period: Optional[str] = None,
    start_period: Optional[str] = None,
    end_period: Optional[str] = None,
    user: TokenData = Depends(require_page("it")),
):
    from src.services.it_ops import ITOpsService
    df = await asyncio.to_thread(_domain_df_call, period=period, start_period=start_period, end_period=end_period, category="IT")
    return ITOpsService().get_devops_metrics(df)

@app.get("/api/v1/it/health")
async def get_it_health(
    period: Optional[str] = None,
    start_period: Optional[str] = None,
    end_period: Optional[str] = None,
    user: TokenData = Depends(require_page("it")),
):
    from src.services.it_ops import ITOpsService
    df = await asyncio.to_thread(_domain_df_call, period=period, start_period=start_period, end_period=end_period, category="IT")
    return ITOpsService().compute_it_health(df)


# ════════════════════════════════════════════════════════════
# OPERATIONS DOMAIN
# ════════════════════════════════════════════════════════════

@app.get("/api/v1/operations/summary")
async def get_ops_summary(
    period: Optional[str] = None,
    start_period: Optional[str] = None,
    end_period: Optional[str] = None,
    user: TokenData = Depends(require_page("operations")),
):
    from src.services.operations import OperationsService
    df = await asyncio.to_thread(_domain_df_call, period=period, start_period=start_period, end_period=end_period, category="Operations")
    return OperationsService().get_operations_summary(df)

@app.get("/api/v1/operations/quality")
async def get_ops_quality(
    period: Optional[str] = None,
    start_period: Optional[str] = None,
    end_period: Optional[str] = None,
    user: TokenData = Depends(require_page("operations")),
):
    from src.services.operations import OperationsService
    df = await asyncio.to_thread(_domain_df_call, period=period, start_period=start_period, end_period=end_period, category="Operations")
    return OperationsService().get_quality_metrics(df)

@app.get("/api/v1/operations/production")
async def get_ops_production(
    period: Optional[str] = None,
    start_period: Optional[str] = None,
    end_period: Optional[str] = None,
    user: TokenData = Depends(require_page("operations")),
):
    from src.services.operations import OperationsService
    df = await asyncio.to_thread(_domain_df_call, period=period, start_period=start_period, end_period=end_period, category="Operations")
    return OperationsService().get_production_metrics(df)

@app.get("/api/v1/operations/safety")
async def get_ops_safety(
    period: Optional[str] = None,
    start_period: Optional[str] = None,
    end_period: Optional[str] = None,
    user: TokenData = Depends(require_page("operations")),
):
    from src.services.operations import OperationsService
    df = await asyncio.to_thread(_domain_df_call, period=period, start_period=start_period, end_period=end_period, category="Operations")
    return OperationsService().get_safety_metrics(df)

@app.get("/api/v1/operations/health")
async def get_ops_health(
    period: Optional[str] = None,
    start_period: Optional[str] = None,
    end_period: Optional[str] = None,
    user: TokenData = Depends(require_page("operations")),
):
    from src.services.operations import OperationsService
    df = await asyncio.to_thread(_domain_df_call, period=period, start_period=start_period, end_period=end_period, category="Operations")
    return OperationsService().compute_ops_health(df)


# ════════════════════════════════════════════════════════════
# GROWTH DOMAIN
# ════════════════════════════════════════════════════════════

@app.get("/api/v1/growth/summary")
async def get_growth_summary(
    period: Optional[str] = None,
    start_period: Optional[str] = None,
    end_period: Optional[str] = None,
    user: TokenData = Depends(require_page("analytics")),
):
    df = await asyncio.to_thread(_domain_df_call, period=period, start_period=start_period, end_period=end_period, category="Growth")
    if df.empty:
        return {"mrr": 0, "arr": 0, "cac": 0, "ltv": 0, "churn_rate": 0, "trends": [], "mrr_trend": 0, "cac_trend": 0, "churn_trend": 0}

    # Sort and grab latest
    df = df.sort_values(by="period")
    latest = df.drop_duplicates(subset=["metric"], keep="last")

    def _val(metric_name):
        row = latest[latest["metric"] == metric_name]
        return float(row["value"].iloc[0]) if not row.empty else 0

    def _trend(metric_name):
        m_df = df[df["metric"] == metric_name]
        if len(m_df) < 2: return 0
        v1 = m_df.iloc[-2]["value"]
        v2 = m_df.iloc[-1]["value"]
        return ((v2 - v1) / v1 * 100) if v1 else 0

    mrr_series = df[df["metric"] == "MRR"][["period", "value"]].tail(12).to_dict("records")

    return {
        "mrr": _val("MRR"),
        "arr": _val("ARR"),
        "cac": _val("CAC"),
        "ltv": _val("LTV"),
        "churn_rate": _val("Churn Rate"),
        "trends": mrr_series,
        "mrr_trend": _trend("MRR"),
        "cac_trend": _trend("CAC"),
        "churn_trend": _trend("Churn Rate")
    }


# ════════════════════════════════════════════════════════════
# ESG DOMAIN
# ════════════════════════════════════════════════════════════

@app.get("/api/v1/esg/summary")
async def get_esg_summary(
    period: Optional[str] = None,
    start_period: Optional[str] = None,
    end_period: Optional[str] = None,
    user: TokenData = Depends(require_page("esg")),
):
    df = await asyncio.to_thread(_domain_df_call, period=period, start_period=start_period, end_period=end_period, category="ESG")
    if df.empty:
        return {"score": 0, "environment": {}, "social": {}, "governance": {}, "trends": []}

    latest = df.sort_values("period").groupby("metric").tail(1)

    def _val(keywords):
        mask = latest["metric"].str.lower().apply(lambda m: any(k in m for k in keywords))
        matched = latest[mask]
        return float(matched.iloc[0]["value"]) if not matched.empty else 0

    # Build trends
    trends = []
    for period_val in sorted(df["period"].unique()):
        p_df = df[df["period"] == period_val]
        score_rows = p_df[p_df["metric"].str.lower().str.contains("esg score")]
        carbon_rows = p_df[p_df["metric"].str.lower().str.contains("carbon")]
        trends.append({
            "period": period_val,
            "score": float(score_rows.iloc[0]["value"]) if not score_rows.empty else 0,
            "carbon": float(carbon_rows.iloc[0]["value"]) if not carbon_rows.empty else 0,
        })

    return {
        "score": _val(["esg score"]),
        "environment": {
            "carbon_emissions": _val(["carbon emissions"]),
            "renewable_energy_pct": _val(["renewables", "renewable"]),
            "water_usage": _val(["water usage", "water consumption"]),
            "waste_diverted": _val(["waste diverted", "waste recycled"]),
        },
        "social": {
            "community_investment": _val(["community investment"]),
            "diversity_index": _val(["diversity index", "diversity score"]),
            "gender_pay_gap": _val(["gender pay gap"]),
        },
        "governance": {
            "board_diversity": _val(["board diversity"]),
            "ethics_training": _val(["ethics training"]),
            "supplier_compliance": _val(["supplier esg", "supplier compliance"]),
            "data_privacy_incidents": int(_val(["data privacy"])),
        },
        "trends": trends,
    }


# ════════════════════════════════════════════════════════════
# PERSONA TOOLS (whitelisted + RBAC-enforced)
# ════════════════════════════════════════════════════════════

@app.get("/api/v1/agent/tools")
async def agent_list_tools(persona: Optional[str] = None, user: TokenData = Depends(get_current_user)):
    """List the tools a persona may invoke (its whitelist). Defaults to the persona for the
    caller's role, and only personas the role is allowed to use (RBAC)."""
    from src.services.omnismart_chatbot import get_persona_factory
    from src.services.tools import TOOLS, list_persona_tools
    factory = get_persona_factory()
    p = persona or factory.get_persona_for_role(user.role)
    if p not in factory.allowed_personas_for_role(user.role):
        raise HTTPException(status_code=403, detail=f"Persona '{p}' not allowed for your role")
    return {"persona": p, "allowed_tools": list_persona_tools(p), "implemented": sorted(TOOLS.keys())}


@app.post("/api/v1/agent/run")
async def agent_run_tool(req: AgentToolRequest, user: TokenData = Depends(get_current_user)):
    """Run a whitelisted tool for a persona. Enforces both RBAC (the role may use the persona)
    and the persona's tool whitelist (the tool must be in allowed_tools)."""
    from src.services.omnismart_chatbot import get_persona_factory
    from src.services.tools import run_tool
    factory = get_persona_factory()
    persona = req.persona or factory.get_persona_for_role(user.role)
    if persona not in factory.allowed_personas_for_role(user.role):
        raise HTTPException(status_code=403, detail=f"Persona '{persona}' not allowed for your role")
    result = await asyncio.to_thread(run_tool, persona, req.tool, req.args or {})
    return _json_safe(result)


# ════════════════════════════════════════════════════════════
# ADMIN ENDPOINTS
# ════════════════════════════════════════════════════════════

@app.get("/api/v1/admin/users")
async def list_users(user: TokenData = Depends(require_role("admin"))):
    # Postgres is authoritative when configured — _users_db only holds the
    # bootstrap defaults and would hide every user registered since startup.
    if _pg_users_enabled():
        try:
            from src.services.pg_store import list_users as _pg_list_users
            rows = await asyncio.to_thread(_pg_list_users)
            return {"users": [{
                "id": r.get("id"), "username": r.get("username"), "role": r.get("role"),
                "is_active": r.get("is_active", True),
                "language": r.get("preferred_language", "en"),
                "created_at": r.get("created_at"),
            } for r in rows]}
        except Exception as e:
            log.warning("PG list_users failed, falling back to in-memory: %s", e)
    result = []
    for username, data in _users_db.items():
        result.append({
            "id": data["id"], "username": data["username"], "role": data["role"],
            "is_active": data.get("is_active", True),
            "language": data.get("preferred_language", "en"),
            "created_at": data.get("created_at"),
        })
    return {"users": result}


@app.put("/api/v1/admin/users/{user_id}")
async def update_user(
    user_id: str, req: UserUpdateRequest,
    user: TokenData = Depends(require_role("admin")),
):
    # Postgres is authoritative when configured: resolve the target there first
    # (the in-memory dict only ever held bootstrap defaults), write the change to
    # Postgres, then mirror it into _users_db when the entry exists as a cache.
    if _pg_users_enabled():
        try:
            from src.services.pg_store import get_user_by_id, update_user as _pg_update_user
            target_row = await asyncio.to_thread(get_user_by_id, user_id)
            if not target_row:
                raise HTTPException(status_code=404, detail="User not found")
            await asyncio.to_thread(
                _pg_update_user, user_id,
                role=req.role, is_active=req.is_active, preferred_language=req.preferred_language,
            )
            cached = _users_db.get(target_row.get("username"))
            if cached:
                if req.role:
                    cached["role"] = req.role
                if req.is_active is not None:
                    cached["is_active"] = req.is_active
                if req.preferred_language:
                    cached["preferred_language"] = req.preferred_language
            return {"status": "updated"}
        except HTTPException:
            raise
        except Exception as e:
            log.warning("PG admin user update failed: %s", e)
            raise HTTPException(status_code=503, detail="user_store_unavailable")
    target = None
    for username, data in _users_db.items():
        if data["id"] == user_id:
            target = username
            break
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if req.role:
        _users_db[target]["role"] = req.role
    if req.is_active is not None:
        _users_db[target]["is_active"] = req.is_active
    if req.preferred_language:
        _users_db[target]["preferred_language"] = req.preferred_language
    # Persist to Postgres too when reachable: the in-memory _users_db is per
    # process, so an admin's change (e.g. deactivating an account) must be stored
    # to survive a restart.
    try:
        from src.services.pg_store import update_user as _pg_update_user
        await asyncio.to_thread(
            _pg_update_user, user_id,
            role=req.role, is_active=req.is_active, preferred_language=req.preferred_language,
        )
    except Exception:
        pass
    return {"status": "updated"}


@app.get("/api/v1/admin/roles")
async def list_roles(user: TokenData = Depends(get_current_user)):
    return {"roles": ROLE_DEFINITIONS}


@app.get("/api/v1/admin/audit")
async def get_audit_log(limit: int = 100, user: TokenData = Depends(require_role("admin", "risk"))):
    try:
        from src.services.pg_store import get_audit_trail
        df = await asyncio.to_thread(get_audit_trail, limit=limit)
        return {"logs": df.to_dict(orient="records") if not df.empty else []}
    except Exception as e:
        return {"logs": [], "error": str(e)}


@app.post("/api/v1/admin/seed")
async def seed_data(user: TokenData = Depends(require_role("admin"))):
    from src.services.pg_store import seed_all_domains
    count = await asyncio.to_thread(seed_all_domains)
    return {"status": "seeded", "rows": count}

VALID_SCENARIOS = ["healthy", "declining_financial", "high_churn_crisis", "operational_meltdown",
                    "talent_crisis", "cybersecurity_breach", "esg_compliance_failure"]


def _run_scenario_switch(scenario: str) -> Dict[str, Any]:
    """The actual scenario switch — writes thousands of KPI rows, extracts entities,
    generates + embeds knowledge docs. Confirmed live to take 80s+, which is why this
    is called from a background task by the async endpoint below rather than inline.

    "healthy" is not "generate a fresh synthetic healthy-looking dataset" — it resets
    to the real baseline dataset exactly, by removing the active scenario's overlay
    rather than regenerating an approximation of it (see reset_to_baseline())."""
    from scripts.seed_scenarios import reset_to_baseline, seed_database
    if scenario == "healthy":
        return reset_to_baseline()
    return seed_database(replace=True, scenario=scenario)


@app.post("/api/v1/admin/scenario")
async def switch_scenario(req: ScenarioRequest, user: TokenData = Depends(require_role("admin"))):
    """Switch database scenario for benchmarking (admin only) — synchronous, blocks
    until the switch completes. A switch can take over a minute, longer than a reverse
    proxy typically waits, so prefer POST .../async + GET .../{job_id} below for any
    caller behind one; this synchronous form is for callers that set their own longer
    timeout (e.g. local dev, or scripts run directly against the backend)."""
    if req.scenario not in VALID_SCENARIOS:
        raise HTTPException(status_code=400, detail=f"Invalid scenario. Valid: {', '.join(VALID_SCENARIOS)}")
    try:
        counts = await asyncio.to_thread(_run_scenario_switch, req.scenario)
        return {"status": "success", "scenario": req.scenario, "counts": counts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/admin/scenario/async")
async def switch_scenario_async(req: ScenarioRequest, background: BackgroundTasks,
                                 user: TokenData = Depends(require_role("admin"))):
    """Same switch as POST /api/v1/admin/scenario, but returns a job_id immediately
    instead of blocking — the fix for the Cloudflare 524/502 risk documented above.
    Poll GET /api/v1/admin/scenario/{job_id} for the result."""
    if req.scenario not in VALID_SCENARIOS:
        raise HTTPException(status_code=400, detail=f"Invalid scenario. Valid: {', '.join(VALID_SCENARIOS)}")
    from src.services.admin_jobs import new_job, run_job
    job_id = new_job({"scenario": req.scenario}, owner_user_id=user.user_id)
    background.add_task(run_job, job_id, lambda: _run_scenario_switch(req.scenario))
    return {"job_id": job_id}


@app.get("/api/v1/admin/scenario/{job_id}")
async def scenario_job_status(job_id: str, user: TokenData = Depends(require_role("admin"))):
    """Poll target for POST /api/v1/admin/scenario/async."""
    from src.services.admin_jobs import get_job
    job = await asyncio.to_thread(get_job, job_id, user.user_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")
    out = {"job_id": job_id, "status": job["status"]}
    if job["status"] == "done":
        result = job.get("result") or {}
        out["scenario"] = (job.get("request") or {}).get("scenario")
        out["counts"] = result
    elif job["status"] == "error":
        out["error"] = job.get("error")
    return out


@app.get("/api/v1/admin/scenario")
async def get_current_scenario(user: TokenData = Depends(require_role("admin"))):
    """Get current active scenario (admin only)."""
    # This would require tracking current scenario in database, for now return default
    return {"current_scenario": "healthy", "available_scenarios": VALID_SCENARIOS}




@app.post("/api/v1/admin/cleanup")
async def cleanup_data(user: TokenData = Depends(require_role("admin"))):
    """Wipe safe-to-delete data (chat history + audit trail); keeps KPI/knowledge/seed data."""
    from src.services.pg_store import clear_user_data
    return {"status": "cleaned", "deleted": await asyncio.to_thread(clear_user_data)}


@app.get("/api/v1/admin/vsdebug")
async def vsdebug(q: str = "revenue", user: TokenData = Depends(require_role("admin"))):
    """Diagnostic: localize why knowledge search may return nothing."""
    out = {}
    try:
        from src.services.vector_store import get_vector_store, vector_store_retrieve
        vs = get_vector_store()
        out["vs"] = getattr(vs, "name", None)
        if vs is not None:
            out["count"] = vs.count()
            try:
                dense = vs.query(q, n=5)
                out["dense_hits"] = len(dense)
                out["dense_top"] = (dense[0]["title"], round(dense[0]["score"], 3)) if dense else None
            except Exception as e:
                out["dense_error"] = str(e)[:200]
        fused = vector_store_retrieve(q, top_k=3, language="en")
        out["fused_hits"] = (len(fused) if fused is not None else None)
    except Exception as e:
        out["error"] = str(e)[:200]
    return out


@app.post("/api/v1/admin/reindex")
async def reindex_vectors(force: bool = True, user: TokenData = Depends(require_role("admin"))):
    """(Re)build the persistent vector store from the knowledge base — fixes empty search.
    force=True (default) drops + recreates the store at the current embedding dimension."""
    from src.services.vector_store import reindex, get_vector_store
    if get_vector_store() is None:
        return {"status": "skipped", "reason": "VECTOR_STORE=memory (no persistent store)"}
    # reindex() does real, minutes-long blocking work (a DB read plus hundreds of
    # synchronous remote embed calls) — calling it directly on this coroutine blocks
    # the whole event loop for the entire duration, freezing every other request on
    # this instance (WEB_CONCURRENCY=1). Confirmed live: /health and other simple
    # endpoints went unresponsive for the full reindex.
    n = await asyncio.to_thread(reindex, force=force)
    return {"status": "reindexed", "docs": n, "force": force}


# ─── DocIntel Admin Integration ───────────────────────────────────────────────

@app.get("/api/v1/admin/docintel/stats")
async def get_admin_docintel_stats(user: TokenData = Depends(require_role("admin"))):
    """Fetch live DocIntel extraction statistics and database metrics from the DocIntel service."""
    doc_url = settings.DOC_PROCESSOR_URL
    if not doc_url:
        return {"connected": False, "error": "DOC_PROCESSOR_URL not configured",
                "service_url": None, "total_documents": 0, "avg_confidence": 0.0,
                "avg_processing_time_ms": 0.0, "total_pages": 0, "by_doc_type": {}, "by_route": {}}
    import httpx
    headers = {}
    if settings.DOC_PROCESSOR_TOKEN:
        headers["X-DocIntel-Internal-Token"] = settings.DOC_PROCESSOR_TOKEN
        headers["Authorization"] = f"Bearer {settings.DOC_PROCESSOR_TOKEN}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{doc_url}/api/documents/stats", headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                data["service_url"] = doc_url
                data["connected"] = True
                return data
            return {
                "service_url": doc_url,
                "connected": False,
                "error": f"DocIntel responded with status {resp.status_code}",
                "total_documents": 0,
                "avg_confidence": 0.0,
                "avg_processing_time_ms": 0.0,
                "total_pages": 0,
                "by_doc_type": {},
                "by_route": {},
            }
    except Exception as e:
        return {
            "service_url": doc_url,
            "connected": False,
            "error": str(e),
            "total_documents": 0,
            "avg_confidence": 0.0,
            "avg_processing_time_ms": 0.0,
            "total_pages": 0,
            "by_doc_type": {},
            "by_route": {},
        }


@app.get("/api/v1/admin/docintel/documents")
async def get_admin_docintel_documents(
    limit: int = 50,
    offset: int = 0,
    doc_type: Optional[str] = None,
    search: Optional[str] = None,
    user: TokenData = Depends(require_role("admin")),
):
    """List persistent document extraction records from DocIntel Neon DB."""
    doc_url = settings.DOC_PROCESSOR_URL
    if not doc_url:
        return {"total": 0, "documents": [], "limit": limit, "offset": offset,
                "error": "DOC_PROCESSOR_URL not configured"}
    import httpx
    headers = {}
    if settings.DOC_PROCESSOR_TOKEN:
        headers["X-DocIntel-Internal-Token"] = settings.DOC_PROCESSOR_TOKEN
        headers["Authorization"] = f"Bearer {settings.DOC_PROCESSOR_TOKEN}"
    params = {"limit": limit, "offset": offset}
    if doc_type:
        params["doc_type"] = doc_type
    if search:
        params["search"] = search
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{doc_url}/api/documents", headers=headers, params=params)
            if resp.status_code == 200:
                return resp.json()
            return {"total": 0, "documents": [], "limit": limit, "offset": offset, "error": resp.text}
    except Exception as e:
        return {"total": 0, "documents": [], "limit": limit, "offset": offset, "error": str(e)}


# ════════════════════════════════════════════════════════════
# CHAT HISTORY & SESSIONS (PostgreSQL)
# ════════════════════════════════════════════════════════════
# NOTE: GET /api/v1/chat/sessions itself is registered earlier, right before
# GET /api/v1/chat/{job_id} — see the comment there for why route order matters here.

@app.get("/api/v1/chat/sessions/{session_id}/messages")
async def get_chat_messages(
    session_id: str,
    request: Request,
    user: TokenData = Depends(get_current_user),
    x_admin_token: Optional[str] = Header(default=None, alias="X-Admin-Token"),
    x_intelai_token: Optional[str] = Header(default=None, alias="X-IntelAI-Internal-Token"),
):
    try:
        from src.services.pg_store import get_session_messages
        admin_secret = os.getenv("ADMIN_TOKEN")
        is_admin = bool(
            (x_admin_token and admin_secret and hmac.compare_digest(x_admin_token, admin_secret)) or
            (user.role == "admin")
        )
        target_user = "*" if is_admin else user.user_id
        messages = await asyncio.to_thread(get_session_messages, session_id, target_user)
        return {"messages": messages, "session_id": session_id}
    except Exception as e:
        return {"messages": [], "error": str(e)}


@app.post("/api/v1/chat/sessions")
async def create_new_session(user: TokenData = Depends(get_current_user)):
    try:
        from src.services.pg_store import create_chat_session
        session_id = await asyncio.to_thread(create_chat_session, user.user_id)
        return {"session_id": session_id, "title": "New Chat"}
    except Exception as e:
        return {"session_id": str(uuid.uuid4()), "error": str(e)}


@app.put("/api/v1/chat/sessions/{session_id}/title")
async def rename_session(session_id: str, req: Dict[str, str], user: TokenData = Depends(get_current_user)):
    try:
        from src.services.pg_store import update_session_title
        updated = await asyncio.to_thread(update_session_title, session_id, user.user_id, req.get("title", "Untitled"))
        if not updated:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"status": "updated"}
    except HTTPException:
        raise
    except Exception as e:
        return {"error": str(e)}


@app.delete("/api/v1/chat/sessions/{session_id}")
async def delete_chat_session(session_id: str, user: TokenData = Depends(get_current_user)):
    try:
        from src.services.pg_store import delete_session
        deleted = await asyncio.to_thread(delete_session, session_id, user.user_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"status": "deleted"}
    except HTTPException:
        raise
    except Exception as e:
        return {"error": str(e)}


# ════════════════════════════════════════════════════════════
# KNOWLEDGE BASE SEARCH (vector store / hybrid retrieval)
# ════════════════════════════════════════════════════════════

@app.get("/api/v1/knowledge/search")
async def knowledge_search(q: str, n: int = 5, user: TokenData = Depends(get_current_user)):
    """Retrieve the most relevant knowledge-base docs through the configured retrieval stack:
    the persistent vector store (chroma/pgvector/qdrant) fused with BM25 + reranker when
    VECTOR_STORE is set, otherwise the in-process hybrid retriever."""
    try:
        from src.services.omnismart_chatbot import _get_shared_rag
        rag = _get_shared_rag()
        # Detect the query language; it only sets a preference, documents in both
        # languages remain searchable (the models are multilingual).
        from src.services.language import detect_language
        detected_lang = detect_language(q, default=getattr(user, "language", None) or "en")

        hits = await asyncio.to_thread(
            rag._retrieve_documents, q, top_k=n, language=detected_lang
        )
        if not hits:  # last-resort: retry language-agnostic
            hits = await asyncio.to_thread(rag._retrieve_documents, q, top_k=n)
        results = [
            {"title": title, "content": (content or "")[:600], "score": round(score, 4)}
            for title, content, score in hits
        ]
        out = {"results": results, "query": q, "count": len(results), "detected_language": detected_lang}
        if getattr(hits, "partial", False):
            out["partial"] = True
        return out
    except Exception as e:
        return {"results": [], "query": q, "error": str(e)}


def _detect_search_language(q: str, user: TokenData) -> str:
    from src.services.language import detect_language
    return detect_language(q, default=getattr(user, "language", None) or "en")


_SEARCH_JOBS: Dict[str, Dict[str, Any]] = {}
_SEARCH_JOB_TTL = 900.0


@app.post("/api/v1/knowledge/search/async")
async def knowledge_search_async(q: str, n: int = 5, user: TokenData = Depends(get_current_user)):
    """Start a search as a background job and return immediately.

    The full pipeline (dense + BM25 + RRF + cross-encoder) can take many seconds on a
    CPU host, so this returns a job id; poll ``GET /api/v1/knowledge/search/jobs/{id}``
    for stage progress, the fused preliminary ranking, and the final ranking."""
    import time as _time
    from src.services import retrieval_progress as _rp
    from src.services.omnismart_chatbot import _get_shared_rag

    now = _time.time()
    for k in [k for k, v in _SEARCH_JOBS.items() if now - v["created"] > _SEARCH_JOB_TTL]:
        _SEARCH_JOBS.pop(k, None)
        _rp.board.drop(k)
    # Collapse an identical in-flight search from the same user into one job.
    for jid, job in _SEARCH_JOBS.items():
        if job["owner"] == user.user_id and job["q"] == q and job["n"] == n and job["status"] == "running":
            return {"job_id": jid, "status": "running", "shared": True}

    job_id = str(uuid.uuid4())
    job: Dict[str, Any] = {"owner": user.user_id, "q": q, "n": n, "status": "running",
                           "created": now, "result": None, "error": None}
    _SEARCH_JOBS[job_id] = job
    _rp.board.update(job_id, stage="starting")
    lang = _detect_search_language(q, user)

    async def _run() -> None:
        token = _rp.set_progress_key(job_id)
        try:
            rag = _get_shared_rag()
            hits = await asyncio.to_thread(rag._retrieve_documents, q, top_k=n, language=lang, refine=True)
            if not hits:
                hits = await asyncio.to_thread(rag._retrieve_documents, q, top_k=n, refine=True)
            job["result"] = {
                "results": [{"title": t, "content": (c or "")[:600], "score": round(s, 4)}
                            for t, c, s in hits],
                "query": q, "detected_language": lang,
                "partial": bool(getattr(hits, "partial", False)),
            }
            job["status"] = "done"
            _rp.board.update(job_id, stage="done")
        except Exception as e:  # surfaced to the poller, never an empty success
            job["status"], job["error"] = "error", str(e)[:500]
            _rp.board.update(job_id, stage="error")
        finally:
            _rp.reset_progress_key(token)

    asyncio.get_running_loop().create_task(_run())
    return {"job_id": job_id, "status": "running"}


@app.delete("/api/v1/knowledge/search/jobs/{job_id}")
async def knowledge_search_cancel(job_id: str, user: TokenData = Depends(get_current_user)):
    """Stop a running search: remaining cross-encoder batches are skipped."""
    from src.services import retrieval_progress as _rp
    job = _SEARCH_JOBS.get(job_id)
    if not job or job["owner"] != user.user_id:
        raise HTTPException(status_code=404, detail="search job not found")
    _rp.board.update(job_id, cancelled=True)
    return {"job_id": job_id, "cancelled": True}


@app.get("/api/v1/knowledge/search/jobs/{job_id}")
async def knowledge_search_job(job_id: str, user: TokenData = Depends(get_current_user)):
    from src.services import retrieval_progress as _rp
    job = _SEARCH_JOBS.get(job_id)
    if not job or job["owner"] != user.user_id:
        raise HTTPException(status_code=404, detail="search job not found")
    out: Dict[str, Any] = {"job_id": job_id, "status": job["status"]}
    state = _rp.board.get(job_id) or {}
    out["progress"] = {k: state[k] for k in ("stage", "done", "total", "candidates") if k in state}
    if state.get("preliminary"):
        out["preliminary"] = state["preliminary"]
    if job["status"] == "done":
        out.update(job["result"])
    elif job["status"] == "error":
        out["error"] = job["error"]
    return out


@app.get("/api/v1/knowledge/stats")
async def knowledge_stats(user: TokenData = Depends(get_current_user)):
    try:
        from src.services.pg_store import get_knowledge_docs
        docs = await asyncio.to_thread(get_knowledge_docs)
        embedded = 0
        if not docs.empty and "embedding" in docs.columns:
            embedded = docs["embedding"].notna().sum()
        return {
            "total_documents": len(docs),
            "embedded_documents": int(embedded),
            "sources": docs["source"].unique().tolist() if not docs.empty and "source" in docs.columns else [],
        }
    except Exception as e:
        return {"total_documents": 0, "error": str(e)}


# ════════════════════════════════════════════════════════════
# WEBSOCKET CHAT
# ════════════════════════════════════════════════════════════

@app.websocket("/api/v1/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    try:
        auth_msg = await websocket.receive_json()
        token = auth_msg.get("token", "")
        try:
            from src.core.jwt_auth import decode_access_token
            user = decode_access_token(token)
        except Exception:
            await websocket.send_json({"error": "Authentication failed"})
            await websocket.close()
            return

        from src.services.omnismart_chatbot import get_persona_factory, llm_stream
        factory = get_persona_factory()
        session_id = str(uuid.uuid4())
        history = []
        _session_ready = False
        await websocket.send_json({"type": "connected", "user": user.username, "session_id": session_id})

        while True:
            data = await websocket.receive_json()
            message = data.get("message", "")
            persona_override = data.get("persona")
            if data.get("session_id"):
                session_id = data["session_id"]
            language = data.get("language") or user.language

            # Phase 1: RAG retrieval + persona setup (fast, synchronous-in-thread)
            # This builds the full messages list with retrieved context. Retrieval
            # stages report under a per-turn key; a small pump forwards real stage
            # progress to the client while the turn is being prepared.
            from src.services import retrieval_progress as _rp
            progress_id = f"ws-{uuid.uuid4()}"
            progress_token = _rp.set_progress_key(progress_id)
            _rp.board.update(progress_id, stage="starting")

            async def _progress_pump(pid=progress_id):
                last = None
                sent_preliminary = False
                while True:
                    await asyncio.sleep(0.6)
                    state = _rp.board.get(pid)
                    if not state:
                        continue
                    sig = (state.get("stage"), state.get("done"), state.get("total"))
                    payload = None
                    if sig != last:
                        last = sig
                        payload = {"type": "progress", "stage": sig[0], "done": sig[1], "total": sig[2]}
                    if state.get("preliminary") and not sent_preliminary:
                        sent_preliminary = True
                        payload = payload or {"type": "progress", "stage": sig[0], "done": sig[1], "total": sig[2]}
                        payload["preliminary_sources"] = state["preliminary"]
                    if payload:
                        try:
                            await websocket.send_json(payload)
                        except Exception:
                            return

            progress_pump = asyncio.create_task(_progress_pump())
            try:
                rag_result = await asyncio.wait_for(
                    asyncio.to_thread(
                        factory.chat_prepare,
                        message=message, user_role=user.role,
                        persona_override=persona_override, language=language, history=history,
                    ),
                    timeout=_chat_turn_timeout_seconds(),
                )
            except asyncio.TimeoutError:
                await websocket.send_json({
                    "type": "error",
                    "error": f"Retrieval timed out after {int(_chat_turn_timeout_seconds())}s. Please retry.",
                })
                continue
            except AttributeError:
                # chat_prepare not available — fall back to full blocking chat with chunk wrapping
                try:
                    result = await asyncio.wait_for(
                        asyncio.to_thread(
                            factory.chat,
                            message=message, user_role=user.role,
                            persona_override=persona_override, language=language, history=history,
                        ),
                        timeout=_chat_turn_timeout_seconds(),
                    )
                except asyncio.TimeoutError:
                    await websocket.send_json({
                        "type": "error",
                        "error": f"Chat turn timed out after {int(_chat_turn_timeout_seconds())}s. Please retry.",
                    })
                    continue
                # Simulate streaming by sending the full response as a single chunk then the response frame
                await websocket.send_json({"type": "chunk", "text": result["response"]})
                history.append({"role": "user", "content": message})
                history.append({"role": "assistant", "content": result["response"]})
                try:
                    import json as _json
                    from src.services.pg_store import ensure_session_exists, store_message
                    if not _session_ready:
                        await asyncio.to_thread(ensure_session_exists, session_id, getattr(user, "user_id", user.username))
                        _session_ready = True
                    await asyncio.to_thread(store_message, session_id, "user", message)
                    await asyncio.to_thread(store_message, session_id, "assistant", result["response"],
                                  sources=_json.dumps(result.get("sources", [])))
                except Exception as e:
                    log.warning("WS message persistence failed: %s", e)
                await websocket.send_json({
                    "type": "response", "response": result["response"],
                    "session_id": session_id,
                    "persona_used": result["persona_used"],
                    "persona_display": result.get("persona_display", ""),
                    "tokens_used": result.get("tokens_used", 0),
                    "latency_ms": result.get("latency_ms", 0),
                    "sources": result.get("sources", []),
                    "blocks": _structure_answer(result["response"]),
                })
                continue

            finally:
                progress_pump.cancel()
                _rp.reset_progress_key(progress_token)
                _rp.board.drop(progress_id)

            # Phase 2: Streaming LLM generation — send tokens as they arrive
            messages_for_llm = rag_result["messages"]
            persona_name = rag_result.get("persona_name", "general")
            sources = rag_result.get("sources", [])

            full_text = ""
            import time as _time
            start_ts = _time.time()
            try:
                async for token_text in llm_stream(
                    messages=messages_for_llm,
                    temperature=rag_result.get("temperature", 0.3),
                    max_tokens=2048,
                    persona_name=persona_name,
                ):
                    full_text += token_text
                    try:
                        await websocket.send_json({"type": "chunk", "text": token_text})
                    except Exception:
                        break  # client disconnected during streaming
            except Exception as e:
                log.error("Streaming LLM error: %s", e)
                if not full_text:
                    await websocket.send_json({"type": "error", "error": f"Generation failed: {e}"})
                    continue

            latency_ms = int((_time.time() - start_ts) * 1000)
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": full_text})

            # Persist turn
            try:
                import json as _json
                from src.services.pg_store import ensure_session_exists, store_message
                if not _session_ready:
                    await asyncio.to_thread(ensure_session_exists, session_id, getattr(user, "user_id", user.username))
                    _session_ready = True
                await asyncio.to_thread(store_message, session_id, "user", message)
                await asyncio.to_thread(store_message, session_id, "assistant", full_text,
                              sources=_json.dumps(sources))
            except Exception as e:
                log.warning("WS message persistence failed: %s", e)

            await websocket.send_json({
                "type": "response", "response": full_text,
                "session_id": session_id,
                "persona_used": persona_name,
                "persona_display": rag_result.get("persona_display", ""),
                "tokens_used": 0,  # streaming doesn't return usage in all providers
                "latency_ms": latency_ms,
                "sources": sources,
                "blocks": _structure_answer(full_text),
            })
    except WebSocketDisconnect:
        log.info("WebSocket client disconnected")
    except Exception as e:
        log.error("WebSocket error: %s", e)



# ════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════

def _load_chat_history(user_id: str, session_id: str) -> List[Dict[str, str]]:
    """Prior turns of a session as [{"role", "content"}]. Uses get_session_messages(),
    the ownership-scoped query behind GET .../messages, which returns the real
    role/content columns."""
    try:
        from src.services.pg_store import get_session_messages
        rows = get_session_messages(session_id, user_id)
        history = [{"role": r["role"], "content": r["content"]} for r in rows if r.get("role") and r.get("content")]
        return history[-10:]
    except Exception:
        return []


def _store_chat(user_id: str, session_id: str, message: str, result: dict):
    try:
        from src.services.pg_store import store_conversation
        store_conversation(session_id, message, result.get("response", ""))
    except Exception as e:
        log.warning("Failed to store conversation: %s", e)



# ════════════════════════════════════════════════════════════════════════════
# NEW ENDPOINTS: DOMAIN SWITCHING, DATA INGESTION/EXPORT, & MINI-SPREADSHEET
# ════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/chatbot/domain")
async def set_chatbot_domain(
    domain: str,
    user: TokenData = Depends(get_current_user),
):
    """
    Set user's chatbot domain preference (finance, hr, ops, esg, growth, general).

    This personalizes the conversational agent to focus on a specific domain.
    """
    valid_domains = ["finance", "hr", "ops", "esg", "growth", "general"]
    if domain not in valid_domains:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid domain. Must be one of: {', '.join(valid_domains)}"
        )

    from src.services.pg_store import (
        set_user_default_domain,
        update_domain_history,
    )

    try:
        await asyncio.to_thread(set_user_default_domain, user.username, domain)
        await asyncio.to_thread(update_domain_history, user.username, domain)

        log.info("Domain set to %s for user %s", domain, user.username)

        return {
            "status": "success",
            "domain": domain,
            "message": f"Chatbot domain switched to {domain}"
        }
    except Exception as e:
        log.error("Failed to set domain: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/chatbot/domain")
async def get_chatbot_domain(user: TokenData = Depends(get_current_user)):
    """Get user's current chatbot domain preference."""
    from src.services.pg_store import get_user_default_domain

    try:
        domain = await asyncio.to_thread(get_user_default_domain, user.username)
        return {
            "domain": domain,
            "valid_domains": ["finance", "hr", "ops", "esg", "growth", "general"],
        }
    except Exception as e:
        log.error("Failed to get domain: %s", e)
        return {"domain": "general", "error": str(e)[:200]}


# ════════════════════════════════════════════════════════════════════════════
# DATA INGESTION & MANAGEMENT
# ════════════════════════════════════════════════════════════════════════════

class DataIngestionRequest(BaseModel):
    file_type: str  # csv, xlsx, pdf, docx, json
    source: str  # upload, email, drive, api
    destination: str  # kpis, knowledge_base, spreadsheet
    destination_name: Optional[str] = None  # if destination is spreadsheet
    domain: Optional[str] = None  # finance, hr, ops, etc.
    mapping_config: Optional[Dict[str, Any]] = None  # column mappings
    description: Optional[str] = None


# ════════════════════════════════════════════════════════════════════════════

class DataExportRequest(BaseModel):
    source_type: str  # kpis, conversation, knowledge_base, spreadsheet
    format: str  # csv, xlsx, pdf, json
    source_name: Optional[str] = None  # for spreadsheet export
    query: Optional[Dict[str, Any]] = None  # filter/query parameters


@app.post("/api/v1/data/export")
async def export_data(
    req: DataExportRequest,
    user: TokenData = Depends(get_current_user),
):
    """
    Export data in various formats (CSV, XLSX, PDF, JSON).

    Supports sources:
    - kpis: Export KPI metrics
    - spreadsheet: Export mini-spreadsheet data
    - knowledge_base: Export indexed documents
    - conversation: Export chat history
    """
    from src.services.pg_store import log_data_export, update_export_log
    import io
    import base64

    export_id = await asyncio.to_thread(log_data_export,
        username=user.username,
        export_name=req.source_name or f"export_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
        export_format=req.format,
        source_type=req.source_type,
        status="processing",
        query=req.query,
    )

    try:
        if req.source_type == "spreadsheet":
            if not req.source_name:
                raise HTTPException(status_code=400, detail="source_name required")

            from src.services.pg_store import export_spreadsheet

            data = await asyncio.to_thread(export_spreadsheet, user.username, req.source_name, req.format)
            if not data:
                raise HTTPException(status_code=404, detail="Spreadsheet not found")

            filename = f"{req.source_name}.{req.format}"

        elif req.source_type == "kpis":
            from src.services.pg_store import get_kpi_metrics

            # Get KPI data
            df = await asyncio.to_thread(get_kpi_metrics)
            if not df.empty:
                df = df.head(10000)

            if req.format == "csv":
                data = df.to_csv(index=False)
                filename = "kpis_export.csv"
            elif req.format == "json":
                data = df.to_json(orient="records", indent=2)
                filename = "kpis_export.json"
            elif req.format == "xlsx":
                buffer = io.BytesIO()
                df.to_excel(buffer, index=False)
                data = base64.b64encode(buffer.getvalue()).decode()
                filename = "kpis_export.xlsx"
            elif req.format == "pdf":
                from src.services.board_report import generate_board_pdf
                data = base64.b64encode(generate_board_pdf()).decode()
                filename = "board_report.pdf"
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported format: {req.format}")

        else:
            raise HTTPException(status_code=400, detail=f"Unsupported source: {req.source_type}")

        await asyncio.to_thread(update_export_log,
            export_id=export_id,
            status="completed",
            file_size_bytes=len(data.encode()) if isinstance(data, str) else len(data),
            row_count=len(data.split("\n")) if req.format == "csv" else 1,
        )

        # csv/json are returned as text; xlsx is base64-encoded so the client can
        # decode and download it directly (no separate download round-trip).
        return {
            "status": "success",
            "export_id": export_id,
            "format": req.format,
            "filename": filename,
            "encoding": "base64" if req.format in ("xlsx", "pdf") else "text",
            "data": data,
            "download_url": f"/api/v1/exports/{export_id}/download",
        }

    except HTTPException:
        raise
    except Exception as e:
        log.error("Data export error: %s", e)
        await asyncio.to_thread(update_export_log, export_id=export_id, status="failed", error_message=str(e)[:500])
        raise HTTPException(status_code=500, detail=str(e))


# ════════════════════════════════════════════════════════════
# SPA CATCH-ALL — must stay LAST (routes are matched in definition order)
# ════════════════════════════════════════════════════════════

@app.get("/{full_path:path}", include_in_schema=False)
async def spa_fallback(full_path: str):
    """Serve the SPA's index.html for client-side routes.

    The frontend is a client-side-routed React app, so /dashboard, /chat, /api-docs …
    exist only in the browser's router — the server has no route for them. Without this
    fallback the single-container deployment (FastAPI serving frontend/dist itself, per
    SELF_HOSTING.md and the Dockerfile) 404s on every deep link: refreshing any page,
    opening a bookmark, or following a shared URL all fail, and only "/" works. Verified
    against the real production topology (uvicorn src.api.server:app, no dev proxy):
    /dashboard, /chat, /api-docs, /settings and /knowledge-graph all returned 404 before
    this existed.

    A split deploy (static frontend + this API) never hit it because the host's SPA fallback already
    rewrites /(.*) to /index.html — which is exactly why it survived: the hosted demo
    masks a bug that every self-hoster would hit immediately.

    API/doc paths are excluded so a genuinely wrong endpoint still returns a JSON 404
    instead of silently handing back HTML (which would surface downstream as a confusing
    JSON-parse error rather than "that route doesn't exist").
    """
    import os as _o
    from fastapi.responses import FileResponse
    if full_path.startswith(("api/", "health", "docs", "openapi.json", "metrics", "static/", "assets/")):
        raise HTTPException(status_code=404, detail="Not Found")
    spa = _o.path.join(_o.path.dirname(_o.path.dirname(_o.path.dirname(__file__))),
                       "frontend", "dist", "index.html")
    if _o.path.exists(spa):
        return FileResponse(spa)
    raise HTTPException(status_code=404, detail="Not Found")
