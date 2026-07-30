"""In-process smoke tests for IntelAI.

These run without a live server or a real database by importing the FastAPI
app and exercising it through Starlette's TestClient. The live-server
integration checks live in ``test_api.py`` and require ``uvicorn`` + Postgres
to be running (see STATUS.md / Phase 1 Day 11).
"""
import os

import pytest

os.environ.setdefault("POSTGRES_URL", "postgresql://user:password@localhost/health responds 200 in-process (no DB required)."""
    r = client.get("/health")
    assert r.status_code == 200


@pytest.mark.unit
def test_openapi_schema(client):
    """OpenAPI schema is generated and exposes the documented surface."""
    r = client.get("/openapi.json")
    assert r.status_code == 200
    assert len(r.json().get("paths", {})) > 20


@pytest.mark.unit
def test_docs_served(client):
    """Interactive API docs are served at the configured docs URL."""
    from src.api.server import app

    r = client.get(app.docs_url)
    assert r.status_code == 200
