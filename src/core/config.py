"""
Unified Configuration — Single source of truth for the entire platform.
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

# ── Paths ───────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = BASE_DIR / "uploads"
LOGS_DIR = BASE_DIR / "logs"
CHROMA_DIR = BASE_DIR / "chroma_db"

for _d in (DATA_DIR, UPLOADS_DIR, LOGS_DIR, CHROMA_DIR):
    _d.mkdir(parents=True, exist_ok=True)


# ── Enums ───────────────────────────────────────────────────────────────────
class Role(str, Enum):
    ADMIN = "admin"
    CFO = "cfo"
    COO = "coo"
    HR = "hr"
    ESG = "esg"
    ANALYST = "analyst"
    VIEWER = "viewer"


class DataCategory(str, Enum):
    FINANCE = "Finance"
    GROWTH = "Growth"
    OPERATIONS = "Operations"
    PEOPLE = "People"
    ESG = "ESG"


class DocumentType(str, Enum):
    INVOICE = "Invoice"
    RECEIPT = "Receipt"
    STATEMENT = "Statement"
    REPORT = "Report"
    CONTRACT = "Contract"
    OTHER = "Other"


# ── RBAC Definitions ───────────────────────────────────────────────────────
ROLE_DEFINITIONS: Dict[Role, Dict[str, Any]] = {
    Role.ADMIN: {
        "name": "Administrator",
        "pages": ["all"],
        "actions": ["read", "write", "delete", "admin"],
        "data_access": ["all"],
        "can_manage_users": True,
        "can_view_audit": True,
        "can_manage_roles": True,
    },
    Role.CFO: {
        "name": "Chief Financial Officer",
        "pages": [
            "Dashboard", "Assistant", "Analytics", "Knowledge Base",
            "Data Hub", "Forecasting", "Risk Radar", "Settings",
        ],
        "actions": ["read", "write"],
        "data_access": ["finance", "growth", "operations", "forecast", "risk"],
        "can_manage_users": False,
        "can_view_audit": True,
        "can_manage_roles": False,
    },
    Role.COO: {
        "name": "Chief Operating Officer",
        "pages": [
            "Dashboard", "Assistant", "Analytics", "Knowledge Base",
            "Data Hub", "Forecasting", "Risk Radar", "Settings",
        ],
        "actions": ["read", "write"],
        "data_access": ["operations", "finance", "risk", "forecast"],
        "can_manage_users": False,
        "can_view_audit": True,
        "can_manage_roles": False,
    },
    Role.HR: {
        "name": "HR Director",
        "pages": [
            "Dashboard", "Assistant", "Analytics", "Knowledge Base",
            "ESG", "Settings",
        ],
        "actions": ["read", "write"],
        "data_access": ["people", "esg", "executive"],
        "can_manage_users": False,
        "can_view_audit": False,
        "can_manage_roles": False,
    },
    Role.ESG: {
        "name": "ESG Officer",
        "pages": [
            "Dashboard", "Assistant", "Analytics", "Knowledge Base",
            "ESG", "Risk Radar", "Settings",
        ],
        "actions": ["read", "write"],
        "data_access": ["esg", "risk", "executive", "operations"],
        "can_manage_users": False,
        "can_view_audit": False,
        "can_manage_roles": False,
    },
    Role.ANALYST: {
        "name": "Data Analyst",
        "pages": [
            "Dashboard", "Assistant", "Analytics", "Knowledge Base",
            "Data Hub", "Forecasting", "ESG", "Risk Radar", "Settings",
        ],
        "actions": ["read", "write"],
        "data_access": ["all"],
        "can_manage_users": False,
        "can_view_audit": False,
        "can_manage_roles": False,
    },
    Role.VIEWER: {
        "name": "Viewer",
        "pages": ["Dashboard", "Assistant", "Settings"],
        "actions": ["read"],
        "data_access": ["executive"],
        "can_manage_users": False,
        "can_view_audit": False,
        "can_manage_roles": False,
    },
}


# ── Settings ───────────────────────────────────────────────────────────────
@dataclass(frozen=True)
class Settings:
    """Immutable application settings loaded once at startup."""

    # Runtime environment
    ENVIRONMENT: str = field(default_factory=lambda: os.getenv("ENVIRONMENT", "development").lower())

    # Paths
    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = DATA_DIR
    UPLOADS_DIR: Path = UPLOADS_DIR
    LOGS_DIR: Path = LOGS_DIR
    CHROMA_DB_PATH: str = field(
        default_factory=lambda: os.getenv("CHROMA_DB_PATH", str(CHROMA_DIR))
    )

    # PostgreSQL — primary and only database
    POSTGRES_URL: str = field(
        default_factory=lambda: os.getenv(
            "POSTGRES_URL", "postgresql://omniintel:change_me_postgres_password@localhost:5432/omniintelos"
        )
    )

    # API keys — required; validated at startup
    GROQ_API_KEY: str = field(default_factory=lambda: os.getenv("GROQ_API_KEY", ""))
    TAVILY_API_KEY: str = field(default_factory=lambda: os.getenv("TAVILY_API_KEY", ""))

    # n8n
    N8N_BASE_URL: str = field(
        default_factory=lambda: os.getenv("N8N_BASE_URL", "http://localhost:5678")
    )
    N8N_API_KEY: str = field(default_factory=lambda: os.getenv("N8N_API_KEY", ""))

    # Google OAuth2 (via n8n)
    GMAIL_PRIMARY: str = field(default_factory=lambda: os.getenv("GMAIL_PRIMARY", ""))
    DRIVE_ACCOUNT: str = field(default_factory=lambda: os.getenv("DRIVE_ACCOUNT", ""))
    GSHEETS_ACCOUNT: str = field(default_factory=lambda: os.getenv("GSHEETS_ACCOUNT", ""))
    GOOGLE_CLIENT_ID: str = field(default_factory=lambda: os.getenv("GOOGLE_CLIENT_ID", ""))
    GOOGLE_CLIENT_SECRET: str = field(default_factory=lambda: os.getenv("GOOGLE_CLIENT_SECRET", ""))

    # ClickUp
    CLICKUP_API_KEY: str = field(default_factory=lambda: os.getenv("CLICKUP_API_KEY", ""))
    CLICKUP_WORKSPACE_ID: str = field(default_factory=lambda: os.getenv("CLICKUP_WORKSPACE_ID", ""))
    CLICKUP_ACCOUNT: str = field(default_factory=lambda: os.getenv("CLICKUP_ACCOUNT", ""))

    # Cloudflare tunnel
    TUNNEL_URL: str = field(default_factory=lambda: os.getenv("TUNNEL_URL", ""))

    # FastAPI
    FASTAPI_HOST: str = field(default_factory=lambda: os.getenv("FASTAPI_HOST", "0.0.0.0"))
    FASTAPI_PORT: int = field(default_factory=lambda: int(os.getenv("FASTAPI_PORT", "8000")))

    # Frontend base URL (used for OAuth redirects)
    FRONTEND_URL: str = field(default_factory=lambda: os.getenv("FRONTEND_URL", "http://localhost:5173"))
    CORS_ALLOWED_ORIGINS: str = field(
        default_factory=lambda: os.getenv(
            "CORS_ALLOWED_ORIGINS",
            "http://localhost:5173,http://localhost:3001,http://localhost:8000,http://localhost:8501",
        )
    )

    # Microservices URLs (internal Docker network)
    OCR_SERVICE_URL: str = field(
        default_factory=lambda: os.getenv("OCR_SERVICE_URL", "http://omnitel-ocr:8001")
    )
    VOICE_SERVICE_URL: str = field(
        default_factory=lambda: os.getenv("VOICE_SERVICE_URL", "http://omnitel-voice:8002")
    )

    # Security
    SECRET_KEY: str = field(
        default_factory=lambda: os.getenv("SECRET_KEY", "change-me-in-production")
    )
    SESSION_TIMEOUT: int = field(default_factory=lambda: int(os.getenv("SESSION_TIMEOUT", "3600")))

    # Language
    SUPPORTED_LANGUAGES: tuple = ("en", "fr")
    DEFAULT_LANGUAGE: str = field(default_factory=lambda: os.getenv("DEFAULT_LANGUAGE", "en"))

    # LLM — Groq is the only provider
    LLM_MODEL: str = field(default_factory=lambda: os.getenv("LLM_MODEL", "llama-3.1-8b-instant"))
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 2048

    # Voice (Groq Whisper)
    VOICE_MODEL: str = "whisper-large-v3-turbo"

    # Embedding / RAG
    EMBEDDING_MODEL: str = field(
        default_factory=lambda: os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    )
    CHROMA_COLLECTION: str = "company_knowledge"
    CHUNK_SIZE: int = 900
    CHUNK_OVERLAP: int = 120

    # Feature flags — all enabled by default; disabled explicitly via env
    FEATURE_VOICE: bool = field(
        default_factory=lambda: os.getenv("FEATURE_VOICE", "true").lower() == "true"
    )
    FEATURE_N8N: bool = field(
        default_factory=lambda: os.getenv("FEATURE_N8N", "true").lower() == "true"
    )
    FEATURE_RAG: bool = field(
        default_factory=lambda: os.getenv("FEATURE_RAG", "true").lower() == "true"
    )
    FEATURE_MONTE_CARLO: bool = field(
        default_factory=lambda: os.getenv("FEATURE_MONTE_CARLO", "true").lower() == "true"
    )

    # Logging
    LOG_LEVEL: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    LOG_FORMAT: str = "%(asctime)s | %(name)-20s | %(levelname)-7s | %(message)s"

    # Cache
    CACHE_TTL: int = 300
    MAX_CACHE_SIZE: int = 1000


settings = Settings()


# ── Startup validation ─────────────────────────────────────────────────────
def validate_required_keys() -> None:
    """Fail fast if required API keys are missing."""
    missing = []
    if not settings.GROQ_API_KEY:
        missing.append("GROQ_API_KEY")
    if not settings.TAVILY_API_KEY:
        missing.append("TAVILY_API_KEY")
    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing)}. "
            "Set them in .env before starting the platform."
        )

    if settings.ENVIRONMENT == "production" and settings.SECRET_KEY == "change-me-in-production":
        raise EnvironmentError(
            "Insecure SECRET_KEY for production environment. "
            "Set a strong random SECRET_KEY in .env."
        )


def get_cors_allowed_origins() -> List[str]:
    """Parse and normalize CORS origins from env."""
    origins = [o.strip() for o in settings.CORS_ALLOWED_ORIGINS.split(",") if o.strip()]
    return origins or ["http://localhost:5173"]


# ── Helpers ─────────────────────────────────────────────────────────────────
def get_role_definition(role: str) -> Dict[str, Any]:
    try:
        return ROLE_DEFINITIONS[Role(role)]
    except (ValueError, KeyError):
        return {}


def get_role_pages(role: str) -> List[str]:
    return get_role_definition(role).get("pages", [])


def has_role_permission(role: str, action: str) -> bool:
    return action in get_role_definition(role).get("actions", [])


def has_data_access(role: str, category: str) -> bool:
    access = get_role_definition(role).get("data_access", [])
    return "all" in access or category.lower() in access


def get_all_roles() -> Dict[str, str]:
    return {r.value: d["name"] for r, d in ROLE_DEFINITIONS.items()}

