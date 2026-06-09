"""In-process smoke tests for IntelAI.

These run without a live server or a real database by importing the FastAPI
app and exercising it through Starlette's TestClient. The live-server
integration checks live in ``test_api.py`` and require ``uvicorn`` + Postgres
to be running (see STATUS.md / Phase 1 Day 11).
"""
import os

import pytest

os.environ.setdefault("POSTGRES_URL", "postgresql://localhost/intelai_test")


@pytest.fixture(scope="module")
def client():
    from fastapi.testclient import TestClient

    from src.api.server_v2 import app

    return TestClient(app)


def test_core_imports():
    """Shared core utilities import cleanly without a database."""
    from src.core import config, logger

    assert config is not None
    assert logger is not None


def test_app_imports_and_has_routes():
    """The FastAPI app object builds and registers its routes."""
    from src.api.server_v2 import app

    assert len(app.routes) > 50


def test_health_endpoint(client):
    """/health responds 200 in-process (no DB required)."""
    r = client.get("/health")
    assert r.status_code == 200


def test_openapi_schema(client):
    """OpenAPI schema is generated and exposes the documented surface."""
    r = client.get("/openapi.json")
    assert r.status_code == 200
    assert len(r.json().get("paths", {})) > 20


def test_docs_served(client):
    """Interactive API docs are served at the configured docs URL."""
    from src.api.server_v2 import app

    r = client.get(app.docs_url)
    assert r.status_code == 200
