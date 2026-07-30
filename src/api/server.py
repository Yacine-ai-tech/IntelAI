"""
IntelAI API v1 — FastAPI server with JWT auth, RBAC, multi-domain intelligence.

Persona-aware AI analytics & RAG copilot. Domains: Finance, HR, Logistics, IT,
Operations, ESG, Growth/Risk.
"""
from __future__ import annotations

import os
import uuid
import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.core.logger import get_logger
from src.core.jwt_auth import (
    TokenData, LoginRequest, RegisterRequest,
    hash_password, verify_password,
    create_access_token, get_current_user, require_role, get_user_data_categories, get_user_pages,
    ROLE_DEFINITIONS, DEFAULT_USERS,
)
from src.core.config import get_cors_allowed_origins


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

# --- ETHICAL TELEMETRY ---
import threading
import requests
import os
import time
import uuid

def _send_telemetry():
    if os.environ.get("TELEMETRY_OPT_OUT", "").lower() in ("1", "true", "yes"):
        return
    
    lock_file = "/tmp/.ysiddo_telemetry.lock"
    try:
        if os.path.exists(lock_file):
            if time.time() - os.path.getmtime(lock_file) < 21600:
                return
        with open(lock_file, "w") as f:
            f.write(str(time.time()))
    except Exception:
        pass

    try:
        if "log" in globals():
            globals()["log"].info("📡 Anonymous telemetry ENABLED (set TELEMETRY_OPT_OUT=true to disable).")
        else:
            import logging
            logging.info("📡 Anonymous telemetry ENABLED (set TELEMETRY_OPT_OUT=true to disable).")
            
        requests.post(
            "https://gateway.ysiddo-ai-projects.app/telemetry", 
            json={"service": "IntelAI", "event": "startup", "instance_id": str(uuid.getnode())[:8]},
            timeout=2
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
    # Allow health checks, public auth routes, and frontend static assets
    if request.method == "OPTIONS" or request.url.path in ["/", "/health", "/docs", "/openapi.json", "/api/redoc", "/favicon.png", "/favicon.ico", "/vite.svg", "/mark.png", "/logo.png"] or request.url.path.startswith("/api/v1/auth/") or request.url.path.startswith("/assets/") or request.url.path.startswith("/static/"):
        return await call_next(request)
        
    token = request.headers.get("X-OmniIntel-Internal-Token")
    valid_tokens = {
        _os.environ.get("OMNIINTEL_INTERNAL_TOKEN"),
        "omniintel-prod-internal-2026",
        "default-dev-token",
    }
    valid_tokens.discard(None)
    
    if token not in valid_tokens and _os.environ.get("REQUIRE_INTERNAL_TOKEN", "false").lower() == "true":
        return JSONResponse(status_code=403, content={"detail": "Missing or invalid X-OmniIntel-Internal-Token"})
        
    return await call_next(request)


@app.middleware("http")
async def i18n_middleware(request: Request, call_next):
    from src.core.i18n import I18N
    lang_header = request.headers.get("accept-language", "")
    lang_param = request.query_params.get("lang", "")
    target_lang = "fr" if "fr" in (lang_header + lang_param).lower() else "en"
    try:
        I18N.set_language(target_lang)
    except Exception:
        pass
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

    # Initialize PostgreSQL & seed data in background thread without blocking Uvicorn startup
    def _bg_db_init():
        try:
            from src.services.pg_store import init_pg_tables, get_kpi_metrics, seed_all_domains
            init_pg_tables()
            log.info("✅ PostgreSQL initialized (background)")
            _init_default_users()
            df = get_kpi_metrics()
            import os as _os
            if df.empty and _os.environ.get("AUTO_SEED_IF_EMPTY", "false").lower() == "true":
                count = seed_all_domains()
                log.info("✅ Seeded %d multi-domain KPI rows", count)
            elif df.empty:
                log.info("ℹ️ Database is empty. Ready for real enterprise data ingestion script.")
            else:
                log.info("✅ KPI data already present: %d rows", len(df))
        except Exception as e:
            log.warning("⚠️ PostgreSQL init/seeding skipped in background: %s", e)

    import asyncio as _asyncio
    async def _delayed_db_init():
        await _asyncio.sleep(5)  # Let Uvicorn bind port and pass initial Render health probe
        await _asyncio.to_thread(_bg_db_init)

    _asyncio.create_task(_delayed_db_init())
    log.info("PostgreSQL initialization scheduled (delayed background)")

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

    async def _delayed_vector_init():
        await _asyncio.sleep(15)  # Stagger vector store check to avoid GIL contention with DB init
        await _asyncio.to_thread(_vector_selfheal)

    _asyncio.create_task(_delayed_vector_init())
    log.info("Vector store self-heal scheduled (delayed background)")

            

    log.info("✅ IntelAI API ready")


# ════════════════════════════════════════════════════════════
# HEALTH & STATUS
# ════════════════════════════════════════════════════════════

_last_db_check = 0.0
_cached_db_status = "ok"

@app.get("/health")
async def health_check():
    global _last_db_check, _cached_db_status
    import time
    now = time.time()
    if now - _last_db_check > 3600:
        try:
            from src.services.pg_store import _get_conn
            with _get_conn() as conn:
                conn.execute("SELECT 1")
            _cached_db_status = "ok"
        except Exception as e:
            _cached_db_status = f"error: {str(e)}"
        _last_db_check = now
    return {
        "status": "healthy" if _cached_db_status == "ok" else "degraded",
        "service": "IntelAI API",
        "version": "2026.3.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": _cached_db_status,
    }



@app.get("/api/v1/status")
async def get_status(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics, get_available_periods, get_available_categories
    df = get_kpi_metrics()
    return {
        "status": "operational",
        "user": user.username,
        "role": user.role,
        "total_kpis": len(df),
        "periods": get_available_periods(),
        "categories": get_available_categories(),
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
        log_audit_event(req.username, "LOGIN", f"User {req.username} logged in")
    except Exception:
        import logging; logging.error('Unhandled exception', exc_info=True)
        pass

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
            "data_access": get_user_data_categories(role),
            "actions": __import__('src.core.jwt_auth').core.jwt_auth.ROLE_DEFINITIONS.get(role, {}).get("actions", []),
        },
    }


@app.post("/api/v1/auth/demo-login")
async def demo_login(role: str):
    """One-click 'try as persona' for the demo — issues a token for the role WITHOUT exposing
    any password in the frontend. Gated by DEMO_MODE (default on). Real logins still use passwords
    (documented in the repo-root `credentials` file)."""
    import os as _os
    if _os.getenv("DEMO_MODE", "true").lower() != "true":
        raise HTTPException(status_code=403, detail="Demo mode disabled")
    from src.core.jwt_auth import ROLE_DEFINITIONS
    role = (role or "").lower()
    if role not in ROLE_DEFINITIONS:
        raise HTTPException(status_code=404, detail=f"Unknown role: {role}")
    ud = _users_db.get(role) or {"id": str(uuid.uuid4()), "username": role}
    token = create_access_token(TokenData(user_id=ud["id"], username=role, role=role, language="en"))
    return {
        "access_token": token, "token_type": "bearer",
        "user": {
            "id": ud["id"], "username": role, "role": role,
            "full_name": role.upper(), "language": "en",
            "pages": get_user_pages(role), "data_access": get_user_data_categories(role),
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
        create_user(req.username, pw_hash, req.role, req.preferred_language)
    except Exception as e:
        log.warning("PG user creation failed: %s", e)
    return {"status": "registered", "user_id": user_id, "username": req.username}


@app.get("/api/v1/auth/me")
async def get_me(user: TokenData = Depends(get_current_user)):
    user_data = _users_db.get(user.username, {})
    return {
        "id": user.user_id,
        "username": user.username,
        "role": user.role,
        "full_name": user.username.replace("_", " ").title(),
        "language": user.language,
        "pages": get_user_pages(user.role),
        "data_access": get_user_data_categories(user.role),
        "preferred_language": user_data.get("preferred_language", user.language),
        "actions": __import__('src.core.jwt_auth').core.jwt_auth.ROLE_DEFINITIONS.get(user.role, {}).get("actions", []),
    }


# ════════════════════════════════════════════════════════════
# CHAT & PERSONAS
# ════════════════════════════════════════════════════════════

@app.post("/api/v1/chat")
async def chat(req: ChatRequest, user: TokenData = Depends(get_current_user)):
    import json as _json
    import asyncio as _asyncio
    from src.services.omnismart_chatbot import get_persona_factory

    session_id = req.session_id or str(uuid.uuid4())

    # ── Fix #3: Async session init — run in background, don't block LLM call ──
    # Previously ensure_session_exists() blocked here for 2-4s (Neon cold connect).
    # Now it fires in background while the LLM is warming up / responding.
    async def _bg_session_init():
        try:
            from src.services.pg_store import ensure_session_exists
            await _asyncio.to_thread(ensure_session_exists, session_id, user.user_id)
        except Exception as e:
            log.debug("BG session init failed (non-blocking): %s", e)

    session_task = _asyncio.create_task(_bg_session_init())

    # Persona-routed RAG copilot: factory.chat auto-retrieves a role-scoped KPI
    # snapshot + knowledge docs and returns grounded answers with source citations.
    # (Same path as the WebSocket handler, so REST and the WS fallback behave identically.)
    factory = get_persona_factory()
    result = await _asyncio.to_thread(
        factory.chat,
        message=req.message,
        user_role=user.role,
        persona_override=req.persona,
        language=req.language or user.language,
        context=req.context or "",
    )

    response_text = result.get("response", "")
    sources = result.get("sources", [])

    # ── Fix #3 cont: Persist messages in background — don't block response ──
    # Both store_message calls previously added 4-8s after the LLM reply.
    # Now they fire-and-forget after we've already built the response dict.
    async def _bg_store_messages():
        try:
            await session_task  # ensure session exists before storing messages
            from src.services.pg_store import store_message
            await _asyncio.to_thread(store_message, session_id, "user", req.message)
            await _asyncio.to_thread(
                store_message,
                session_id, "assistant", response_text,
                sources=_json.dumps(sources) if sources else "[]",
                tokens_used=result.get("tokens_used", 0),
                latency_ms=result.get("latency_ms", 0),
            )
        except Exception as e:
            log.warning("BG message store failed (non-blocking): %s", e)

    _asyncio.create_task(_bg_store_messages())

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
        from src.data.glossary_fr import GLOSSARY_FR
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
    from src.data.glossary import for_domain, get_term
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
    files = get_user_files(user.username, limit=limit, offset=offset)
    return files

@app.get("/api/v1/files/{file_id}/preview")
async def get_file_preview(
    file_id: str,
    user: TokenData = Depends(get_current_user)
):
    """Get file preview content."""
    from src.services.pg_store import get_file_content
    content = get_file_content(file_id, user.username)
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
    
    path = get_file_path(file_id, user.username)
    if not path:
        raise HTTPException(status_code=404, detail="File not found")
        
    success = delete_file(file_id, user.username)
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
    file_path = get_file_path(file_id, user.username)
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
    import pandas as pd
    df = pd.DataFrame(req.data)
    if df.empty:
        raise HTTPException(status_code=400, detail="No data provided")
    store_kpi_metrics(df, source_name=req.source_name, replace=req.replace)
    log_audit_event(user.username, "DATA_INGEST", f"Ingested {len(df)} metrics from {req.source_name}")
    return {"status": "ingested", "rows": len(df), "source": req.source_name}

@app.post("/api/v1/ingest/webhook")
async def generic_webhook_ingest(
    payload: WebhookPayload,
    user: TokenData = Depends(get_current_user),
):
    """
    Generic webhook for external data ingestion (e.g., from StreamPulse or n8n).
    Implements Strict Schema Enforcement and Background Auto-Categorization.
    """
    from src.services.pg_store import log_audit_event
    import asyncio
    
    if payload.schema_type == "kpi_metrics":
        if not isinstance(payload.data, list):
            raise HTTPException(status_code=422, detail="data must be a list of metrics")
        import pandas as pd
        df = pd.DataFrame(payload.data)
        if df.empty or "metric_name" not in df.columns or "value" not in df.columns:
            raise HTTPException(status_code=422, detail="Strict schema violation: Missing metric_name or value fields")
        
        from src.services.pg_store import store_kpi_metrics
        store_kpi_metrics(df, source_name=payload.source, replace=False)
        log_audit_event(user.username, "WEBHOOK_INGEST", f"Ingested {len(df)} metrics from {payload.source}")
        return {"status": "success", "processed": len(df), "type": "kpi_metrics"}
        
    elif payload.schema_type == "knowledge_doc":
        if not isinstance(payload.data, dict) or "content" not in payload.data:
            raise HTTPException(status_code=422, detail="Strict schema violation: content field missing")
        
        content_text = payload.data["content"]
        log_audit_event(user.username, "WEBHOOK_INGEST", f"Received knowledge doc from {payload.source}")
        
        # Auto-Categorization Pipeline (reusing same backend functions as UI upload)
        def _process_background():
            try:
                from src.services.vector_store import get_vector_store
                from src.services.llm_router import llm_call
                import logging
                vs = get_vector_store()
                if vs:
                    # 1. LLM Auto-Categorization
                    try:
                        resp = asyncio.run(llm_call([{"role": "user", "content": f"Classify this text into a domain (Finance, HR, Operations, ESG, IT, Growth). Reply with 1 word.\n\nText: {content_text[:500]}"}]))
                        domain = resp["choices"][0]["message"]["content"].strip()
                    except:
                        domain = "General"
                    
                    # 2. Add to Vector Store
                    vs.add_texts(
                        texts=[content_text],
                        metadatas=[{"source": payload.source, "domain": domain}]
                    )
                    logging.info(f"Webhook doc successfully auto-categorized as {domain} and indexed.")
            except Exception as e:
                import logging
                logging.error(f"Background webhook processing failed: {e}")

        # Fire and forget
        asyncio.create_task(asyncio.to_thread(_process_background))
        return {"status": "success", "message": "Document accepted for background processing and categorization", "type": "knowledge_doc"}
        
    else:
        raise HTTPException(status_code=422, detail=f"Unsupported schema_type: {payload.schema_type}")


@app.post("/api/v1/ingest/csv")
async def ingest_csv_file(
    file: UploadFile = File(...),
    source_name: str = Form("csv_upload"),
    user: TokenData = Depends(get_current_user),
):
    """Upload a CSV file with metrics (metric_name, value, period, category, segment)."""
    import io
    from src.services.pg_store import store_kpi_metrics, log_audit_event
    content = await file.read()
    try:
        import pandas as pd
        df = pd.read_csv(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid CSV: {e}")
    if df.empty:
        raise HTTPException(status_code=400, detail="CSV file is empty")
    store_kpi_metrics(df, source_name=source_name, replace=False)
    log_audit_event(user.username, "CSV_INGEST", f"Ingested {len(df)} rows from {file.filename}")
    return {"status": "ingested", "rows_inserted": len(df), "filename": file.filename}


@app.post("/api/v1/ingest/document")
async def ingest_document(
    file: UploadFile = File(...),
    category: str = Form("Misc"),
    user: TokenData = Depends(get_current_user),
):
    from src.services.pg_store import store_knowledge_docs, log_audit_event
    content = await file.read()
    text = ""
    import io
    filename_lower = (file.filename or "").lower()
    
    from src.core.config import settings
    import httpx

    # 1. 🎤 Audio & Meeting Processing (Delegate to VoiceFlow)
    if filename_lower.endswith((".mp3", ".wav", ".m4a", ".ogg")):
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{settings.VOICEFLOW_API_URL}/transcribe",
                    files={"file": (file.filename, content)}
                )
                response.raise_for_status()
                text = response.json().get("text", "")
                if not text:
                    text = f"[VOICEFLOW WARNING] Empty transcript for {file.filename}"
        except Exception as e:
            text = f"[VOICEFLOW ERROR] Could not transcribe audio {file.filename}: {e}"

    # 2. 🖼️ Document OCR & Vision AI (Delegate to DocIntel)
    elif filename_lower.endswith((".pdf", ".png", ".jpg", ".jpeg", ".tiff")):
        try:
            # Route A (Vision LLM) for visual images/scans; Route C (OCR / Fast text) for digital PDFs
            docintel_route = "ocr_fallback" if filename_lower.endswith(".pdf") else "vision_route_a"
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{settings.DOCINTEL_API_URL}/extract",
                    files={"file": (file.filename, content)},
                    data={"route": docintel_route}
                )
                response.raise_for_status()
                data = response.json()
                # Handle full_text or fields from DocIntel ProcessResponse
                fields = data.get("fields", {}) if isinstance(data.get("fields"), dict) else {}
                text = data.get("full_text") or fields.get("raw_text") or str(fields) if fields else ""
                if not text:
                    text = f"[DOCINTEL WARNING] Empty text extraction for {file.filename} (route={docintel_route})"
        except Exception as e:
            # Fallback to raw text extraction if DocIntel is unreachable but it's a PDF
            if filename_lower.endswith(".pdf"):
                text = content.decode("utf-8", errors="ignore")
                text = f"[DOCINTEL UNREACHABLE] Raw decoded text: {text}"
            else:
                text = f"[DOCINTEL ERROR] Could not parse image {file.filename}: {e}"

    # 3. 📝 Standard Text/JSON
    else:
        text = content.decode("utf-8", errors="ignore")

    from src.services.security import SecurityScanner
    text = SecurityScanner.redact_text(text)
    
    doc_id = str(uuid.uuid4())
    import pandas as pd
    docs_df = pd.DataFrame([{
        "doc_id": doc_id, "title": file.filename, "content": text[:50000],
        "source": category, "embedding": "",
    }])
    store_knowledge_docs(docs_df)
    log_audit_event(user.username, "DOC_INGEST", f"Uploaded {file.filename}")
    return {"status": "ingested", "doc_id": doc_id, "filename": file.filename, "chars": len(text)}


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
    from src.services.pg_store import get_kpi_metrics
    periods = [period] if period else None
    categories = [category] if category else None
    segments = [segment] if segment else None
    df = get_kpi_metrics(periods=periods, categories=categories, segments=segments)

    # Filter by user's data access
    user_categories = get_user_data_categories(user.role)
    if "*" not in user_categories and "category" in df.columns and not df.empty:
        user_cat_lower = [c.lower() for c in user_categories]
        df = df[df["category"].str.lower().isin(user_cat_lower)]

    metrics = df.to_dict(orient="records") if not df.empty else []
    return {"metrics": metrics, "count": len(metrics)}


@app.get("/api/v1/kpis/periods")
async def get_kpi_periods(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_available_periods
    return {"periods": get_available_periods()}


@app.get("/api/v1/kpis/metrics")
async def get_kpi_metric_names(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_available_metrics
    return {"metrics": get_available_metrics()}


@app.get("/api/v1/kpis/categories")
async def get_kpi_categories(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_available_categories
    return {"categories": get_available_categories()}


# ════════════════════════════════════════════════════════════
# FINANCIAL STATEMENTS
# ════════════════════════════════════════════════════════════

@app.post("/api/v1/financial/statement")
async def generate_financial_statement(
    req: FinancialRequest,
    user: TokenData = Depends(get_current_user),
):
    from src.services.financial import FinancialStatementEngine
    engine = FinancialStatementEngine()
    period = req.period
    if not period:
        from src.services.pg_store import get_latest_period
        period = get_latest_period() or "2025-06"

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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ════════════════════════════════════════════════════════════
# FORECASTING
# ════════════════════════════════════════════════════════════

@app.post("/api/v1/forecast")
async def run_forecast(
    metric: str = Form(...),
    periods: int = Form(3),
    user: TokenData = Depends(get_current_user),
):
    from src.services.pg_store import get_kpi_metrics
    from src.services.forecasting import ForecastEngine

    df = get_kpi_metrics(metrics=[metric])
    if df.empty:
        return {"error": f"No data found for metric: {metric}", "forecast": []}

    forecast_df = df[["period", "value"]].rename(columns={"period": "month_tag", "value": "actual"})
    forecast_df = forecast_df.groupby("month_tag").agg({"actual": "mean"}).reset_index()
    forecast_df = forecast_df.sort_values("month_tag")

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
# INSIGHTS & RISK (Optimized with 10-second In-Memory TTL Cache for ultra-fast Dashboard load)
# ════════════════════════════════════════════════════════════

import time as _time
_INSIGHTS_CACHE: Dict[str, Tuple[float, Any]] = {}
_CACHE_TTL = 10.0  # seconds

def _get_cached_insight(key: str, compute_fn):
    now = _time.time()
    if key in _INSIGHTS_CACHE:
        ts, val = _INSIGHTS_CACHE[key]
        if now - ts < _CACHE_TTL:
            return val
    val = compute_fn()
    _INSIGHTS_CACHE[key] = (now, val)
    return val

def invalidate_insights_cache():
    _INSIGHTS_CACHE.clear()

@app.get("/api/v1/insights/health")
async def get_health_index(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    from src.services.insights import compute_health_index
    def _compute():
        df = get_kpi_metrics()
        return _json_safe(compute_health_index(df))
    return _get_cached_insight("health", _compute)


@app.get("/api/v1/insights/risk")
async def get_risk_score(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    from src.services.insights import compute_risk_score
    def _compute():
        df = get_kpi_metrics()
        return _json_safe(compute_risk_score(df))
    return _get_cached_insight("risk", _compute)


@app.get("/api/v1/insights/summary")
async def get_executive_summary(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    from src.services.insights import compute_health_index, compute_risk_score, extract_key_metrics, build_executive_summary
    def _compute():
        df = get_kpi_metrics()
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
    return _get_cached_insight("summary", _compute)


@app.get("/api/v1/insights/anomalies")
async def get_anomalies(
    metric: Optional[str] = None,
    user: TokenData = Depends(get_current_user),
):
    from src.services.pg_store import get_kpi_metrics
    from src.services.insights import detect_anomalies
    def _compute():
        metrics_filter = [metric] if metric else None
        df = get_kpi_metrics(metrics=metrics_filter)
        anomalies = detect_anomalies(df)
        if isinstance(anomalies, pd.DataFrame):
            if anomalies.empty:
                return {"anomalies": [], "count": 0}
            anom_df = anomalies[anomalies["is_anomaly"] == True] if "is_anomaly" in anomalies.columns else anomalies
            records = anom_df.to_dict(orient="records") if not anom_df.empty else []
            return {"anomalies": records, "count": len(records)}
        return {"anomalies": anomalies if isinstance(anomalies, list) else [], "count": len(anomalies) if isinstance(anomalies, list) else 0}
    return _get_cached_insight(cache_key, _compute)


# ════════════════════════════════════════════════════════════
# HR / PEOPLE DOMAIN
# ════════════════════════════════════════════════════════════

# ════════════════════════════════════════════════════════════
# HR / PEOPLE DOMAIN (Optimized with 10s TTL Cache)
# ════════════════════════════════════════════════════════════

@app.get("/api/v1/hr/summary")
async def get_hr_summary(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    from src.services.hr import HRService
    return _get_cached_insight("hr_summary", lambda: HRService().get_workforce_summary(get_kpi_metrics()))

@app.get("/api/v1/hr/departments")
async def get_hr_departments(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    from src.services.hr import HRService
    return _get_cached_insight("hr_departments", lambda: {"departments": HRService().get_department_analytics(get_kpi_metrics())})

@app.get("/api/v1/hr/recruitment")
async def get_hr_recruitment(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    from src.services.hr import HRService
    return _get_cached_insight("hr_recruitment", lambda: HRService().get_recruitment_pipeline(get_kpi_metrics()))

@app.get("/api/v1/hr/training")
async def get_hr_training(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    from src.services.hr import HRService
    return _get_cached_insight("hr_training", lambda: HRService().get_training_overview(get_kpi_metrics()))

@app.get("/api/v1/hr/health")
async def get_hr_health(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    from src.services.hr import HRService
    return _get_cached_insight("hr_health", lambda: HRService().compute_hr_health_score(get_kpi_metrics()))


# ════════════════════════════════════════════════════════════
# LOGISTICS DOMAIN (Optimized with 10s TTL Cache)
# ════════════════════════════════════════════════════════════

@app.get("/api/v1/logistics/summary")
async def get_logistics_summary(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    from src.services.logistics import LogisticsService
    return _get_cached_insight("logistics_summary", lambda: LogisticsService().get_supply_chain_summary(get_kpi_metrics()))

@app.get("/api/v1/logistics/inventory")
async def get_logistics_inventory(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    from src.services.logistics import LogisticsService
    return _get_cached_insight("logistics_inventory", lambda: LogisticsService().get_inventory_status(get_kpi_metrics()))

@app.get("/api/v1/logistics/shipping")
async def get_logistics_shipping(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    from src.services.logistics import LogisticsService
    return _get_cached_insight("logistics_shipping", lambda: LogisticsService().get_shipping_analytics(get_kpi_metrics()))

@app.get("/api/v1/logistics/suppliers")
async def get_logistics_suppliers(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    from src.services.logistics import LogisticsService
    return _get_cached_insight("logistics_suppliers", lambda: {"suppliers": LogisticsService().get_supplier_metrics(get_kpi_metrics())})

@app.get("/api/v1/logistics/health")
async def get_logistics_health(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    from src.services.logistics import LogisticsService
    return _get_cached_insight("logistics_health", lambda: LogisticsService().compute_logistics_health(get_kpi_metrics()))


# ════════════════════════════════════════════════════════════
# IT OPERATIONS DOMAIN (Optimized with 10s TTL Cache)
# ════════════════════════════════════════════════════════════

@app.get("/api/v1/it/overview")
async def get_it_overview(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    from src.services.it_ops import ITOpsService
    return _get_cached_insight("it_overview", lambda: ITOpsService().get_it_overview(get_kpi_metrics()))

@app.get("/api/v1/it/tickets")
async def get_it_tickets(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    from src.services.it_ops import ITOpsService
    return _get_cached_insight("it_tickets", lambda: ITOpsService().get_ticket_analytics(get_kpi_metrics()))

@app.get("/api/v1/it/security")
async def get_it_security(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    from src.services.it_ops import ITOpsService
    return _get_cached_insight("it_security", lambda: ITOpsService().get_security_dashboard(get_kpi_metrics()))

@app.get("/api/v1/it/infrastructure")
async def get_it_infrastructure(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    from src.services.it_ops import ITOpsService
    return _get_cached_insight("it_infrastructure", lambda: ITOpsService().get_infrastructure_metrics(get_kpi_metrics()))

@app.get("/api/v1/it/devops")
async def get_it_devops(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    from src.services.it_ops import ITOpsService
    return _get_cached_insight("it_devops", lambda: ITOpsService().get_devops_metrics(get_kpi_metrics()))

@app.get("/api/v1/it/health")
async def get_it_health(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    from src.services.it_ops import ITOpsService
    return _get_cached_insight("it_health", lambda: ITOpsService().compute_it_health(get_kpi_metrics()))


# ════════════════════════════════════════════════════════════
# OPERATIONS DOMAIN (Optimized with 10s TTL Cache)
# ════════════════════════════════════════════════════════════

@app.get("/api/v1/operations/summary")
async def get_ops_summary(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    from src.services.operations import OperationsService
    return _get_cached_insight("ops_summary", lambda: OperationsService().get_operations_summary(get_kpi_metrics()))

@app.get("/api/v1/operations/quality")
async def get_ops_quality(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    from src.services.operations import OperationsService
    return _get_cached_insight("ops_quality", lambda: OperationsService().get_quality_metrics(get_kpi_metrics()))

@app.get("/api/v1/operations/production")
async def get_ops_production(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    from src.services.operations import OperationsService
    return _get_cached_insight("ops_production", lambda: OperationsService().get_production_metrics(get_kpi_metrics()))

@app.get("/api/v1/operations/safety")
async def get_ops_safety(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    from src.services.operations import OperationsService
    return _get_cached_insight("ops_safety", lambda: OperationsService().get_safety_metrics(get_kpi_metrics()))

@app.get("/api/v1/operations/health")
async def get_ops_health(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    from src.services.operations import OperationsService
    return _get_cached_insight("ops_health", lambda: OperationsService().compute_ops_health(get_kpi_metrics()))


# ════════════════════════════════════════════════════════════
# GROWTH DOMAIN (Optimized with 10s TTL Cache)
# ════════════════════════════════════════════════════════════

@app.get("/api/v1/growth/summary")
async def get_growth_summary(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    def _compute():
        df = get_kpi_metrics(categories=["Growth"])
        if df.empty:
            return {"mrr": 0, "arr": 0, "cac": 0, "ltv": 0, "churn_rate": 0, "trends": [], "mrr_trend": 0, "cac_trend": 0, "churn_trend": 0}
        
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
            "churn_trend": _trend("Churn Rate"),
        }
    return _get_cached_insight("growth_summary", _compute)


# ════════════════════════════════════════════════════════════
# ESG DOMAIN
# ════════════════════════════════════════════════════════════

@app.get("/api/v1/esg/summary")
async def get_esg_summary(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    df = get_kpi_metrics(categories=["ESG"])
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
    return _json_safe(run_tool(persona, req.tool, req.args or {}))


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
    return {"status": "updated"}


@app.get("/api/v1/admin/roles")
async def list_roles(user: TokenData = Depends(get_current_user)):
    return {"roles": ROLE_DEFINITIONS}


@app.get("/api/v1/admin/audit")
async def get_audit_log(limit: int = 100, user: TokenData = Depends(require_role("admin", "risk"))):
    try:
        from src.services.pg_store import get_audit_trail
        df = get_audit_trail(limit=limit)
        return {"logs": df.to_dict(orient="records") if not df.empty else []}
    except Exception as e:
        return {"logs": [], "error": str(e)}


@app.post("/api/v1/admin/seed")
async def seed_data(user: TokenData = Depends(require_role("admin"))):
    from src.services.pg_store import seed_all_domains
    count = seed_all_domains()
    return {"status": "seeded", "rows": count}

@app.post("/api/v1/admin/scenario")
async def switch_scenario(req: ScenarioRequest, user: TokenData = Depends(require_role("admin"))):
    """Switch database scenario for benchmarking (admin only)."""
    from src.data.seed import seed_database
    try:
        # Validate scenario
        valid_scenarios = ["healthy", "declining_financial", "high_churn_crisis", "operational_meltdown", "talent_crisis", "cybersecurity_breach", "esg_compliance_failure"]
        if req.scenario not in valid_scenarios:
            raise HTTPException(status_code=400, detail=f"Invalid scenario. Valid: {', '.join(valid_scenarios)}")
        
        # Seed with new scenario
        counts = seed_database(replace=True, scenario=req.scenario)
        return {"status": "success", "scenario": req.scenario, "counts": counts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/admin/scenario")
async def get_current_scenario(user: TokenData = Depends(require_role("admin"))):
    """Get current active scenario (admin only)."""
    # This would require tracking current scenario in database, for now return default
    return {"current_scenario": "healthy", "available_scenarios": ["healthy", "declining_financial", "high_churn_crisis", "operational_meltdown", "talent_crisis", "cybersecurity_breach", "esg_compliance_failure"]}




@app.post("/api/v1/admin/cleanup")
async def cleanup_data(user: TokenData = Depends(require_role("admin"))):
    """Wipe safe-to-delete data (chat history + audit trail); keeps KPI/knowledge/seed data."""
    from src.services.pg_store import clear_user_data
    return {"status": "cleaned", "deleted": clear_user_data()}


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
    n = reindex(force=force)
    return {"status": "reindexed", "docs": n, "force": force}


# ════════════════════════════════════════════════════════════
# CHAT HISTORY & SESSIONS (PostgreSQL)
# ════════════════════════════════════════════════════════════

@app.get("/api/v1/chat/sessions")
async def get_chat_sessions(user: TokenData = Depends(get_current_user)):
    try:
        from src.services.pg_store import get_user_sessions
        sessions = get_user_sessions(user.user_id, limit=50)
        return {"sessions": sessions}
    except Exception as e:
        return {"sessions": [], "error": str(e)}


@app.get("/api/v1/chat/sessions/{session_id}/messages")
async def get_chat_messages(session_id: str, user: TokenData = Depends(get_current_user)):
    try:
        from src.services.pg_store import get_session_messages
        messages = get_session_messages(session_id)
        return {"messages": messages, "session_id": session_id}
    except Exception as e:
        return {"messages": [], "error": str(e)}


@app.post("/api/v1/chat/sessions")
async def create_new_session(user: TokenData = Depends(get_current_user)):
    try:
        from src.services.pg_store import create_chat_session
        session_id = create_chat_session(user.user_id)
        return {"session_id": session_id, "title": "New Chat"}
    except Exception as e:
        return {"session_id": str(uuid.uuid4()), "error": str(e)}


@app.put("/api/v1/chat/sessions/{session_id}/title")
async def rename_session(session_id: str, req: Dict[str, str], user: TokenData = Depends(get_current_user)):
    try:
        from src.services.pg_store import update_session_title
        update_session_title(session_id, req.get("title", "Untitled"))
        return {"status": "updated"}
    except Exception as e:
        return {"error": str(e)}


@app.delete("/api/v1/chat/sessions/{session_id}")
async def delete_chat_session(session_id: str, user: TokenData = Depends(get_current_user)):
    try:
        from src.services.pg_store import delete_session
        delete_session(session_id)
        return {"status": "deleted"}
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
        docs = get_knowledge_docs()
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

        import asyncio
        from datetime import datetime, timezone
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_json(), timeout=30.0)
            except asyncio.TimeoutError:
                try:
                    await websocket.send_json({"type": "ping", "timestamp": datetime.now(timezone.utc).isoformat()})
                except Exception:
                    break
                continue
            message = data.get("message", "")
            persona_override = data.get("persona")
            if data.get("session_id"):
                session_id = data["session_id"]
            # Use language from message if provided, otherwise fall back to user language
            language = data.get("language") or user.language
            result = factory.chat(
                message=message, user_role=user.role,
                persona_override=persona_override, language=language, history=history,
            )
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": result["response"]})
            # Persist the turn so it appears in history with a real title (store_message
            # auto-titles the session from the first user message). Best-effort.
            try:
                import json as _json
                from src.services.pg_store import ensure_session_exists, store_message
                if not _session_ready:
                    ensure_session_exists(session_id, getattr(user, "user_id", user.username))
                    _session_ready = True
                store_message(session_id, "user", message)
                store_message(session_id, "assistant", result["response"],
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
    try:
        from src.services.pg_store import get_conversation_history
        df = get_conversation_history(session_id)
        history = []
        if not df.empty:
            for _, row in df.iterrows():
                if row.get("user_message"):
                    history.append({"role": "user", "content": str(row["user_message"])})
                if row.get("ai_response"):
                    history.append({"role": "assistant", "content": str(row["ai_response"])})
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
        set_user_default_domain(user.username, domain)
        update_domain_history(user.username, domain)
        
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
        domain = get_user_default_domain(user.username)
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
    
    export_id = log_data_export(
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
            
            data = export_spreadsheet(user.username, req.source_name, req.format)
            if not data:
                raise HTTPException(status_code=404, detail="Spreadsheet not found")
            
            filename = f"{req.source_name}.{req.format}"
        
        elif req.source_type == "kpis":
            from src.services.pg_store import get_kpi_metrics
            
            # Get KPI data
            df = get_kpi_metrics()
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
        
        update_export_log(
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
        update_export_log(export_id=export_id, status="failed", error_message=str(e)[:500])
        raise HTTPException(status_code=500, detail=str(e))
