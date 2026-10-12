import asyncio
import os
import uuid
from types import SimpleNamespace
from urllib.parse import urlsplit

import pytest
from fastapi import HTTPException

from src.api import server
from src.services import pg_store


@pytest.fixture
def migration_schema(monkeypatch):
    if os.getenv("RUN_POSTGRES_MIGRATION_TESTS") != "true":
        pytest.skip("Postgres migration tests are enabled only in the isolated CI database")
    dsn = os.getenv("TEST_POSTGRES_URL")
    if not dsn:
        pytest.skip("TEST_POSTGRES_URL is not configured")
    if urlsplit(dsn).hostname not in {"localhost", "127.0.0.1", "::1"}:
        pytest.fail("Migration tests require a loopback-only Postgres database")

    import psycopg
    from psycopg import sql
    from psycopg.conninfo import make_conninfo

    schema = f"migration_test_{uuid.uuid4().hex}"
    admin = psycopg.connect(dsn, autocommit=True)
    admin.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema)))

    def connect_to_schema():
        return psycopg.connect(
            make_conninfo(dsn, options=f"-c search_path={schema}")
        )

    monkeypatch.setattr(pg_store, "_get_conn", connect_to_schema)
    monkeypatch.setattr(pg_store, "seed_glossary_knowledge_docs", lambda: None)
    try:
        yield admin, schema
    finally:
        admin.execute(sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(schema)))
        admin.close()


def _columns(conn, schema, table):
    return {
        row[0]
        for row in conn.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_schema = %s AND table_name = %s",
            (schema, table),
        ).fetchall()
    }


def test_clean_database_bootstraps_idempotently(migration_schema):
    admin, schema = migration_schema

    pg_store.init_pg_tables()
    pg_store.init_pg_tables()

    tables = {
        row[0]
        for row in admin.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = %s",
            (schema,),
        ).fetchall()
    }
    assert {"users", "kpi_metrics", "knowledge_base", "chat_jobs"} <= tables
    assert "owner_user_id" in _columns(admin, schema, "kpi_metrics")


def test_legacy_schema_migrations_preserve_rows(migration_schema):
    admin, schema = migration_schema
    admin.execute(f'SET search_path TO "{schema}"')
    admin.execute(
        """
        CREATE TABLE kpi_metrics (
            id SERIAL PRIMARY KEY, period TEXT NOT NULL, metric TEXT NOT NULL,
            value DOUBLE PRECISION NOT NULL, category TEXT NOT NULL,
            segment TEXT DEFAULT '', unit TEXT DEFAULT '',
            direction TEXT DEFAULT 'higher_is_better', source TEXT DEFAULT 'manual',
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    admin.execute(
        """
        CREATE TABLE kpi_entities (
            id SERIAL PRIMARY KEY, record_ref TEXT NOT NULL, entity_type TEXT NOT NULL,
            entity_value TEXT NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    admin.execute(
        """
        CREATE TABLE knowledge_base (
            doc_id TEXT PRIMARY KEY, title TEXT NOT NULL, content TEXT NOT NULL,
            source TEXT DEFAULT 'manual', embedding TEXT DEFAULT '',
            language TEXT DEFAULT 'en', created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    admin.execute(
        "INSERT INTO kpi_metrics (period, metric, value, category) VALUES ('2026-Q1', 'revenue', 42, 'finance')"
    )
    admin.execute(
        "INSERT INTO kpi_entities (record_ref, entity_type, entity_value) VALUES ('r1', 'company', 'Example')"
    )
    admin.execute(
        "INSERT INTO knowledge_base (doc_id, title, content) VALUES ('d1', 'Legacy', 'kept')"
    )
    admin.commit()

    pg_store.init_pg_tables()
    pg_store.init_pg_tables()

    assert "owner_user_id" in _columns(admin, schema, "kpi_metrics")
    assert "source" in _columns(admin, schema, "kpi_entities")
    assert "owner_user_id" in _columns(admin, schema, "knowledge_base")
    assert admin.execute("SELECT COUNT(*) FROM kpi_metrics").fetchone()[0] == 1
    assert admin.execute("SELECT entity_value FROM kpi_entities").fetchone()[0] == "Example"
    assert admin.execute("SELECT content FROM knowledge_base").fetchone()[0] == "kept"


def test_production_startup_fails_when_required_database_bootstrap_fails(monkeypatch):
    from src.core import config

    monkeypatch.setattr(config, "validate_required_keys", lambda: None)
    monkeypatch.setattr(
        server,
        "settings",
        SimpleNamespace(ENVIRONMENT="production", VECTOR_STORE="qdrant"),
    )

    def fail_init():
        raise OSError("simulated migration failure")

    monkeypatch.setattr(pg_store, "init_pg_tables", fail_init)
    with pytest.raises(RuntimeError, match="Required PostgreSQL bootstrap or migration failed"):
        asyncio.run(server.startup())


def test_persistent_storage_requires_postgres_bootstrap():
    assert server._requires_persistent_database("production", "memory")
    assert server._requires_persistent_database("development", "qdrant")
    assert not server._requires_persistent_database("development", "memory")


def test_readiness_rejects_degraded_service(monkeypatch):
    async def degraded():
        return {"status": "degraded", "database": "unreachable"}

    monkeypatch.setattr(server, "health_check", degraded)
    with pytest.raises(HTTPException) as exc:
        asyncio.run(server.readiness_check())
    assert exc.value.status_code == 503
