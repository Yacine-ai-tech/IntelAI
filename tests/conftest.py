"""Shared test setup: ensure the DB schema, the bootstrap admin (in the in-memory auth
store that the login route reads), and seed data exist — so the DB-backed tests RUN (no
skips) wherever a Postgres is reachable (CI service or the Studio's Neon via .env).

This calls the app's own ``_init_default_users`` instead of running full startup, so the
test suite needs a database but NOT the LLM keys (``validate_required_keys`` is skipped).
"""
import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
os.environ.setdefault("POSTGRES_URL", "postgresql://localhost/intelai_test")
# Ensure a bootstrap admin exists for DEFAULT_USERS (used by _init_default_users()).
os.environ.setdefault("BOOTSTRAP_ADMIN_USERNAME", "admin")
os.environ.setdefault("BOOTSTRAP_ADMIN_PASSWORD", "admin123")


@pytest.fixture(scope="session", autouse=True)
def _init_db():
    """Create tables, seed the bootstrap admin (in-memory + DB), and seed KPIs/knowledge."""
    from src.api import server
    from src.services.pg_store import init_pg_tables, get_kpi_metrics, seed_all_domains

    init_pg_tables()
    server._init_default_users()  # populates server._users_db (read by /auth/login)
    try:
        empty = get_kpi_metrics().empty
    except Exception:
        empty = True
    if empty:
        seed_all_domains()
    yield
