"""
IntelAI API v1 — FastAPI server with JWT auth, RBAC, multi-domain intelligence.

Persona-aware AI analytics & RAG copilot. Domains: Finance, HR, Logistics, IT,
Operations, ESG, Growth/Risk.
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
    title="IntelAI API",
    description="Persona-Aware AI Analytics & RAG Copilot — Multi-Domain KPI Intelligence",
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
    log.info("🚀 IntelAI API starting...")

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

    log.info("✅ IntelAI API ready")


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
        "service": "IntelAI API",
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
    from src.services.omnismart_chatbot import get_persona_factory

    session_id = req.session_id or str(uuid.uuid4())

    # Ensure session exists in PostgreSQL
    try:
        from src.services.pg_store import ensure_session_exists, store_message
        ensure_session_exists(session_id, user.user_id)
    except Exception:
        pass  # Fallback — still works without PG

    # Persona-routed RAG copilot: factory.chat auto-retrieves a role-scoped KPI
    # snapshot + knowledge docs and returns grounded answers with source citations.
    # (Same path as the WebSocket handler, so REST and the WS fallback behave identically.)
    factory = get_persona_factory()
    result = factory.chat(
        message=req.message,
        user_role=user.role,
        persona_override=req.persona,
        language=user.language,
        context=req.context or "",
    )

    response_text = result.get("response", "")
    sources = result.get("sources", [])

    # Persist both messages to PostgreSQL
    try:
        store_message(session_id, "user", req.message)
        store_message(
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
    }


@app.get("/api/v1/personas")
async def list_personas(user: TokenData = Depends(get_current_user)):
    from src.services.omnismart_chatbot import get_persona_factory
    factory = get_persona_factory()
    return {"personas": factory.list_personas(user_role=user.role)}


@app.get("/api/v1/glossary")
async def get_glossary(
    domain: Optional[str] = None,
    term: Optional[str] = None,
    user: TokenData = Depends(get_current_user),
):
    """Authoritative, sourced domain glossary — powers the per-page contextual
    explainer and grounds term definitions (no hallucination)."""
    from src.data.glossary import for_domain, get_term
    if term:
        entry = get_term(term)
        if not entry:
            raise HTTPException(status_code=404, detail=f"Term not found: {term}")
        return entry
    return {"terms": for_domain(domain)}


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
                "sources": result.get("sources", []),
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
        
        # csv/json are returned as text; xlsx is base64-encoded so the client can
        # decode and download it directly (no separate download round-trip).
        return {
            "status": "success",
            "export_id": export_id,
            "format": req.format,
            "filename": filename,
            "encoding": "base64" if req.format == "xlsx" else "text",
            "data": data,
            "download_url": f"/api/v1/exports/{export_id}/download",
        }
    
    except HTTPException:
        raise
    except Exception as e:
        log.error("Data export error: %s", e)
        update_export_log(export_id=export_id, status="failed", error_message=str(e)[:500])
        raise HTTPException(status_code=500, detail=str(e))
