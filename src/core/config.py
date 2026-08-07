"""
Unified Configuration — Single source of truth for all IntelAI runtime settings.

All values are loaded from environment variables at startup. Defaults are safe
for local development only. Always set the required secrets (GROQ_API_KEY or
another LLM key, POSTGRES_URL, SECRET_KEY) via the platform's environment
configuration (e.g., Render environment variables) before deploying to production.
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

    POSTGRES_URL: str = field(
        default_factory=lambda: os.getenv("POSTGRES_URL", "")
    )

    # External Microservice APIs — set via env in production (STRATEGY.md § Decoupling)
    # Defaults target the live production endpoints on the custom domain.
    VISION_API_URL: str = field(
        default_factory=lambda: os.getenv("VISION_API_URL", "http://localhost:8000")
    )
    VOICE_API_URL: str = field(
        default_factory=lambda: os.getenv("VOICE_API_URL", "http://localhost:8000")
    )

    # LLM API keys — at least one must be set; validated at startup.
    GROQ_API_KEY: str = field(default_factory=lambda: os.getenv("GROQ_API_KEY", ""))
    # Anthropic Claude — optional; enables LiteLLM routing to Claude models.
    ANTHROPIC_API_KEY: str = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    # Tavily — optional; enables real-time web search to augment RAG responses
    # with cited, up-to-date external sources.
    TAVILY_API_KEY: str = field(default_factory=lambda: os.getenv("TAVILY_API_KEY", ""))
    WEB_SEARCH_MAX_RESULTS: int = field(default_factory=lambda: int(os.getenv("WEB_SEARCH_MAX_RESULTS", "4")))

    # FastAPI
    FASTAPI_HOST: str = field(default_factory=lambda: os.getenv("FASTAPI_HOST", "0.0.0.0"))
    FASTAPI_PORT: int = field(default_factory=lambda: int(os.getenv("PORT", os.getenv("FASTAPI_PORT", "8000"))))

    # Frontend base URL (used for OAuth redirects)
    FRONTEND_URL: str = field(default_factory=lambda: os.getenv("FRONTEND_URL", "http://localhost:5173"))
    CORS_ALLOWED_ORIGINS: str = field(
        default_factory=lambda: os.getenv(
            "CORS_ALLOWED_ORIGINS",
            "http://localhost:5173,http://localhost:3001,http://localhost:8000,http://localhost:8501",
        )
    )

    # Security — SECRET_KEY must be set to a strong random value in production.
    # Generate one with: python3 -c "import secrets; print(secrets.token_hex(32))"
    SECRET_KEY: str = field(
        default_factory=lambda: os.getenv("SECRET_KEY", "change-me-in-production")
    )
    SESSION_TIMEOUT: int = field(default_factory=lambda: int(os.getenv("SESSION_TIMEOUT", "3600")))

    # Language
    SUPPORTED_LANGUAGES: tuple = ("en", "fr")
    DEFAULT_LANGUAGE: str = field(default_factory=lambda: os.getenv("DEFAULT_LANGUAGE", "en"))

    # Display currency for KPI/insight formatting. ISO 4217 code: USD | EUR | GBP | XOF (FCFA) | …
    # This is a presentation setting (symbol + locale rules); it does not perform FX conversion.
    CURRENCY: str = field(default_factory=lambda: os.getenv("CURRENCY", "USD").strip().upper())

    # LLM — provider-agnostic routing.
    # LLM_PROVIDER selects the backend: "groq" uses the Groq SDK directly for lowest
    # latency; any other value routes through LiteLLM for provider-agnostic compatibility.
    LLM_PROVIDER: str = field(default_factory=lambda: os.getenv("LLM_PROVIDER", "groq").strip().lower())
    LLM_MODEL: str = field(default_factory=lambda: os.getenv("LLM_MODEL", "groq/llama-3.1-8b-instant"))
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 2048

    # Embedding / RAG
    EMBEDDING_MODEL: str = field(
        default_factory=lambda: os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    )
    CHROMA_COLLECTION: str = "company_knowledge"
    CHUNK_SIZE: int = 900
    CHUNK_OVERLAP: int = 120

    # Vector store backend selection:
    #   memory   — in-process (development / CI, no persistence)
    #   chroma   — local ChromaDB (development with persistence)
    #   pgvector — Neon PostgreSQL with pgvector extension (recommended for production)
    #   qdrant   — Qdrant Cloud (production; requires QDRANT_URL + QDRANT_API_KEY)
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
    missing = []
    if not any([settings.GROQ_API_KEY, settings.ANTHROPIC_API_KEY, settings.GEMINI_API_KEY, settings.OPENAI_API_KEY]):
        missing.append("ANY_LLM_API_KEY (Groq, Anthropic, Gemini, or OpenAI)")
    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing)}. "
            "Set them in .env before starting the platform."
        )

    if settings.ENVIRONMENT == "production" and settings.SECRET_KEY == "change-me-in-production":
        from src.core.logger import get_logger
        get_logger(__name__).warning("⚠️ Using default SECRET_KEY in production. Please set SECRET_KEY in environment.")


def get_cors_allowed_origins() -> List[str]:
    """Parse and normalize CORS origins from env."""
    origins = [o.strip() for o in settings.CORS_ALLOWED_ORIGINS.split(",") if o.strip()]
    return origins or ["*"]



# The Gemini fallback logic has been removed as it violated the decoupled architecture
# guidelines in STRATEGY.md by forcing IntelAI to route to Gemini when OPENAI_API_KEY was missing.
