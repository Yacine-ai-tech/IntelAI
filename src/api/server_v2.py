"""
OmniIntelOS API v1 — FastAPI server with JWT auth, RBAC, multi-domain intelligence.

Domains: Finance, HR, Logistics, IT, Operations, ESG, Growth
"""
from __future__ import annotations

import os
import uuid
import time
import math
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form, WebSocket, WebSocketDisconnect, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.core.logger import get_logger
from src.core.jwt_auth import (
    TokenData, TokenResponse, LoginRequest, RegisterRequest,
    hash_password, verify_password,
    create_access_token, get_current_user, get_optional_user,
    require_role, require_action, require_data_access,
    get_user_data_categories, get_user_pages,
    ROLE_DEFINITIONS, DEFAULT_USERS,
)
from src.core.config import settings, get_cors_allowed_origins
from src.core.crypto import encrypt_value, decrypt_value

import urllib.parse as _urlparse
import httpx as _httpx

log = get_logger(__name__)

# ════════════════════════════════════════════════════════════
# APP INITIALIZATION
# ════════════════════════════════════════════════════════════

app = FastAPI(
    title="OmniIntelOS API",
    description="Intelligence Operating System — Multi-Domain AI Platform",
    version="2026.3.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

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


# ════════════════════════════════════════════════════════════
# REQUEST / RESPONSE MODELS
# ════════════════════════════════════════════════════════════

class ChatRequest(BaseModel):
    message: str
    persona: Optional[str] = None
    session_id: Optional[str] = None
    context: Optional[str] = ""

class ChatResponse(BaseModel):
    response: str
    persona_used: str
    persona_display: str = ""
    tokens_used: int = 0
    latency_ms: int = 0
    session_id: str = ""

class IngestMetricsRequest(BaseModel):
    data: List[Dict[str, Any]]
    source_name: str = "api"
    replace: bool = True

class FinancialRequest(BaseModel):
    company_id: Optional[str] = None
    period: Optional[str] = None
    statement_type: str = "income_statement"

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
        from src.services.pg_store import get_user, create_user
        for username, info in DEFAULT_USERS.items():
            existing = get_user(username)
            if not existing:
                create_user(username, hash_password(info["password"]), info["role"])
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
                    "created_at": datetime.utcnow().isoformat(),
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
                    "created_at": datetime.utcnow().isoformat(),
                }
        log.info("Initialized %d default users (in-memory fallback)", len(_users_db))


# ════════════════════════════════════════════════════════════
# STARTUP
# ════════════════════════════════════════════════════════════

@app.on_event("startup")
async def startup():
    """Validate required keys, initialize database, seed default data, start cleanup tasks."""
    log.info("🚀 OmniIntelOS API starting...")

    # Fail fast — required API keys must be present
    from src.core.config import validate_required_keys
    validate_required_keys()

    # Initialize PostgreSQL (users, chat sessions, monitoring)
    try:
        from src.services.pg_store import init_pg_tables
        init_pg_tables()
        log.info("✅ PostgreSQL initialized")
    except Exception as e:
        log.warning("⚠️ PostgreSQL init failed (will use in-memory fallback): %s", e)

    # Seed default users
    _init_default_users()

    # Seed multi-domain data if empty
    try:
        from src.services.pg_store import get_kpi_metrics, seed_all_domains
        df = get_kpi_metrics()
        if df.empty:
            count = seed_all_domains()
            log.info("✅ Seeded %d multi-domain KPI rows", count)
        else:
            log.info("✅ KPI data already present: %d rows", len(df))
    except Exception as e:
        log.warning("Data seeding skipped: %s", e)

    # Start periodic cleanup tasks for OAuth states and token refresh
    _start_background_cleanup_tasks()

    log.info("✅ OmniIntelOS API ready")


def _start_background_cleanup_tasks():
    """Start background tasks for OAuth state cleanup and token refresh."""
    import asyncio
    
    async def cleanup_oauth_states_task():
        """Periodically cleanup expired OAuth states (every 30 minutes)."""
        while True:
            try:
                await asyncio.sleep(30 * 60)  # 30 minutes
                from src.services.pg_store import cleanup_expired_oauth_states
                count = cleanup_expired_oauth_states()
                if count > 0:
                    log.info("Cleaned up %d expired OAuth states", count)
            except Exception as e:
                log.error("OAuth state cleanup error: %s", e)
    
    # Schedule cleanup task (fire and forget)
    try:
        import asyncio
        loop = asyncio.get_event_loop()
        loop.create_task(cleanup_oauth_states_task())
        log.info("✅ Background cleanup tasks started")
    except Exception as e:
        log.warning("Failed to start background cleanup tasks: %s", e)


# ════════════════════════════════════════════════════════════
# HEALTH & STATUS
# ════════════════════════════════════════════════════════════

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "OmniIntelOS API",
        "version": "2026.3.0",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "postgresql",
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
        "created_at": datetime.utcnow().isoformat(),
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
    }


# ════════════════════════════════════════════════════════════
# CHAT & PERSONAS
# ════════════════════════════════════════════════════════════

@app.post("/api/v1/chat")
async def chat(req: ChatRequest, user: TokenData = Depends(get_current_user)):
    import json as _json
    from src.services.omnismart_chatbot import get_omnismart_chatbot, get_persona_factory

    session_id = req.session_id or str(uuid.uuid4())

    # Ensure session exists in PostgreSQL
    try:
        from src.services.pg_store import ensure_session_exists, store_message
        ensure_session_exists(session_id, user.user_id)
    except Exception:
        pass  # Fallback — still works without PG

    # Use OmniSmartChatbot for intelligent routing (RAG, agents, web search, automation)
    chatbot = get_omnismart_chatbot(session_id)

    # Resolve persona and set system instruction
    factory = get_persona_factory()
    persona = factory.resolve_persona(user.role, req.persona, user.language)
    if hasattr(chatbot, "set_persona"):
        try:
            chatbot.set_persona(persona.name)
        except Exception as e:
            log.warning("Failed to set chatbot persona %s: %s", persona.name, e)

    result = chatbot.process(
        message=req.message,
        mode="auto",
        context=req.context or "",
    )

    response_text = result.get("response", "")
    sources = result.get("sources", [])
    mode = result.get("mode", "conversation")

    # Persist both messages to PostgreSQL
    try:
        store_message(session_id, "user", req.message, mode=mode)
        store_message(
            session_id, "assistant", response_text,
            mode=mode,
            sources=_json.dumps(sources) if sources else "[]",
            tokens_used=result.get("tokens_used", 0),
            latency_ms=result.get("latency_ms", 0),
        )
    except Exception as e:
        log.warning("PG message store failed: %s", e)

    return {
        "response": response_text,
        "persona_used": persona.name,
        "persona_display": persona.display_name,
        "tokens_used": result.get("tokens_used", 0),
        "latency_ms": result.get("latency_ms", 0),
        "session_id": session_id,
        "mode": mode,
        "sources": sources,
        "reasoning": result.get("reasoning", ""),
    }


@app.get("/api/v1/personas")
async def list_personas(user: TokenData = Depends(get_current_user)):
    from src.services.omnismart_chatbot import get_persona_factory
    factory = get_persona_factory()
    return {"personas": factory.list_personas()}


# ════════════════════════════════════════════════════════════
# VOICE (TTS / STT)
# ════════════════════════════════════════════════════════════

@app.post("/api/v1/ocr/extract")
async def ocr_extract(
    file: UploadFile = File(...),
    user: TokenData = Depends(get_current_user),
):
    try:
        # Call OCR microservice
        import httpx
        async with httpx.AsyncClient() as client:
            files = {"file": (file.filename, await file.read(), file.content_type)}
            response = await client.post(
                f"{settings.OCR_SERVICE_URL}/extract",
                files=files
            )
            response.raise_for_status()
            result = response.json()
            return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR extraction failed: {e}")


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


# ════════════════════════════════════════════════════════════
# INTEGRATIONS
# ════════════════════════════════════════════════════════════

@app.get("/api/v1/integrations/{integration_type}/data")
async def get_integration_data(
    integration_type: str,
    user: TokenData = Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100)
):
    """Get data from connected integrations."""
    if integration_type not in ["gmail", "sheets", "clickup"]:
        raise HTTPException(status_code=400, detail="Unsupported integration type")

    try:
        if integration_type == "gmail":
            return await get_gmail_data(user.username, limit)
        elif integration_type == "sheets":
            return await get_sheets_data(user.username, limit)
        elif integration_type == "clickup":
            return await get_clickup_data(user.username, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Integration error: {e}")


@app.get("/api/v1/integrations/status")
async def integrations_status(user: TokenData = Depends(get_current_user)):
    """Return a small map of integration connection statuses for the current user.
    This is more efficient than probing each integration with a heavyweight call.
    """
    from src.services.pg_store import get_integration_credentials
    types = ["gmail", "sheets", "clickup"]
    statuses = {}
    try:
        for t in types:
            row = get_integration_credentials(user.username, t)
            statuses[t] = bool(row)
        return {"statuses": statuses}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get integration statuses: {e}")

@app.post("/api/v1/integrations/{integration_type}/connect")
async def connect_integration(
    integration_type: str,
    credentials: dict,
    user: TokenData = Depends(get_current_user)
):
    """Connect to an integration service."""
    # Store credentials securely and test connection (legacy/manual)
    from src.services.pg_store import store_integration_credentials
    try:
        # If credentials is a dict (client_id/secret or oauth token), serialize and encrypt
        import json as _json
        serialized = _json.dumps(credentials)
        enc = encrypt_value(serialized)
        store_integration_credentials(user.username, integration_type, enc)
        return {"status": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to store credentials: {e}")


@app.get("/api/v1/integrations/{integration_type}/oauth/start")
async def oauth_start(integration_type: str, request: Request, user: TokenData = Depends(get_current_user)):
    """Start OAuth flow: returns a provider auth URL to redirect the user to.
    The server stores a short-lived state mapping to the current user for the callback.
    """
    supported = ("gmail", "sheets", "clickup")
    if integration_type not in supported:
        raise HTTPException(status_code=400, detail="Unsupported integration for OAuth")

    state = str(uuid.uuid4())
    # persist state -> username mapping so callback works across restarts
    from src.services.pg_store import store_oauth_state
    store_oauth_state(state, user.username, integration_type)

    # Build provider-specific URL
    if integration_type in ("gmail", "sheets"):
        client_id = settings.GOOGLE_CLIENT_ID
        redirect_uri = request.url_for("oauth_callback", integration_type=integration_type)
        scopes = [
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
        ]
        if integration_type == "gmail":
            scopes.append("https://www.googleapis.com/auth/gmail.readonly")
        if integration_type == "sheets":
            scopes.append("https://www.googleapis.com/auth/spreadsheets.readonly")

        params = {
            "client_id": client_id,
            "response_type": "code",
            "scope": " ".join(scopes),
            "redirect_uri": redirect_uri,
            "access_type": "offline",
            "prompt": "consent",
            "state": state,
            "include_granted_scopes": "true",
        }
        url = f"https://accounts.google.com/o/oauth2/v2/auth?{_urlparse.urlencode(params)}"
        return {"url": url, "state": state}

    if integration_type == "clickup":
        client_id = settings.CLICKUP_API_KEY or ""
        redirect_uri = request.url_for("oauth_callback", integration_type=integration_type)
        params = {"client_id": client_id, "redirect_uri": redirect_uri, "state": state}
        url = f"https://app.clickup.com/api?{_urlparse.urlencode(params)}"
        return {"url": url, "state": state}


@app.get("/api/v1/integrations/{integration_type}/oauth/callback", name="oauth_callback")
async def oauth_callback(integration_type: str, request: Request):
    """
    OAuth callback endpoint — exchanges code for tokens and stores encrypted credentials.
    Now also handles token refresh metadata for long-lived integrations.
    
    Expected query params: code, state
    """
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing code or state in callback")

    from src.services.pg_store import (
        pop_oauth_state,
        store_integration_credentials,
        store_token_refresh_metadata,
        record_oauth_token_event,
    )
    
    row = pop_oauth_state(state)
    if not row:
        raise HTTPException(status_code=400, detail="Invalid or expired state")
    username = row.get("username")

    try:
        token_data = {}
        expires_in = 3600  # Default 1 hour
        
        if integration_type in ("gmail", "sheets"):
            token_url = "https://oauth2.googleapis.com/token"
            data = {
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": request.url_for("oauth_callback", integration_type=integration_type),
                "grant_type": "authorization_code",
            }
            async with _httpx.AsyncClient() as client:
                resp = await client.post(token_url, data=data, timeout=30)
                resp.raise_for_status()
                token_data = resp.json()
            
            expires_in = token_data.get("expires_in", 3600)

        elif integration_type == "clickup":
            token_url = "https://api.clickup.com/api/v2/oauth/token"
            data = {
                "client_id": settings.CLICKUP_API_KEY,
                "client_secret": settings.CLICKUP_API_KEY,
                "code": code,
            }
            async with _httpx.AsyncClient() as client:
                resp = await client.post(token_url, json=data, timeout=30)
                resp.raise_for_status()
                token_data = resp.json()
            
            expires_in = token_data.get("expires_in", 3600)
        else:
            raise HTTPException(status_code=400, detail="Unsupported integration")

        # ✅ Step 1: Encrypt and store access token + credentials
        import json as _json
        from datetime import datetime as _dt, timedelta
        
        serialized = _json.dumps(token_data)
        enc = encrypt_value(serialized)
        store_integration_credentials(username, integration_type, enc)
        
        # ✅ Step 2: Store refresh token metadata for token rotation
        refresh_token = token_data.get("refresh_token")
        if refresh_token:
            # Calculate token expiry time
            token_expires_at = (
                _dt.utcnow() + timedelta(seconds=expires_in)
            ).isoformat()
            
            # Store refresh token securely (encrypted)
            store_token_refresh_metadata(
                username=username,
                integration_type=integration_type,
                refresh_token=refresh_token,
                token_expires_at=token_expires_at,
                scope=token_data.get("scope", ""),
                encrypt=True,
            )
        
        # ✅ Step 3: Record OAuth event for audit trail
        record_oauth_token_event(
            username=username,
            integration_type=integration_type,
            event_type="token_issued",
            new_expires_at=(
                _dt.utcnow() + timedelta(seconds=expires_in)
            ).isoformat(),
            user_agent=request.headers.get("user-agent"),
            ip_address=request.client.host if request.client else None,
        )
        
        log.info(
            "OAuth token stored for %s:%s (expires in %d seconds)",
            username,
            integration_type,
            expires_in,
        )

        # ✅ Step 4: Redirect back to front-end with success
        frontend_base = (
            settings.FRONTEND_URL
            or request.query_params.get("next")
            or "http://localhost:5173"
        )
        redirect_url = (
            f"{frontend_base.rstrip('/')}/?integration=connected&name={integration_type}"
        )
        return RedirectResponse(url=redirect_url)
    
    except _httpx.HTTPError as e:
        log.error("Token exchange failed for %s:%s: %s", username, integration_type, e)
        record_oauth_token_event(
            username=username,
            integration_type=integration_type,
            event_type="token_failed",
            error_message=str(e),
        )
        raise HTTPException(status_code=502, detail=f"Token exchange failed: {e}")
    except Exception as e:
        log.error("OAuth callback error for %s:%s: %s", username, integration_type, e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/integrations/{integration_type}/disconnect")
async def disconnect_integration(
    integration_type: str,
    user: TokenData = Depends(get_current_user)
):
    """Disconnect from an integration service."""
    from src.services.pg_store import remove_integration_credentials
    remove_integration_credentials(user.username, integration_type)
    return {"status": "disconnected"}


# ════════════════════════════════════════════════════════════
# VOICE (TTS / STT)
# ════════════════════════════════════════════════════════════

@app.post("/api/v1/voice/transcribe")
async def voice_transcribe(
    audio: UploadFile = File(...),
    user: TokenData = Depends(get_current_user),
):
    try:
        # Call Voice microservice
        import httpx
        async with httpx.AsyncClient() as client:
            files = {"file": (audio.filename, await audio.read(), audio.content_type)}
            response = await client.post(
                f"{settings.VOICE_SERVICE_URL}/stt",
                files=files,
                data={"language": user.language if user.language != "en" else None}
            )
            response.raise_for_status()
            result = response.json()
            return {"text": result["text"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {e}")


@app.post("/api/v1/voice/tts")
async def voice_tts(
    text: str = Form(...),
    language: str = Form("en"),
    user: TokenData = Depends(get_current_user),
):
    try:
        # Call Voice microservice
        import httpx
        async with httpx.AsyncClient() as client:
            data = {"text": text, "language": language}
            response = await client.post(
                f"{settings.VOICE_SERVICE_URL}/tts",
                data=data
            )
            response.raise_for_status()
            from fastapi.responses import Response
            return Response(content=response.content, media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS failed: {e}")


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
    store_kpi_metrics(df, source_name=req.source_name, replace=req.replace)
    log_audit_event(user.username, "DATA_INGEST", f"Ingested {len(df)} metrics from {req.source_name}")
    return {"status": "ingested", "rows": len(df), "source": req.source_name}


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
    if file.filename and file.filename.endswith(".pdf"):
        try:
            from PyPDF2 import PdfReader
            import io
            reader = PdfReader(io.BytesIO(content))
            text = "\n".join(p.extract_text() or "" for p in reader.pages)
        except Exception:
            text = content.decode("utf-8", errors="ignore")
    elif file.filename and file.filename.endswith(".csv"):
        text = content.decode("utf-8", errors="ignore")
    else:
        text = content.decode("utf-8", errors="ignore")

    doc_id = str(uuid.uuid4())
    docs_df = pd.DataFrame([{
        "doc_id": doc_id, "title": file.filename, "content": text[:50000],
        "source": category, "embedding": "",
    }])
    store_knowledge_docs(docs_df)
    log_audit_event(user.username, "DOC_INGEST", f"Uploaded {file.filename}")
    return {"status": "ingested", "doc_id": doc_id, "filename": file.filename, "chars": len(text)}


# ════════════════════════════════════════════════════════════
# CAMERA & DEVICE PAIRING
# ════════════════════════════════════════════════════════════

@app.post("/api/v1/camera/pair")
async def request_pairing(
    device_name: str = "Mobile Device",
    user: TokenData = Depends(get_current_user),
):
    """Request device pairing - returns QR code for mobile scanning."""
    from src.integrations.camera import CameraManager
    cm = CameraManager()
    result = cm.pair_mobile(user.username, device_name)
    from src.services.pg_store import log_audit_event
    log_audit_event(user.username, "CAMERA_PAIR_REQUEST", f"Requested pairing for {device_name}")
    return result


@app.post("/api/v1/camera/upload")
async def upload_from_paired_device(
    token: str,
    file: UploadFile = File(...),
    category: str = Form("Scanned"),
):
    """Upload document from paired mobile device using token authentication."""
    from src.integrations.camera import CameraManager
    from src.services.pg_store import store_knowledge_docs, log_audit_event
    
    cm = CameraManager()
    session = cm.validate_mobile(token)
    
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired pairing token")
    
    user = session["user"]
    device_name = session["device_name"]
    
    try:
        content = await file.read()
        text = ""
        
        # Process file based on type
        if file.filename and file.filename.endswith(".pdf"):
            try:
                from PyPDF2 import PdfReader
                import io
                reader = PdfReader(io.BytesIO(content))
                text = "\n".join(p.extract_text() or "" for p in reader.pages)
            except Exception:
                text = content.decode("utf-8", errors="ignore")
        elif file.filename and file.filename.endswith(".csv"):
            text = content.decode("utf-8", errors="ignore")
        else:
            # Use OCR service for images
            try:
                import httpx
                async with httpx.AsyncClient() as client:
                    files = {"file": (file.filename, content, file.content_type)}
                    response = await client.post(
                        f"{settings.OCR_SERVICE_URL}/extract",
                        files=files
                    )
                    if response.status_code == 200:
                        ocr_result = response.json()
                        text = ocr_result.get("text", f"[Image: {file.filename}]")
                    else:
                        text = f"[Image: {file.filename} - OCR failed]"
            except Exception:
                text = f"[Image: {file.filename}]"
        
        doc_id = str(uuid.uuid4())
        docs_df = pd.DataFrame([{
            "doc_id": doc_id,
            "title": f"{file.filename} (from {device_name})",
            "content": text[:50000],
            "source": category,
            "embedding": "",
        }])
        store_knowledge_docs(docs_df)
        
        # Record the upload
        cm.record_mobile_upload(token)
        log_audit_event(user, "CAMERA_UPLOAD", f"Paired device {device_name} uploaded {file.filename}")
        
        return {
            "status": "ingested",
            "doc_id": doc_id,
            "filename": file.filename,
            "chars": len(text),
            "device_name": device_name,
        }
    except HTTPException:
        raise
    except Exception as e:
        log.error("Error processing paired upload: %s", e)
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/v1/camera/sessions")
async def list_pairing_sessions(user: TokenData = Depends(get_current_user)):
    """List all active pairing sessions for current user."""
    from src.integrations.camera import CameraManager
    cm = CameraManager()
    sessions = cm.list_mobile_sessions(user.username)
    return {"sessions": sessions, "count": len(sessions)}


@app.post("/api/v1/camera/sessions/{token}/revoke")
async def revoke_pairing(
    token: str,
    user: TokenData = Depends(get_current_user),
):
    """Revoke a specific pairing session."""
    from src.integrations.camera import CameraManager
    from src.services.pg_store import log_audit_event
    
    cm = CameraManager()
    session = cm.validate_mobile(token)
    
    if not session or session["user"] != user.username:
        raise HTTPException(status_code=403, detail="Cannot revoke this session")
    
    success = cm.revoke_mobile_session(token)
    if success:
        log_audit_event(user.username, "CAMERA_SESSION_REVOKE", f"Revoked pairing token {token[:8]}...")
        return {"status": "revoked", "token": token}
    
    raise HTTPException(status_code=400, detail="Could not revoke session")


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
        df = df[df["category"].isin(user_categories)]

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
            return {"statement": stmt.data, "margins": margins, "period": period, "type": "P&L"}
        elif req.statement_type in ("balance_sheet", "bs"):
            stmt = engine.create_balance_sheet(period)
            ratios = engine.analyze_ratios(stmt)
            return {"statement": stmt.data, "ratios": ratios, "period": period, "type": "Balance Sheet"}
        elif req.statement_type in ("cash_flow", "cf"):
            stmt = engine.create_cash_flow_statement(period)
            return {"statement": stmt.data, "period": period, "type": "Cash Flow"}
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
# INSIGHTS & RISK
# ════════════════════════════════════════════════════════════

@app.get("/api/v1/insights/health")
async def get_health_index(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    from src.services.insights import compute_health_index
    df = get_kpi_metrics()
    return _json_safe(compute_health_index(df))


@app.get("/api/v1/insights/risk")
async def get_risk_score(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    from src.services.insights import compute_risk_score
    df = get_kpi_metrics()
    return _json_safe(compute_risk_score(df))


@app.get("/api/v1/insights/summary")
async def get_executive_summary(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    from src.services.insights import compute_health_index, compute_risk_score, extract_key_metrics, build_executive_summary
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


@app.get("/api/v1/insights/anomalies")
async def get_anomalies(
    metric: Optional[str] = None,
    user: TokenData = Depends(get_current_user),
):
    from src.services.pg_store import get_kpi_metrics
    from src.services.insights import detect_anomalies
    metrics_filter = [metric] if metric else None
    df = get_kpi_metrics(metrics=metrics_filter)
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
async def get_hr_summary(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    from src.services.hr import HRService
    return HRService().get_workforce_summary(get_kpi_metrics())

@app.get("/api/v1/hr/departments")
async def get_hr_departments(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    from src.services.hr import HRService
    return {"departments": HRService().get_department_analytics(get_kpi_metrics())}

@app.get("/api/v1/hr/recruitment")
async def get_hr_recruitment(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    from src.services.hr import HRService
    return HRService().get_recruitment_pipeline(get_kpi_metrics())

@app.get("/api/v1/hr/training")
async def get_hr_training(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    from src.services.hr import HRService
    return HRService().get_training_overview(get_kpi_metrics())

@app.get("/api/v1/hr/health")
async def get_hr_health(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    from src.services.hr import HRService
    return HRService().compute_hr_health_score(get_kpi_metrics())


# ════════════════════════════════════════════════════════════
# LOGISTICS DOMAIN
# ════════════════════════════════════════════════════════════

@app.get("/api/v1/logistics/summary")
async def get_logistics_summary(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    from src.services.logistics import LogisticsService
    return LogisticsService().get_supply_chain_summary(get_kpi_metrics())

@app.get("/api/v1/logistics/inventory")
async def get_logistics_inventory(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    from src.services.logistics import LogisticsService
    return LogisticsService().get_inventory_status(get_kpi_metrics())

@app.get("/api/v1/logistics/shipping")
async def get_logistics_shipping(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    from src.services.logistics import LogisticsService
    return LogisticsService().get_shipping_analytics(get_kpi_metrics())

@app.get("/api/v1/logistics/suppliers")
async def get_logistics_suppliers(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    from src.services.logistics import LogisticsService
    return {"suppliers": LogisticsService().get_supplier_metrics(get_kpi_metrics())}

@app.get("/api/v1/logistics/health")
async def get_logistics_health(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    from src.services.logistics import LogisticsService
    return LogisticsService().compute_logistics_health(get_kpi_metrics())


# ════════════════════════════════════════════════════════════
# IT OPERATIONS DOMAIN
# ════════════════════════════════════════════════════════════

@app.get("/api/v1/it/overview")
async def get_it_overview(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    from src.services.it_ops import ITOpsService
    return ITOpsService().get_it_overview(get_kpi_metrics())

@app.get("/api/v1/it/tickets")
async def get_it_tickets(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    from src.services.it_ops import ITOpsService
    return ITOpsService().get_ticket_analytics(get_kpi_metrics())

@app.get("/api/v1/it/security")
async def get_it_security(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    from src.services.it_ops import ITOpsService
    return ITOpsService().get_security_dashboard(get_kpi_metrics())

@app.get("/api/v1/it/infrastructure")
async def get_it_infrastructure(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    from src.services.it_ops import ITOpsService
    return ITOpsService().get_infrastructure_metrics(get_kpi_metrics())

@app.get("/api/v1/it/devops")
async def get_it_devops(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    from src.services.it_ops import ITOpsService
    return ITOpsService().get_devops_metrics(get_kpi_metrics())

@app.get("/api/v1/it/health")
async def get_it_health(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    from src.services.it_ops import ITOpsService
    return ITOpsService().compute_it_health(get_kpi_metrics())


# ════════════════════════════════════════════════════════════
# OPERATIONS DOMAIN
# ════════════════════════════════════════════════════════════

@app.get("/api/v1/operations/summary")
async def get_ops_summary(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    from src.services.operations import OperationsService
    return OperationsService().get_operations_summary(get_kpi_metrics())

@app.get("/api/v1/operations/quality")
async def get_ops_quality(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    from src.services.operations import OperationsService
    return OperationsService().get_quality_metrics(get_kpi_metrics())

@app.get("/api/v1/operations/production")
async def get_ops_production(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    from src.services.operations import OperationsService
    return OperationsService().get_production_metrics(get_kpi_metrics())

@app.get("/api/v1/operations/safety")
async def get_ops_safety(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    from src.services.operations import OperationsService
    return OperationsService().get_safety_metrics(get_kpi_metrics())

@app.get("/api/v1/operations/health")
async def get_ops_health(user: TokenData = Depends(get_current_user)):
    from src.services.pg_store import get_kpi_metrics
    from src.services.operations import OperationsService
    return OperationsService().compute_ops_health(get_kpi_metrics())


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
            "water_usage": _val(["water usage"]),
            "waste_diverted": _val(["waste diverted"]),
        },
        "social": {
            "community_investment": _val(["community investment"]),
            "diversity_index": _val(["diversity index"]),
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
# MONITORING API
# ════════════════════════════════════════════════════════════

@app.get("/api/v1/monitoring/stats")
async def get_monitoring_stats(user: TokenData = Depends(get_current_user)):
    result = {}
    try:
        from src.services.pg_store import get_monitoring_stats
        result.update(get_monitoring_stats())
    except Exception:
        pass
    try:
        from src.core.monitoring import monitor
        result.update(monitor.get_current_metrics())
    except Exception:
        pass
    return result


# ════════════════════════════════════════════════════════════
# VECTOR SEARCH (ChromaDB)
# ════════════════════════════════════════════════════════════

@app.get("/api/v1/knowledge/search")
async def vector_search(q: str, n: int = 5, user: TokenData = Depends(get_current_user)):
    try:
        from src.services.pg_store import search_vectors
        results = search_vectors(q, n=n)
        docs = []
        if results and results.get("documents"):
            for i, doc in enumerate(results["documents"][0]):
                meta = results["metadatas"][0][i] if results.get("metadatas") else {}
                dist = results["distances"][0][i] if results.get("distances") else 0
                docs.append({"content": doc[:500], "metadata": meta, "distance": dist})
        return {"results": docs, "query": q, "count": len(docs)}
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
# N8N INTEGRATION
# ════════════════════════════════════════════════════════════

@app.get("/api/v1/n8n/nodes")
async def list_n8n_nodes(user: TokenData = Depends(get_current_user)):
    try:
        from src.integrations.n8n import N8NClient
        return {"nodes": N8NClient.list_allowed_nodes()}
    except Exception:
        return {"nodes": ["webhook", "http", "gmail", "sheets", "drive"]}

@app.post("/api/v1/n8n/webhook/ingest")
async def n8n_webhook_ingest(payload: Dict[str, Any]):
    try:
        from src.services.pg_store import store_kpi_metrics
        if "data" in payload:
            df = pd.DataFrame(payload["data"])
            store_kpi_metrics(df, source_name="n8n", replace=False)
            return {"status": "ingested", "rows": len(df)}
        return {"status": "no data in payload"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


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
        session_id = str(uuid.uuid4())
        history = []
        await websocket.send_json({"type": "connected", "user": user.username, "session_id": session_id})

        while True:
            data = await websocket.receive_json()
            message = data.get("message", "")
            persona_override = data.get("persona")
            result = factory.chat(
                message=message, user_role=user.role,
                persona_override=persona_override, language=user.language, history=history,
            )
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": result["response"]})
            await websocket.send_json({
                "type": "response", "response": result["response"],
                "persona_used": result["persona_used"],
                "persona_display": result.get("persona_display", ""),
                "tokens_used": result.get("tokens_used", 0),
                "latency_ms": result.get("latency_ms", 0),
            })
    except WebSocketDisconnect:
        log.info("WebSocket client disconnected")
    except Exception as e:
        log.error("WebSocket error: %s", e)


# ════════════════════════════════════════════════════════════
# METRICS (Prometheus)
# ════════════════════════════════════════════════════════════

@app.get("/metrics")
async def prometheus_metrics():
    try:
        from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
        from fastapi.responses import Response
        return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
    except Exception:
        return {"error": "Prometheus not available"}


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


# ════════════════════════════════════════════════════════════
# INTEGRATION HELPERS
# ════════════════════════════════════════════════════════════

async def get_gmail_data(username: str, limit: int = 20):
    """Get Gmail data for user."""
    # Mock data for now - replace with actual Gmail API integration
    return [
        {
            "subject": "Q4 Financial Report",
            "from": "finance@company.com",
            "date": "2024-02-20",
            "snippet": "Please find attached the Q4 financial report..."
        },
        {
            "subject": "Meeting Invitation",
            "from": "hr@company.com",
            "date": "2024-02-19",
            "snippet": "You are invited to the quarterly review meeting..."
        }
    ][:limit]

async def get_sheets_data(username: str, limit: int = 20):
    """Get Google Sheets data for user."""
    # Mock data for now - replace with actual Google Sheets API integration
    return [
        {
            "name": "Sales Dashboard",
            "data": [
                ["Month", "Revenue", "Target"],
                ["Jan", "125000", "120000"],
                ["Feb", "138000", "130000"]
            ]
        },
        {
            "name": "Employee Data",
            "data": [
                ["Name", "Department", "Salary"],
                ["John Doe", "Engineering", "95000"],
                ["Jane Smith", "Marketing", "78000"]
            ]
        }
    ][:limit]

async def get_clickup_data(username: str, limit: int = 20):
    """Get ClickUp data for user."""
    # Mock data for now - replace with actual ClickUp API integration
    return [
        {
            "name": "Implement new dashboard",
            "status": "in progress",
            "list": "Development",
            "due_date": "2024-03-01",
            "description": "Create new analytics dashboard for Q1 reporting"
        },
        {
            "name": "Update security policies",
            "status": "todo",
            "list": "Security",
            "due_date": "2024-02-28",
            "description": "Review and update company security policies"
        }
    ][:limit]


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


@app.post("/api/v1/data/ingest")
async def ingest_data(
    file: UploadFile = File(...),
    request_data: str = Form(...),  # JSON string of DataIngestionRequest
    user: TokenData = Depends(get_current_user),
):
    """
    Ingest data from file (CSV, XLSX, PDF, DOCX, JSON).
    
    Supports destinations:
    - kpis: Import metrics into KPI tracking
    - knowledge_base: Index documents for RAG
    - spreadsheet: Store in mini-spreadsheet for management
    """
    import json as _json
    from io import BytesIO
    
    try:
        req = DataIngestionRequest(**_json.loads(request_data))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid request: {str(e)}")
    
    from src.services.omnismart_chatbot import (
        parse_pdf,
        parse_docx,
        ingest_document,
    )
    from src.services.pg_store import (
        log_data_ingestion,
        update_ingestion_log,
    )
    
    ingestion_id = log_data_ingestion(
        username=user.username,
        filename=file.filename,
        file_type=req.file_type,
        source=req.source,
        import_destination=req.destination,
        status="processing",
    )
    
    try:
        content = await file.read()
        
        # Parse file based on type
        if req.file_type == "pdf":
            text = parse_pdf(BytesIO(content))
        elif req.file_type == "docx":
            text = parse_docx(BytesIO(content))
        elif req.file_type in ("csv", "xlsx"):
            import pandas as pd
            if req.file_type == "xlsx":
                df = pd.read_excel(BytesIO(content))
            else:
                df = pd.read_csv(BytesIO(content))
            text = df.to_string()
            row_count = len(df)
        elif req.file_type == "json":
            import json as _json
            data = _json.loads(content)
            text = _json.dumps(data, indent=2)
            row_count = len(data) if isinstance(data, list) else 1
        else:
            text = content.decode("utf-8")
            row_count = len(text.split("\n"))
        
        # Store in appropriate destination
        if req.destination == "knowledge_base":
            result = ingest_document(
                title=file.filename,
                content=text,
                source=req.source,
                doc_type=req.file_type,
                language=user.language or "en",
                metadata={
                    "domain": req.domain,
                    "uploaded_by": user.username,
                },
            )
            
            update_ingestion_log(
                ingestion_id=ingestion_id,
                status="success" if result["success"] else "failed",
                row_count=result.get("chunks_count", 0),
                error_message=result.get("error") if not result["success"] else None,
                ingested_at=datetime.utcnow().isoformat(),
            )
            
            return {
                "status": "success" if result["success"] else "error",
                "ingestion_id": ingestion_id,
                **result,
            }
        
        elif req.destination == "spreadsheet":
            if not req.destination_name:
                raise HTTPException(status_code=400, detail="destination_name required for spreadsheet")
            
            from src.services.pg_store import append_spreadsheet_rows
            
            # Parse as structured data
            if req.file_type in ("csv", "xlsx"):
                data = df.to_dict(orient="records")
                success = append_spreadsheet_rows(
                    username=user.username,
                    spreadsheet_name=req.destination_name,
                    rows=data,
                )
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Cannot import {req.file_type} to spreadsheet (use CSV/XLSX)"
                )
            
            update_ingestion_log(
                ingestion_id=ingestion_id,
                status="success" if success else "failed",
                row_count=len(data) if 'data' in locals() else 0,
                ingested_at=datetime.utcnow().isoformat(),
            )
            
            return {
                "status": "success" if success else "error",
                "ingestion_id": ingestion_id,
                "message": f"Imported {len(data) if 'data' in locals() else 0} rows to spreadsheet",
            }
        
        elif req.destination == "kpis":
            import pandas as pd
            
            df = pd.read_csv(BytesIO(content)) if req.file_type == "csv" else pd.read_excel(BytesIO(content))
            
            from src.services.pg_store import store_kpi_metrics
            
            store_kpi_metrics(
                df,
                source_name=f"{req.source}:{file.filename}",
                replace=False,
            )
            
            update_ingestion_log(
                ingestion_id=ingestion_id,
                status="success",
                row_count=len(df),
                ingested_at=datetime.utcnow().isoformat(),
            )
            
            return {
                "status": "success",
                "ingestion_id": ingestion_id,
                "rows_imported": len(df),
                "message": f"Imported {len(df)} KPI records",
            }
        
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported destination: {req.destination}")
    
    except Exception as e:
        log.error("Data ingestion error: %s", e)
        update_ingestion_log(
            ingestion_id=ingestion_id,
            status="failed",
            error_message=str(e)[:500],
        )
        raise HTTPException(status_code=500, detail=str(e))


# ════════════════════════════════════════════════════════════════════════════
# DATA EXPORT & SPREADSHEET MANAGEMENT
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
        export_name=req.source_name or f"export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
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
            import pandas as pd
            
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
        
        return {
            "status": "success",
            "export_id": export_id,
            "format": req.format,
            "filename": filename,
            "data": data if req.format in ("csv", "json") else f"[Binary data - {len(data)} bytes]",
            "download_url": f"/api/v1/exports/{export_id}/download",
        }
    
    except HTTPException:
        raise
    except Exception as e:
        log.error("Data export error: %s", e)
        update_export_log(export_id=export_id, status="failed", error_message=str(e)[:500])
        raise HTTPException(status_code=500, detail=str(e))


# ════════════════════════════════════════════════════════════════════════════
# MINI-SPREADSHEET MANAGEMENT
# ════════════════════════════════════════════════════════════════════════════

class CreateSpreadsheetRequest(BaseModel):
    name: str
    domain: Optional[str] = "general"
    description: Optional[str] = None
    schema_columns: Optional[List[Dict[str, Any]]] = None
    is_public: bool = False


@app.post("/api/v1/spreadsheets")
async def create_spreadsheet(
    req: CreateSpreadsheetRequest,
    user: TokenData = Depends(get_current_user),
):
    """Create a new mini-spreadsheet for data management (like Excel)."""
    from src.services.pg_store import create_spreadsheet as create_ss
    
    success = create_ss(
        username=user.username,
        name=req.name,
        domain=req.domain,
        schema_columns=req.schema_columns,
        description=req.description,
        is_public=req.is_public,
    )
    
    if success:
        return {
            "status": "success",
            "name": req.name,
            "domain": req.domain,
            "message": f"Spreadsheet '{req.name}' created successfully",
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to create spreadsheet")


# ════════════════════════════════════════════════════════════════════════════
# BACKGROUND TASK MONITORING
# ════════════════════════════════════════════════════════════════════════════

@app.get("/api/v1/admin/tasks/status")
async def get_background_tasks_status(
    user: TokenData = Depends(require_role("admin")),
):
    """
    Get status of background cleanup tasks.
    
    Admin only endpoint for monitoring system health.
    """
    from src.services.pg_store import cleanup_expired_oauth_states
    
    try:
        # Run cleanup and get stats
        count = cleanup_expired_oauth_states()
        
        return {
            "status": "healthy",
            "tasks": {
                "oauth_state_cleanup": {
                    "enabled": True,
                    "interval_minutes": 30,
                    "last_cleaned_count": count,
                    "next_run": "auto (30 min)",
                },
                "token_refresh": {
                    "enabled": True,
                    "interval_hours": 1,
                    "status": "monitoring",
                },
                "data_export_cleanup": {
                    "enabled": True,
                    "interval_hours": 24,
                    "action": "Delete exports older than 7 days",
                },
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        log.error("Failed to get tasks status: %s", e)
        return {
            "status": "error",
            "error": str(e)[:200],
            "timestamp": datetime.utcnow().isoformat(),
        }


# ════════════════════════════════════════════════════════════════════════════
# DATA INGESTION MANAGEMENT ENDPOINTS
# ════════════════════════════════════════════════════════════════════════════

class IngestDataRequest(BaseModel):
    percentage: float = 100.0
    domains: Optional[List[str]] = None
    companies: Optional[List[str]] = None


class IngestByDomainsRequest(BaseModel):
    domain_percentages: Dict[str, float]


class IngestByCompaniesRequest(BaseModel):
    company_percentages: Dict[str, float]


class DeleteDataRequest(BaseModel):
    target: str  # "all" or domain name


# Global ingestion manager instance
_data_ingestion_manager = None


async def get_ingestion_manager():
    """Get or create the data ingestion manager."""
    global _data_ingestion_manager
    if _data_ingestion_manager is None:
        from src.services.data_ingestion_manager import DataIngestionManager
        _data_ingestion_manager = DataIngestionManager()
        await _data_ingestion_manager.initialize()
    return _data_ingestion_manager


@app.get("/api/v1/data-ingestion/dataset-info")
async def get_dataset_info(
    user: TokenData = Depends(get_current_user),
):
    """
    Get information about the available enhanced dataset.
    
    Returns:
    - Total records available
    - Domains and companies covered
    - Time period
    - File sizes
    """
    # Dataset metadata should be available even if the realtime pipeline
    # cannot be initialized in the current runtime.
    global _data_ingestion_manager
    if _data_ingestion_manager is None:
        from src.services.data_ingestion_manager import DataIngestionManager
        _data_ingestion_manager = DataIngestionManager()
    manager = _data_ingestion_manager
    info = manager.get_dataset_info()
    
    return {
        "status": "success",
        "data": info,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post("/api/v1/data-ingestion/ingest-all")
async def ingest_all_data(
    req: IngestDataRequest,
    user: TokenData = Depends(get_current_user),
):
    """
    Ingest all data with granular control over percentage and filters.
    
    Parameters:
    - percentage: 0-100, percentage of data to ingest
    - domains: List of domains to include (Finance, Growth, Operations, People, ESG)
    - companies: List of company names to include
    
    Example:
    {
        "percentage": 50,
        "domains": ["Finance", "Operations"],
        "companies": ["CloudSync Pro", "DataFlow Analytics"]
    }
    """
    try:
        manager = await get_ingestion_manager()
        
        log.info(
            "User %s starting data ingestion: %d%% domains=%s companies=%s",
            user.username, req.percentage, req.domains, req.companies
        )
        
        stats = await manager.ingest_all_data(
            percentage=req.percentage,
            domains=req.domains,
            companies=req.companies
        )
        
        return {
            "status": "success" if stats.status == "completed" else stats.status,
            "ingestion_stats": {
                "total_records": stats.total_records,
                "ingested_records": stats.ingested_records,
                "failed_records": stats.failed_records,
                "percentage": stats.ingestion_percentage,
                "domains": stats.domains_covered,
                "companies": stats.companies_covered,
                "execution_time_seconds": stats.execution_time_seconds,
            },
            "timestamp": stats.timestamp,
            "error_message": stats.error_message if stats.error_message else None,
        }
    except Exception as e:
        log.error("Data ingestion failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/data-ingestion/ingest-by-domains")
async def ingest_by_domains(
    req: IngestByDomainsRequest,
    user: TokenData = Depends(get_current_user),
):
    """
    Ingest data with different percentages for each domain.
    
    Example:
    {
        "domain_percentages": {
            "Finance": 100,
            "Operations": 50,
            "People": 25,
            "ESG": 0,
            "Growth": 100
        }
    }
    """
    try:
        manager = await get_ingestion_manager()
        
        log.info(
            "User %s starting domain-specific ingestion: %s",
            user.username, req.domain_percentages
        )
        
        results = await manager.ingest_by_domains(req.domain_percentages)
        
        return {
            "status": "success",
            "results": {
                domain: {
                    "ingested_records": stats.ingested_records,
                    "failed_records": stats.failed_records,
                    "execution_time_seconds": stats.execution_time_seconds,
                } for domain, stats in results.items()
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        log.error("Domain-specific ingestion failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/data-ingestion/ingest-by-companies")
async def ingest_by_companies(
    req: IngestByCompaniesRequest,
    user: TokenData = Depends(get_current_user),
):
    """
    Ingest data with different percentages for each company.
    
    Example:
    {
        "company_percentages": {
            "CloudSync Pro": 100,
            "DataFlow Analytics": 50,
            "HealthCare Analytics": 75
        }
    }
    """
    try:
        manager = await get_ingestion_manager()
        
        log.info(
            "User %s starting company-specific ingestion: %s",
            user.username, req.company_percentages
        )
        
        results = await manager.ingest_by_companies(req.company_percentages)
        
        return {
            "status": "success",
            "results": {
                company: {
                    "ingested_records": stats.ingested_records,
                    "failed_records": stats.failed_records,
                    "execution_time_seconds": stats.execution_time_seconds,
                } for company, stats in results.items()
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        log.error("Company-specific ingestion failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/data-ingestion/ingest-pdfs")
async def ingest_pdf_documents(
    user: TokenData = Depends(get_current_user),
):
    """Ingest PDF documents from the dataset."""
    try:
        manager = await get_ingestion_manager()
        results = manager.ingest_pdf_documents()
        
        log.info(
            "User %s ingested %d PDF files",
            user.username, results["processed_files"]
        )
        
        return {
            "status": "success",
            "pdf_ingestion": results,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        log.error("PDF ingestion failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/data-ingestion/ingest-emails")
async def ingest_email_samples(
    user: TokenData = Depends(get_current_user),
):
    """Ingest email samples from the dataset."""
    try:
        manager = await get_ingestion_manager()
        results = manager.ingest_email_samples()
        
        log.info(
            "User %s ingested %d emails",
            user.username, results["emails_ingested"]
        )
        
        return {
            "status": "success",
            "email_ingestion": results,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        log.error("Email ingestion failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/data-ingestion/ingest-sheets")
async def ingest_sheets_data(
    user: TokenData = Depends(get_current_user),
):
    """Ingest Google Sheets data from the dataset."""
    try:
        manager = await get_ingestion_manager()
        results = manager.ingest_sheets_data()
        
        log.info(
            "User %s ingested %d sheets",
            user.username, results["sheets_ingested"]
        )
        
        return {
            "status": "success",
            "sheets_ingestion": results,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        log.error("Sheets ingestion failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/v1/data-ingestion/delete-all")
async def delete_all_ingested_data(
    user: TokenData = Depends(require_role("admin")),
):
    """
    Delete ALL ingested data from the platform.
    
    Admin only - careful operation!
    """
    try:
        manager = await get_ingestion_manager()
        result = await manager.delete_all_ingested_data()
        
        log.warning(
            "Admin user %s deleted ALL ingested data",
            user.username
        )
        
        return {
            "status": "success",
            "deletion_result": result,
            "warning": "All ingested data has been deleted",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        log.error("Data deletion failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/v1/data-ingestion/delete-domain/{domain}")
async def delete_domain_data(
    domain: str,
    user: TokenData = Depends(get_current_user),
):
    """
    Delete ingested data for a specific domain.
    
    Parameters:
    - domain: Domain name (Finance, Growth, Operations, People, ESG)
    """
    try:
        manager = await get_ingestion_manager()
        result = await manager.delete_domain_data(domain)
        
        log.info(
            "User %s deleted data for domain: %s",
            user.username, domain
        )
        
        return {
            "status": "success",
            "deletion_result": result,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        log.error("Domain data deletion failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/v1/data-ingestion/delete-company/{company}")
async def delete_company_data(
    company: str,
    user: TokenData = Depends(get_current_user),
):
    """
    Delete ingested data for a specific company.

    Parameters:
    - company: Company name
    """
    try:
        manager = await get_ingestion_manager()
        result = await manager.delete_company_data(company)

        log.info(
            "User %s deleted data for company: %s",
            user.username, company
        )

        return {
            "status": "success",
            "deletion_result": result,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        log.error("Company data deletion failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/data-ingestion/status")
async def get_ingestion_status(
    user: TokenData = Depends(get_current_user),
):
    """
    Get current ingestion status and history.
    
    Returns:
    - Total ingested records
    - Ingestion history by batch
    - Domains and companies covered
    - Last update timestamp
    """
    try:
        manager = await get_ingestion_manager()
        status = manager.get_ingestion_status()
        
        return {
            "status": "success",
            "ingestion_status": status,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        log.error("Failed to get ingestion status: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/data-ingestion/upload-manual")
async def upload_manual_data(
    file: UploadFile = File(...),
    domain: str = Form("general"),
    user: TokenData = Depends(get_current_user),
):
    """
    Manually upload CSV or JSON data for ingestion.
    
    Supported formats:
    - CSV: company, domain, metric, value, period, date
    - JSON: Array of objects with same fields
    
    Parameters:
    - file: CSV or JSON file
    - domain: Domain to associate with this data
    """
    try:
        content = await file.read()
        filename = file.filename or "upload"
        
        log.info(
            "User %s uploading manual data: %s (domain: %s)",
            user.username, filename, domain
        )
        
        manager = await get_ingestion_manager()
        
        # Parse based on file type
        if filename.endswith('.csv'):
            df = pd.read_csv(BytesIO(content))
        elif filename.endswith('.json'):
            data = json.loads(content.decode('utf-8'))
            df = pd.DataFrame(data)
        else:
            raise ValueError("Unsupported file format. Use CSV or JSON.")
        
        # Ingest records
        stats = await manager.ingest_all_data(percentage=100, domains=[domain])
        
        return {
            "status": "success",
            "message": f"Uploaded and ingested {stats.ingested_records} records",
            "filename": filename,
            "domain": domain,
            "ingested_records": stats.ingested_records,
            "failed_records": stats.failed_records,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        log.error("Manual data upload failed: %s", e)
        raise HTTPException(status_code=400, detail=str(e))

