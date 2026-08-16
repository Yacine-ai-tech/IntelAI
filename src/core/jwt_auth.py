"""
JWT Authentication & Authorization — Replaces Streamlit session-based auth.

Provides:
- JWT token generation/validation
- Password hashing (bcrypt via passlib)
- Role-based access control middleware
- FastAPI dependency injection
"""
from __future__ import annotations

import os
import uuid
import json
from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from src.core.logger import get_logger
from src.core.config import settings

log = get_logger(__name__)

# ── Configuration ──────────────────────────────────────────────────────────

SECRET_KEY = os.getenv("JWT_SECRET_KEY", settings.SECRET_KEY)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "480"))  # 8 hours

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)


# ── Pydantic Schemas ───────────────────────────────────────────────────────

class TokenData(BaseModel):
    user_id: str
    username: str
    role: str
    company_id: Optional[str] = None
    language: str = "en"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str = "viewer"
    preferred_language: str = "en"


# ── Password Utilities ────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a password against its bcrypt hash."""
    return pwd_context.verify(plain, hashed)


# ── JWT Token Management ──────────────────────────────────────────────────

def create_access_token(data: TokenData, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = {
        "sub": data.user_id,
        "username": data.username,
        "role": data.role,
        "company_id": data.company_id,
        "language": data.language,
    }
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode["exp"] = expire
    to_encode["iat"] = datetime.utcnow()
    to_encode["jti"] = str(uuid.uuid4())  # Unique token ID
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> TokenData:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return TokenData(
            user_id=payload["sub"],
            username=payload["username"],
            role=payload["role"],
            company_id=payload.get("company_id"),
            language=payload.get("language", "en"),
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ── FastAPI Dependencies ──────────────────────────────────────────────────

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> TokenData:
    """FastAPI dependency: extract and validate the current user from JWT."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return decode_access_token(credentials.credentials)


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[TokenData]:
    """FastAPI dependency: optionally extract user (for public + auth endpoints)."""
    if credentials is None:
        return None
    try:
        return decode_access_token(credentials.credentials)
    except HTTPException:
        return None


# ── Role-Based Access Control ──────────────────────────────────────────────

# Extended role definitions for IntelAI
ROLE_DEFINITIONS = {
    "admin": {
        "pages": ["*"],
        "actions": ["*"],
        "data_access": ["*"],
        "description": "Full system access",
    },
    "ceo": {
        "pages": ["dashboard", "analytics", "assistant", "forecasting", "financial", "esg", "risk", "hr", "logistics", "it", "operations", "settings"],
        "actions": ["read", "analyze", "forecast", "report"],
        "data_access": ["Finance", "Growth", "Operations", "People", "ESG", "IT"],
        "description": "Strategic overview, all domains",
    },
    "cfo": {
        "pages": ["dashboard", "analytics", "assistant", "forecasting", "financial", "data_hub", "settings"],
        "actions": ["read", "analyze", "forecast", "report", "financial_write", "ingest"],
        "data_access": ["Finance", "Growth"],
        "description": "Financial analysis and reporting",
    },
    "cto": {
        "pages": ["dashboard", "analytics", "assistant", "it", "risk", "settings"],
        "actions": ["read", "analyze", "risk_assess"],
        "data_access": ["Operations", "Finance", "IT"],
        "description": "Technology and security oversight",
    },
    "coo": {
        "pages": ["dashboard", "analytics", "assistant", "forecasting", "operations", "logistics", "data_hub", "settings"],
        "actions": ["read", "analyze", "forecast", "ingest"],
        "data_access": ["Operations", "Growth", "People"],
        "description": "Operations management",
    },
    "chro": {
        "pages": ["dashboard", "analytics", "assistant", "hr", "esg", "settings"],
        "actions": ["read", "analyze"],
        "data_access": ["People", "ESG"],
        "description": "People and culture analytics",
    },
    "hr": {
        "pages": ["dashboard", "assistant", "hr", "settings"],
        "actions": ["read"],
        "data_access": ["People"],
        "description": "HR operations",
    },
    "esg": {
        "pages": ["dashboard", "analytics", "assistant", "esg", "settings"],
        "actions": ["read", "analyze", "report"],
        "data_access": ["ESG", "Operations"],
        "description": "ESG monitoring and reporting",
    },
    "risk": {
        "pages": ["dashboard", "analytics", "assistant", "risk", "settings"],
        "actions": ["read", "analyze", "risk_assess", "audit"],
        "data_access": ["Finance", "Operations", "ESG", "IT"],
        "description": "Risk and compliance",
    },
    "analyst": {
        "pages": ["dashboard", "analytics", "assistant", "forecasting", "financial", "data_hub", "hr", "logistics", "it", "operations", "esg", "risk", "settings"],
        "actions": ["read", "analyze", "forecast", "ingest"],
        "data_access": ["Finance", "Growth", "Operations", "People", "ESG", "IT"],
        "description": "Data analysis and insights",
    },
    "board": {
        "pages": ["dashboard", "analytics", "assistant", "esg", "settings"],
        "actions": ["read"],
        "data_access": ["Finance", "Growth", "Operations", "People", "ESG"],
        "description": "Board-level read access",
    },
    "viewer": {
        "pages": ["dashboard", "assistant", "settings"],
        "actions": ["read"],
        "data_access": ["Finance"],
        "description": "Read-only access",
    },
}

def _load_default_users() -> dict:
    """Build bootstrap users from env, keeping insecure defaults opt-in."""
    users_json = os.getenv("OMNI_DEFAULT_USERS_JSON", "").strip()
    if users_json:
        try:
            parsed = json.loads(users_json)
            if isinstance(parsed, dict):
                return parsed
            log.warning("OMNI_DEFAULT_USERS_JSON must be a JSON object; ignoring value")
        except json.JSONDecodeError as exc:
            log.warning("Invalid OMNI_DEFAULT_USERS_JSON: %s", exc)

    if os.getenv("ALLOW_INSECURE_DEFAULT_USERS", "false").lower() == "true":
        log.warning("Using insecure default users; disable in production")
        return {
            "admin": {"password": "admin123", "role": "admin"},
            "ceo": {"password": "ceo123", "role": "ceo"},
            "cfo": {"password": "cfo123", "role": "cfo"},
            "cto": {"password": "cto123", "role": "cto"},
            "coo": {"password": "coo123", "role": "coo"},
            "analyst": {"password": "analyst123", "role": "analyst"},
            "viewer": {"password": "viewer123", "role": "viewer"},
        }

    bootstrap_user = os.getenv("BOOTSTRAP_ADMIN_USERNAME", "").strip()
    bootstrap_pass = os.getenv("BOOTSTRAP_ADMIN_PASSWORD", "").strip()
    if bootstrap_user and bootstrap_pass:
        return {bootstrap_user: {"password": bootstrap_pass, "role": "admin"}}

    return {}


DEFAULT_USERS = _load_default_users()


def require_role(*allowed_roles: str):
    """FastAPI dependency factory: restrict endpoint to specific roles."""
    async def role_checker(user: TokenData = Depends(get_current_user)) -> TokenData:
        if user.role == "admin":
            return user  # Admin bypasses all role checks
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{user.role}' does not have access. Required: {', '.join(allowed_roles)}",
            )
        return user
    return role_checker


def require_action(action: str):
    """FastAPI dependency factory: restrict endpoint to users with specific action permission."""
    async def action_checker(user: TokenData = Depends(get_current_user)) -> TokenData:
        role_def = ROLE_DEFINITIONS.get(user.role, {})
        allowed_actions = role_def.get("actions", [])
        if "*" in allowed_actions or action in allowed_actions:
            return user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Action '{action}' not permitted for role '{user.role}'",
        )
    return action_checker


def require_data_access(category: str):
    """FastAPI dependency factory: restrict endpoint to users with data category access."""
    async def data_checker(user: TokenData = Depends(get_current_user)) -> TokenData:
        role_def = ROLE_DEFINITIONS.get(user.role, {})
        data_access = role_def.get("data_access", [])
        if "*" in data_access or category in data_access:
            return user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Data category '{category}' not accessible for role '{user.role}'",
        )
    return data_checker


def require_page(page: str):
    """FastAPI dependency factory: restrict a domain data endpoint to roles whose
    `pages` list includes it. Without this, App.jsx's ProtectedRoute was the ONLY
    enforcement — hiding /hr, /it, /financial etc. from the nav for a role that
    lacks that page, while the backend endpoints behind them (/api/v1/hr/summary,
    /api/v1/it/overview, /api/v1/financial/statement, ...) accepted any
    authenticated user regardless of role. Confirmed live: a role without "it" in
    its pages list could still call /api/v1/it/overview directly and get full data."""
    async def page_checker(user: TokenData = Depends(get_current_user)) -> TokenData:
        role_def = ROLE_DEFINITIONS.get(user.role, {})
        pages = role_def.get("pages", [])
        if "*" in pages or page in pages:
            return user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Page '{page}' not accessible for role '{user.role}'",
        )
    return page_checker


def get_user_data_categories(role: str, all_categories: Optional[List[str]] = None) -> List[str]:
    """Get the data categories accessible to a given role.

    A wildcard role ("*") means "every category that actually exists" — not a fixed
    list. A hardcoded list here drifts every time a new domain is added to the KPI
    catalog (confirmed live: a hardcoded list missing "IT"/"Logistics" silently zeroed
    out GET /api/v1/kpis for both, for every wildcard-access role, until this was found
    and the list patched by hand — which just moves the same bug to the next new
    domain). It also breaks the moment anyone deploys IntelAI against a different
    dataset with different domain names, since this app is meant to be data-agnostic,
    not hardwired to whatever the current 7 demo domains happen to be.

    `all_categories`: the caller's own query of get_available_categories() (a DISTINCT
    SELECT against kpi_metrics), passed in explicitly rather than fetched here so this
    stays a synchronous, DB-free function — the caller decides how/where to run the
    actual query (e.g. via asyncio.to_thread from an async route handler). Falls back to
    an empty list (not a guessed default) when the caller has no data yet — an empty
    wildcard-access result is honest; a hardcoded guess would just reintroduce this bug
    under a different name.
    """
    role_def = ROLE_DEFINITIONS.get(role, {})
    access = role_def.get("data_access", [])
    if "*" in access:
        return all_categories if all_categories is not None else []
    return access


def get_user_pages(role: str) -> List[str]:
    """Get the pages accessible to a given role."""
    role_def = ROLE_DEFINITIONS.get(role, {})
    return role_def.get("pages", [])
