"""Shared test setup: ensure the DB schema, a bootstrap admin, and seed data exist so the
DB-backed tests run (no skips) wherever a Postgres is reachable (CI service or the Studio's
Neon via .env)."""
import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
os.environ.setdefault("POSTGRES_URL", "postgresql://localhost/intelai_test")

ADMIN_USER = os.getenv("BOOTSTRAP_ADMIN_USERNAME", "admin")
ADMIN_PASS = os.getenv("BOOTSTRAP_ADMIN_PASSWORD", "admin123")


@pytest.fixture(scope="session", autouse=True)
def _init_db():
    """Create tables, bootstrap admin, and seed KPIs/knowledge once per test session."""
    from src.services.pg_store import (
        init_pg_tables, get_user, create_user, get_kpi_metrics, seed_all_domains,
    )
    from src.core.jwt_auth import hash_password

    init_pg_tables()
    if not get_user(ADMIN_USER):
        create_user(ADMIN_USER, hash_password(ADMIN_PASS), "admin")
    try:
        empty = get_kpi_metrics().empty
    except Exception:
        empty = True
    if empty:
        seed_all_domains()
    yield
