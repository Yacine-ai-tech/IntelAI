"""
Unified Configuration — Single source of truth for the entire platform.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

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


# RBAC (roles → pages/actions) and the default user set live in
# ``src.core.jwt_auth`` — the single source of truth used by the API.


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
    # Optional: Anthropic (LiteLLM router can fall back to Claude)
    ANTHROPIC_API_KEY: str = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))

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

    # Security
    SECRET_KEY: str = field(
        default_factory=lambda: os.getenv("SECRET_KEY", "change-me-in-production")
    )
    SESSION_TIMEOUT: int = field(default_factory=lambda: int(os.getenv("SESSION_TIMEOUT", "3600")))

    # Language
    SUPPORTED_LANGUAGES: tuple = ("en", "fr")
    DEFAULT_LANGUAGE: str = field(default_factory=lambda: os.getenv("DEFAULT_LANGUAGE", "en"))

    # LLM — provider-agnostic. LLM_PROVIDER selects the backend (groq uses the Groq SDK
    # directly for speed; any other value routes through LiteLLM → no vendor lock-in).
    LLM_PROVIDER: str = field(default_factory=lambda: os.getenv("LLM_PROVIDER", "groq").strip().lower())
    LLM_MODEL: str = field(default_factory=lambda: os.getenv("LLM_MODEL", "llama-3.1-8b-instant"))
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 2048

    # Embedding / RAG
    EMBEDDING_MODEL: str = field(
        default_factory=lambda: os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    )
    CHROMA_COLLECTION: str = "company_knowledge"
    CHUNK_SIZE: int = 900
    CHUNK_OVERLAP: int = 120

    # Vector store backend — memory (in-process) | chroma (dev) | pgvector (prod, Neon) | qdrant (prod)
    VECTOR_STORE: str = field(
        default_factory=lambda: os.getenv("VECTOR_STORE", "memory").strip().lower()
    )
    QDRANT_URL: str = field(default_factory=lambda: os.getenv("QDRANT_URL", ""))
    QDRANT_API_KEY: str = field(default_factory=lambda: os.getenv("QDRANT_API_KEY", ""))

    # Feature flags — all enabled by default; disabled explicitly via env
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

