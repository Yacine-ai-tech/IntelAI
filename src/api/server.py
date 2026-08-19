"""
IntelAI API v1 — FastAPI server with JWT auth, RBAC, multi-domain intelligence.

Persona-aware AI analytics & RAG copilot. Domains: Finance, HR, Logistics, IT,
Operations, ESG, Growth/Risk.
"""
from __future__ import annotations

import asyncio
import os
import uuid
import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import pandas as pd
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, WebSocket, WebSocketDisconnect, Query, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.core.logger import get_logger
from src.core.jwt_auth import (
    TokenData, LoginRequest, RegisterRequest,
    hash_password, verify_password,
    create_access_token, get_current_user, require_role, require_page, get_user_data_categories, get_user_pages,
    ROLE_DEFINITIONS, DEFAULT_USERS,
)
from src.core.config import get_cors_allowed_origins, settings


log = get_logger(__name__)

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
    See TELEMETRY.md for why this is a random UUID rather than a hardware-derived value.
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


def _send_telemetry():
    """
    One anonymous startup ping per ~6h to TELEMETRY_URL, so the project can count distinct
    installs. Sends only {service, event, instance_id} — no request data, document/KPI
    content, or credentials. Disable entirely with TELEMETRY_OPT_OUT=true.
    """
    if os.environ.get("TELEMETRY_OPT_OUT", "").strip().lower() in ("true", "1", "yes"):
        return

    lock_file = os.path.join(str(settings.LOGS_DIR), ".telemetry_last_ping")
    try:
        if os.path.exists(lock_file) and time.time() - os.path.getmtime(lock_file) < 21600:
            return
        with open(lock_file, "w") as f:
            f.write(str(time.time()))
    except Exception:
        pass

    try:
        telemetry_url = os.environ.get(
            "TELEMETRY_URL", os.environ.get("TELEMETRY_URL", "https://gateway.ysiddo-ai-projects.app/telemetry")
        )
        if "log" in globals():
            globals()["log"].info(
                "Anonymous telemetry ping to %s (set TELEMETRY_OPT_OUT=true to disable).",
                telemetry_url,
            )
        else:
            import logging
            logging.info(
                "Anonymous telemetry ping to %s (set TELEMETRY_OPT_OUT=true to disable).",
                telemetry_url,
            )

        requests.post(
            telemetry_url,
            json={"service": "IntelAI", "event": "startup", "instance_id": _telemetry_instance_id()},
            timeout=2,
        )
    except Exception:
        pass

threading.Thread(target=_send_telemetry, daemon=True).start()
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
    if (request.url.path in ["/health", "/docs", "/openapi.json", "/api/redoc"]
            or request.url.path.startswith("/api/v1/auth/")
            or request.url.path.startswith("/api/v1/webhook/")):
        return await call_next(request)

    token = request.headers.get("X-IntelAI-Internal-Token")
    expected_token = _os.environ.get("INTELAI_INTERNAL_TOKEN", "")

    if token != expected_token and _os.environ.get("REQUIRE_INTERNAL_TOKEN", "true").lower() == "true":
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
    - ``text``      — everything else
    """
    import re as _re
    lines = (text or "").replace("\r\n", "\n").split("\n")
    blocks: List[Dict[str, Any]] = []
    buf: List[str] = []
    in_code = False
    code_buf: List[str] = []
    list_buf: List[str] = []
    list_ordered = False

    def flush_text():
        t = " ".join(buf).strip()
        if t:
            blocks.append({"type": "text", "content": t})
        buf.clear()

    def flush_list():
        if list_buf:
            blocks.append({"type": "list", "ordered": list_ordered, "items": list(list_buf)})
            list_buf.clear()

    for line in lines:
        stripped = line.strip()

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
    log.info("🚀 IntelAI API starting...")

    # Fail fast — required API keys must be present
    from src.core.config import validate_required_keys
    validate_required_keys()

    # Initialize PostgreSQL (users, chat sessions, monitoring)
    try:
        from src.services.pg_store import init_pg_tables
        await asyncio.to_thread(init_pg_tables)
        log.info("✅ PostgreSQL initialized")
    except Exception as e:
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
            log.warning("Vector store self-heal skipped: %s", e)

    import asyncio as _asyncio
    _asyncio.create_task(_asyncio.to_thread(_vector_selfheal))
    log.info("Vector store self-heal scheduled (background)")

    # The comment above claims chat is available immediately after startup — it wasn't:
    # _get_shared_rag() is a lazy singleton, so the FIRST real chat message (not this
    # self-heal, which only covers the separate, currently-unused Qdrant path) paid the
    # full embedding-index-build cost inline (confirmed live: minutes, not seconds).
    # Same fix, same pattern — build it here instead, off the request path.
    def _rag_prewarm():
        try:
            from src.services.omnismart_chatbot import _get_shared_rag
            _get_shared_rag()
            log.info("✅ Chat retrieval index pre-warmed (background)")
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
        vs = get_vector_store()
        if vs is None:
            return "memory (no persistent store configured)"
        vs.count()
        return "ok"
    except Exception as e:
        return f"unreachable: {e}"


@app.get("/health")
async def health_check():
    # The configured Render + docker-compose health check — previously a hardcoded
    # "postgresql" string regardless of whether the DB was actually reachable, so a
    # dead connection pool never showed up here. Bounded so a slow DB can't make this
    # endpoint itself the timeout; still returns 200 (informational, not a hard gate)
    # to avoid turning a transient DB hiccup into a restart storm.
    try:
        db_status, vs_status = await asyncio.wait_for(
            asyncio.gather(
                asyncio.to_thread(_health_db_check),
                asyncio.to_thread(_health_vector_store_check),
            ),
            timeout=5.0,
        )
    except asyncio.TimeoutError:
        db_status = vs_status = "timeout"
    return {
        "status": "healthy" if db_status == "ok" else "degraded",
        "service": "IntelAI API",
        "version": "2026.3.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": db_status,
        "vector_store": vs_status,
    }


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

@app.post("/api/v1/auth/login")
async def login(req: LoginRequest):
    user_data = _users_db.get(req.username)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    if not verify_password(req.password, user_data["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
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
    any password in the frontend. Gated by DEMO_MODE (default on). Real logins still use passwords
    (documented in the repo-root `credentials` file).

    Demo-session scoping (default on, DEMO_SESSION_SCOPING): when the caller sends
    X-Demo-Session-Id, each browser gets its own ephemeral identity per role — deterministic
    from (role, session id), so the same visitor keeps their chat history/uploads across
    requests, but two visitors who both pick "cfo" no longer share one user_id and can't see
    each other's chat sessions or uploaded files. Persona behavior (prompts, RBAC, page/data
    access) stays keyed by role either way. Falls back to the old shared-per-role identity
    when no session header is sent or scoping is disabled — not a production auth model."""
    import os as _os
    if _os.getenv("DEMO_MODE", "true").lower() != "true":
        raise HTTPException(status_code=403, detail="Demo mode disabled")
    _check_demo_login_rate_limit(request)
    from src.core.jwt_auth import ROLE_DEFINITIONS
    role = (role or "").lower()
    if role not in ROLE_DEFINITIONS:
        raise HTTPException(status_code=404, detail=f"Unknown role: {role}")

    demo_session_id = request.headers.get("X-Demo-Session-Id")
    from src.services.pg_store import get_or_create_demo_user
    if _os.getenv("DEMO_SESSION_SCOPING", "true").lower() == "true" and demo_session_id:
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
    if req.username in _users_db:
        raise HTTPException(status_code=400, detail="Username already exists")
    user_id = str(uuid.uuid4())
    pw_hash = hash_password(req.password)
    _users_db[req.username] = {
        "id": user_id,
        "username": req.username,
        "password_hash": pw_hash,
        "role": req.role,
        "is_active": True,
        "preferred_language": req.preferred_language,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    # Persist to PostgreSQL
    try:
        from src.services.pg_store import create_user
        await asyncio.to_thread(create_user, req.username, pw_hash, req.role, req.preferred_language)
    except Exception as e:
        log.warning("PG user creation failed: %s", e)
    return {"status": "registered", "user_id": user_id, "username": req.username}


@app.get("/api/v1/auth/me")
async def get_me(user: TokenData = Depends(get_current_user)):
    user_data = _users_db.get(user.username, {})
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

async def _run_chat_turn(req: "ChatRequest", user: TokenData) -> Dict[str, Any]:
    """The actual chat pipeline — retrieval + LLM completion + persistence. Shared by
    the synchronous POST /api/v1/chat and the async POST /api/v1/chat/async + GET
    /api/v1/chat/{job_id} pair, so both paths produce identical results; only how the
    caller receives them differs."""
    import json as _json
    from src.services.omnismart_chatbot import get_persona_factory

    session_id = req.session_id or str(uuid.uuid4())

    # Ensure session exists in PostgreSQL
    try:
        from src.services.pg_store import ensure_session_exists, store_message
        await asyncio.to_thread(ensure_session_exists, session_id, user.user_id)
    except Exception:
        pass  # Fallback — still works without PG

    # Prior turns in this session — without this, every REST message was answered with
    # no memory of the conversation despite a real session_id being tracked (confirmed
    # live: a follow-up question referring to the previous answer got no continuity).
    # The WebSocket handler already keeps this in memory per-connection; REST has no
    # persistent connection to hold that state in, so it's loaded from Postgres instead.
    history = await asyncio.to_thread(_load_chat_history, user.user_id, session_id)

    # Persona-routed RAG copilot: factory.chat auto-retrieves a role-scoped KPI
    # snapshot + knowledge docs and returns grounded answers with source citations.
    # (Same path as the WebSocket handler, so REST and the WS fallback behave identically.)
    factory = get_persona_factory()
    # factory.chat is the expensive part of this request — retrieval + an LLM completion,
    # typically seconds — and is synchronous throughout (sync retrieval, sync LLM client
    # calls). Off the event loop so one in-flight chat can't stall every other request.
    result = await asyncio.to_thread(
        factory.chat,
        message=req.message,
        user_role=user.role,
        persona_override=req.persona,
        language=req.language or user.language,
        context=req.context or "",
        history=history,
    )

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
    return await _run_chat_turn(req, user)


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
    job_id = new_job(req.model_dump(), owner_user_id=user.user_id)
    background.add_task(run_job, job_id, lambda: _run_chat_turn(req, user))
    return {"job_id": job_id}


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
    user: TokenData = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Get user's uploaded files."""
    from src.services.pg_store import get_user_files
    files = await asyncio.to_thread(get_user_files, user.username, limit=limit, offset=offset)
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
        # store_kpi_metrics() reads the "metric" column, not "metric_name" — without this
        # rename every webhook-ingested row was silently stored with metric='', discarding
        # the actual metric name entirely (found via live verification, fixed here).
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

                # 3. Index it immediately. add_texts() never existed on any vector-store
                # backend (ChromaVectorStore/PgVectorStore/QdrantVectorStore only
                # implement upsert/query/count/reset) — every webhook knowledge_doc
                # raised AttributeError here, silently caught below, while the endpoint
                # still returned HTTP 200 "success" (confirmed live).
                vs = get_vector_store()
                if vs:
                    vs.upsert([{"doc_id": doc_id, "title": title, "content": content_text[:4000],
                                "source": payload.source, "category": domain}])
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
    timeout = float(_os.environ.get("DOC_PROCESSOR_TIMEOUT", "180"))
    min_yield = int(_os.environ.get("DOC_PROCESSOR_MIN_CHARS", "200"))

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

    if best.strip():
        # Every endpoint came in under the yield floor. Some text beats none, but say
        # so loudly — this is the signature of a document the processor cannot really
        # read (a malformed or scanned-only PDF), not of a short document.
        log.warning(
            "Document processor returned only %d chars for %s — below the %d-char "
            "floor on every route. Tried: %s", len(best.strip()), filename, min_yield,
            "; ".join(errors))
        return best

    raise RuntimeError(
        f"document processor at {settings.DOC_PROCESSOR_URL} could not extract text "
        f"from {filename}. Tried: " + "; ".join(errors)
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
    # WEB_CONCURRENCY=1 deployment — a multi-second scan on a large document
    # previously froze every other in-flight request for its whole duration.
    from src.services.security import SecurityScanner
    text = await asyncio.to_thread(SecurityScanner.redact_text, text)

    doc_id = str(uuid.uuid4())
    # Store the extracted text in full. A fixed character cap here silently threw away
    # the tail of every long document — an 82-page filing extracting 277k chars kept
    # only its first 50k, and nothing in the response said so. Nothing downstream needs
    # a pre-truncated row: hybrid_retrieval.chunk_text() splits documents into passages
    # at index time, so a whole document is the correct unit to persist.
    docs_df = pd.DataFrame([{
        "doc_id": doc_id, "title": file.filename, "content": text,
        "source": category, "embedding": "",
    }])
    await asyncio.to_thread(store_knowledge_docs, docs_df, owner_user_id=owner)
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
        timeout = float(_os.environ.get("AUDIO_PROCESSOR_TIMEOUT", "300"))
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
    await asyncio.to_thread(log_audit_event, user.username, "AUDIO_INGEST", f"Processed {file.filename} via {settings.AUDIO_PROCESSOR_URL}")
    return {
        "status": "ingested", "doc_id": doc_id, "filename": file.filename,
        "chars": len(text), "transcript": transcript, "analysis": analysis,
        "scope": "global" if global_scope else "user",
    }


# ════════════════════════════════════════════════════════════
# KPI QUERIES (Cross-Domain)
# ════════════════════════════════════════════════════════════

@app.get("/api/v1/kpis")
async def get_kpis(
    period: Optional[str] = None,
    category: Optional[str] = None,
    segment: Optional[str] = None,
    user: TokenData = Depends(get_current_user),
):
    from src.services.pg_store import get_kpi_metrics, get_available_categories
    periods = [period] if period else None
    categories = [category] if category else None
    segments = [segment] if segment else None
    df = await asyncio.to_thread(get_kpi_metrics, periods=periods, categories=categories, segments=segments)

    # Filter by user's data access
    all_categories = await asyncio.to_thread(get_available_categories)
    user_categories = get_user_data_categories(user.role, all_categories)
    if "*" not in user_categories and "category" in df.columns and not df.empty:
        user_cat_lower = [c.lower() for c in user_categories]
        df = df[df["category"].str.lower().isin(user_cat_lower)]

    metrics = df.to_dict(orient="records") if not df.empty else []
    return {"metrics": metrics, "count": len(metrics)}


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

    df = await asyncio.to_thread(get_kpi_metrics, metrics=[metric])
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
    # silently reads as "the forecast is 0%", not "there isn't enough data to forecast" —
    # confirmed live: the UI rendered a real-looking-but-meaningless R²=0.000 result with
    # nothing telling the user why. Flag it explicitly instead.
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

@app.get("/api/v1/hr/summary")
async def get_hr_summary(user: TokenData = Depends(require_page("hr"))):
    from src.services.pg_store import get_kpi_metrics
    from src.services.hr import HRService
    return HRService().get_workforce_summary(await asyncio.to_thread(get_kpi_metrics))

@app.get("/api/v1/hr/departments")
async def get_hr_departments(user: TokenData = Depends(require_page("hr"))):
    from src.services.pg_store import get_kpi_metrics
    from src.services.hr import HRService
    return {"departments": HRService().get_department_analytics(await asyncio.to_thread(get_kpi_metrics))}

@app.get("/api/v1/hr/recruitment")
async def get_hr_recruitment(user: TokenData = Depends(require_page("hr"))):
    from src.services.pg_store import get_kpi_metrics
    from src.services.hr import HRService
    return HRService().get_recruitment_pipeline(await asyncio.to_thread(get_kpi_metrics))

@app.get("/api/v1/hr/training")
async def get_hr_training(user: TokenData = Depends(require_page("hr"))):
    from src.services.pg_store import get_kpi_metrics
    from src.services.hr import HRService
    return HRService().get_training_overview(await asyncio.to_thread(get_kpi_metrics))

@app.get("/api/v1/hr/health")
async def get_hr_health(user: TokenData = Depends(require_page("hr"))):
    from src.services.pg_store import get_kpi_metrics
    from src.services.hr import HRService
    return HRService().compute_hr_health_score(await asyncio.to_thread(get_kpi_metrics))


# ════════════════════════════════════════════════════════════
# LOGISTICS DOMAIN
# ════════════════════════════════════════════════════════════

@app.get("/api/v1/logistics/summary")
async def get_logistics_summary(user: TokenData = Depends(require_page("logistics"))):
    from src.services.pg_store import get_kpi_metrics
    from src.services.logistics import LogisticsService
    return LogisticsService().get_supply_chain_summary(await asyncio.to_thread(get_kpi_metrics))

@app.get("/api/v1/logistics/inventory")
async def get_logistics_inventory(user: TokenData = Depends(require_page("logistics"))):
    from src.services.pg_store import get_kpi_metrics
    from src.services.logistics import LogisticsService
    return LogisticsService().get_inventory_status(await asyncio.to_thread(get_kpi_metrics))

@app.get("/api/v1/logistics/shipping")
async def get_logistics_shipping(user: TokenData = Depends(require_page("logistics"))):
    from src.services.pg_store import get_kpi_metrics
    from src.services.logistics import LogisticsService
    return LogisticsService().get_shipping_analytics(await asyncio.to_thread(get_kpi_metrics))

@app.get("/api/v1/logistics/suppliers")
async def get_logistics_suppliers(user: TokenData = Depends(require_page("logistics"))):
    from src.services.pg_store import get_kpi_metrics
    from src.services.logistics import LogisticsService
    return {"suppliers": LogisticsService().get_supplier_metrics(await asyncio.to_thread(get_kpi_metrics))}

@app.get("/api/v1/logistics/health")
async def get_logistics_health(user: TokenData = Depends(require_page("logistics"))):
    from src.services.pg_store import get_kpi_metrics
    from src.services.logistics import LogisticsService
    return LogisticsService().compute_logistics_health(await asyncio.to_thread(get_kpi_metrics))


# ════════════════════════════════════════════════════════════
# IT OPERATIONS DOMAIN
# ════════════════════════════════════════════════════════════

@app.get("/api/v1/it/overview")
async def get_it_overview(user: TokenData = Depends(require_page("it"))):
    from src.services.pg_store import get_kpi_metrics
    from src.services.it_ops import ITOpsService
    return ITOpsService().get_it_overview(await asyncio.to_thread(get_kpi_metrics))

@app.get("/api/v1/it/tickets")
async def get_it_tickets(user: TokenData = Depends(require_page("it"))):
    from src.services.pg_store import get_kpi_metrics
    from src.services.it_ops import ITOpsService
    return ITOpsService().get_ticket_analytics(await asyncio.to_thread(get_kpi_metrics))

@app.get("/api/v1/it/security")
async def get_it_security(user: TokenData = Depends(require_page("it"))):
    from src.services.pg_store import get_kpi_metrics
    from src.services.it_ops import ITOpsService
    return ITOpsService().get_security_dashboard(await asyncio.to_thread(get_kpi_metrics))

@app.get("/api/v1/it/infrastructure")
async def get_it_infrastructure(user: TokenData = Depends(require_page("it"))):
    from src.services.pg_store import get_kpi_metrics
    from src.services.it_ops import ITOpsService
    return ITOpsService().get_infrastructure_metrics(await asyncio.to_thread(get_kpi_metrics))

@app.get("/api/v1/it/devops")
async def get_it_devops(user: TokenData = Depends(require_page("it"))):
    from src.services.pg_store import get_kpi_metrics
    from src.services.it_ops import ITOpsService
    return ITOpsService().get_devops_metrics(await asyncio.to_thread(get_kpi_metrics))

@app.get("/api/v1/it/health")
async def get_it_health(user: TokenData = Depends(require_page("it"))):
    from src.services.pg_store import get_kpi_metrics
    from src.services.it_ops import ITOpsService
    return ITOpsService().compute_it_health(await asyncio.to_thread(get_kpi_metrics))


# ════════════════════════════════════════════════════════════
# OPERATIONS DOMAIN
# ════════════════════════════════════════════════════════════

@app.get("/api/v1/operations/summary")
async def get_ops_summary(user: TokenData = Depends(require_page("operations"))):
    from src.services.pg_store import get_kpi_metrics
    from src.services.operations import OperationsService
    return OperationsService().get_operations_summary(await asyncio.to_thread(get_kpi_metrics))

@app.get("/api/v1/operations/quality")
async def get_ops_quality(user: TokenData = Depends(require_page("operations"))):
    from src.services.pg_store import get_kpi_metrics
    from src.services.operations import OperationsService
    return OperationsService().get_quality_metrics(await asyncio.to_thread(get_kpi_metrics))

@app.get("/api/v1/operations/production")
async def get_ops_production(user: TokenData = Depends(require_page("operations"))):
    from src.services.pg_store import get_kpi_metrics
    from src.services.operations import OperationsService
    return OperationsService().get_production_metrics(await asyncio.to_thread(get_kpi_metrics))

@app.get("/api/v1/operations/safety")
async def get_ops_safety(user: TokenData = Depends(require_page("operations"))):
    from src.services.pg_store import get_kpi_metrics
    from src.services.operations import OperationsService
    return OperationsService().get_safety_metrics(await asyncio.to_thread(get_kpi_metrics))

@app.get("/api/v1/operations/health")
async def get_ops_health(user: TokenData = Depends(require_page("operations"))):
    from src.services.pg_store import get_kpi_metrics
    from src.services.operations import OperationsService
    return OperationsService().compute_ops_health(await asyncio.to_thread(get_kpi_metrics))


# ════════════════════════════════════════════════════════════
# GROWTH DOMAIN
# ════════════════════════════════════════════════════════════

@app.get("/api/v1/growth/summary")
async def get_growth_summary(user: TokenData = Depends(require_page("analytics"))):
    from src.services.pg_store import get_kpi_metrics
    df = await asyncio.to_thread(get_kpi_metrics, categories=["Growth"])
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
async def get_esg_summary(user: TokenData = Depends(require_page("esg"))):
    from src.services.pg_store import get_kpi_metrics
    df = await asyncio.to_thread(get_kpi_metrics, categories=["ESG"])
    if df.empty:
        return {"score": 0, "environment": {}, "social": {}, "governance": {}, "trends": []}

    latest = df.sort_values("period").groupby("metric").tail(1)

    def _val(keywords):
        mask = latest["metric"].str.lower().apply(lambda m: any(k in m for k in keywords))
        matched = latest[mask]
        return float(matched.iloc[0]["value"]) if not matched.empty else 0

    # Build trends
    trends = []
    for period in sorted(df["period"].unique()):
        p_df = df[df["period"] == period]
        score_rows = p_df[p_df["metric"].str.lower().str.contains("esg score")]
        carbon_rows = p_df[p_df["metric"].str.lower().str.contains("carbon")]
        trends.append({
            "period": period,
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
    # Persist to Postgres too — without this, an admin's change (e.g. deactivating a
    # compromised account) only lived in this one process's in-memory _users_db and
    # silently reverted on the next restart (routine on a free-tier host: idle sleep
    # + cold start), with no indication to the admin that it had been undone.
    from src.services.pg_store import update_user as _pg_update_user
    await asyncio.to_thread(
        _pg_update_user, user_id,
        role=req.role, is_active=req.is_active, preferred_language=req.preferred_language,
    )
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
    until the switch completes. Confirmed live to take 80s+, long enough that
    Cloudflare's free-tier proxy in production can cut the connection with a 502
    before this response comes back, even though the switch succeeds server-side a
    few seconds later. Prefer POST .../async + GET .../{job_id} below for any caller
    behind that proxy; this synchronous form is kept for callers that set their own
    longer timeout (e.g. local dev, or scripts run directly against the backend)."""
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


# ════════════════════════════════════════════════════════════
# CHAT HISTORY & SESSIONS (PostgreSQL)
# ════════════════════════════════════════════════════════════

@app.get("/api/v1/chat/sessions")
async def get_chat_sessions(user: TokenData = Depends(get_current_user)):
    try:
        from src.services.pg_store import get_user_sessions
        sessions = await asyncio.to_thread(get_user_sessions, user.user_id, limit=50)
        return {"sessions": sessions}
    except Exception as e:
        return {"sessions": [], "error": str(e)}


@app.get("/api/v1/chat/sessions/{session_id}/messages")
async def get_chat_messages(session_id: str, user: TokenData = Depends(get_current_user)):
    try:
        from src.services.pg_store import get_session_messages
        messages = await asyncio.to_thread(get_session_messages, session_id, user.user_id)
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
        # Match the (working) chat retrieval path: pass a language so the vector-store query
        # filters consistently instead of returning nothing.
        rag = _get_shared_rag()
        hits = rag._retrieve_documents(q, top_k=n, language=getattr(user, "language", None) or "en")
        if not hits:  # last-resort: retry language-agnostic
            hits = rag._retrieve_documents(q, top_k=n)
        results = [
            {"title": title, "content": (content or "")[:600], "score": round(score, 4)}
            for title, content, score in hits
        ]
        return {"results": results, "query": q, "count": len(results)}
    except Exception as e:
        return {"results": [], "query": q, "error": str(e)}


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

        from src.services.omnismart_chatbot import get_persona_factory
        factory = get_persona_factory()
        # Reuse the client's session when provided (so reconnects continue the same thread);
        # otherwise start a new one. Persisted lazily on the first real message.
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
            # Use language from message if provided, otherwise fall back to user language
            language = data.get("language") or user.language
            # A real chat turn can genuinely take 60-100s+ under cold retrieval — see
            # BENCHMARK.md. A proxy sitting in front of this socket (Cloudflare or
            # otherwise) can treat a connection with no traffic in either direction for
            # too long as dead, same risk a slow synchronous REST call has. Unlike REST,
            # the socket is already open for the whole turn, so the fix here is a
            # periodic status frame while the real work runs in the background — resets
            # any such idle-timeout AND gives the client something to show instead of
            # silence, rather than needing the job+poll pattern REST callers get instead.
            chat_task = asyncio.create_task(asyncio.to_thread(
                factory.chat,
                message=message, user_role=user.role,
                persona_override=persona_override, language=language, history=history,
            ))
            keepalive_interval = float(os.getenv("WS_CHAT_KEEPALIVE_SECONDS", "12"))
            while not chat_task.done():
                try:
                    await asyncio.wait_for(asyncio.shield(chat_task), timeout=keepalive_interval)
                except asyncio.TimeoutError:
                    try:
                        await websocket.send_json({"type": "status", "note": "still working..."})
                    except Exception:
                        break  # client gone — let the outer try/except handle cleanup
            result = await chat_task
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": result["response"]})
            # Persist the turn so it appears in history with a real title (store_message
            # auto-titles the session from the first user message). Best-effort.
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
                "persona_used": result["persona_used"],
                "persona_display": result.get("persona_display", ""),
                "tokens_used": result.get("tokens_used", 0),
                "latency_ms": result.get("latency_ms", 0),
                "sources": result.get("sources", []),
                "blocks": _structure_answer(result["response"]),
            })
    except WebSocketDisconnect:
        log.info("WebSocket client disconnected")
    except Exception as e:
        log.error("WebSocket error: %s", e)


# ════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════

def _load_chat_history(user_id: str, session_id: str) -> List[Dict[str, str]]:
    """Was previously dead code AND broken: get_conversation_history()'s query aliases
    role AS user_message, content AS ai_response — both columns are truthy on every row
    regardless of who sent it, so the old version here pushed a bogus {"role": "user",
    "content": "assistant"} turn (the literal role string, not real content) for every
    row. get_session_messages() is the function this codebase already uses correctly
    for this exact table (see GET .../messages) — same ownership-scoped query, real
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

    A split deploy (Vercel frontend + this API) never hit it because vercel.json already
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
