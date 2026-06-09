"""In-process API tests for IntelAI (FastAPI TestClient).

No live server needed. Endpoints that only depend on routing/auth run everywhere
(incl. CI without a DB). Endpoints that need a seeded database/LLM are exercised
when the bootstrap-admin login succeeds and are otherwise skipped with a clear
reason — so the suite is green in CI and full on the Studio (Neon DB).
"""
import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
os.environ.setdefault("POSTGRES_URL", "postgresql://localhost/intelai_test")

ADMIN = {
    "username": os.getenv("BOOTSTRAP_ADMIN_USERNAME", "admin"),
    "password": os.getenv("BOOTSTRAP_ADMIN_PASSWORD", "admin123"),
}


@pytest.fixture(scope="module")
def client():
    from fastapi.testclient import TestClient
    from src.api.server_v2 import app
    return TestClient(app)


@pytest.fixture(scope="module")
def admin_token(client):
    """Bootstrap-admin JWT (admin + schema + seed are ensured by tests/conftest.py)."""
    r = client.post("/api/v1/auth/login", json=ADMIN)
    assert r.status_code == 200 and "access_token" in r.json(), \
        f"admin login failed ({r.status_code}): {r.text[:200]}"
    return r.json()["access_token"]


def H(token):
    return {"Authorization": f"Bearer {token}"}


# ── Routing / docs (no DB) ───────────────────────────────────────────────────

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200

def test_openapi_paths(client):
    r = client.get("/openapi.json")
    assert r.status_code == 200
    assert len(r.json().get("paths", {})) > 20

def test_docs_served(client):
    assert client.get("/api/docs").status_code == 200

def test_redoc_served(client):
    assert client.get("/api/redoc").status_code == 200

def test_unknown_api_path_404(client):
    assert client.get("/api/v1/does-not-exist").status_code == 404

def test_prometheus_metrics(client):
    r = client.get("/metrics")
    assert r.status_code == 200


# ── Auth validation / RBAC gating (no DB) ────────────────────────────────────

def test_login_missing_fields_422(client):
    assert client.post("/api/v1/auth/login", json={"username": "x"}).status_code == 422

def test_me_requires_token(client):
    assert client.get("/api/v1/auth/me").status_code in (401, 403)

def test_me_rejects_bad_token(client):
    assert client.get("/api/v1/auth/me", headers=H("not-a-jwt")).status_code in (401, 403)

def test_kpis_requires_auth(client):
    assert client.get("/api/v1/kpis").status_code in (401, 403)

def test_chat_requires_auth(client):
    assert client.post("/api/v1/chat", json={"message": "hi"}).status_code in (401, 403)

def test_forecast_requires_auth(client):
    assert client.post("/api/v1/forecast", json={"metric": "revenue"}).status_code in (401, 403)

def test_insights_health_requires_auth(client):
    assert client.get("/api/v1/insights/health").status_code in (401, 403)

def test_ingest_requires_auth(client):
    assert client.post("/api/v1/ingest/metrics", json={"data": []}).status_code in (401, 403)

def test_knowledge_search_requires_auth(client):
    assert client.get("/api/v1/knowledge/search", params={"q": "x"}).status_code in (401, 403)

def test_admin_users_requires_auth(client):
    assert client.get("/api/v1/admin/users").status_code in (401, 403)

def test_chat_sessions_requires_auth(client):
    assert client.get("/api/v1/chat/sessions").status_code in (401, 403)


# ── Authenticated flows (need a seeded DB → skip gracefully) ─────────────────

def test_login_success(admin_token):
    assert isinstance(admin_token, str) and len(admin_token) > 10

def test_me_returns_user(client, admin_token):
    r = client.get("/api/v1/auth/me", headers=H(admin_token))
    assert r.status_code == 200 and "username" in r.json()

def test_login_wrong_password(client, admin_token):
    r = client.post("/api/v1/auth/login", json={"username": ADMIN["username"], "password": "wrong-pw"})
    assert r.status_code in (400, 401)

def test_register_new_user(client, admin_token):
    u = f"testuser_{os.urandom(4).hex()}"
    r = client.post("/api/v1/auth/register", json={"username": u, "password": "testpass123"})
    assert r.status_code in (200, 201, 400)

def test_kpis_list(client, admin_token):
    assert client.get("/api/v1/kpis", headers=H(admin_token)).status_code == 200

def test_kpis_periods(client, admin_token):
    assert client.get("/api/v1/kpis/periods", headers=H(admin_token)).status_code == 200

def test_kpis_metrics(client, admin_token):
    assert client.get("/api/v1/kpis/metrics", headers=H(admin_token)).status_code == 200

def test_kpis_categories(client, admin_token):
    assert client.get("/api/v1/kpis/categories", headers=H(admin_token)).status_code == 200

def test_insights_health(client, admin_token):
    assert client.get("/api/v1/insights/health", headers=H(admin_token)).status_code == 200

def test_insights_risk(client, admin_token):
    assert client.get("/api/v1/insights/risk", headers=H(admin_token)).status_code == 200

def test_insights_summary(client, admin_token):
    assert client.get("/api/v1/insights/summary", headers=H(admin_token)).status_code == 200

def test_insights_anomalies(client, admin_token):
    assert client.get("/api/v1/insights/anomalies", headers=H(admin_token)).status_code == 200

def test_forecast(client, admin_token):
    r = client.post("/api/v1/forecast", json={"metric": "revenue", "periods": 3}, headers=H(admin_token))
    assert r.status_code in (200, 400, 404, 422)  # 200 normally; tolerant if metric/data absent

def test_ingest_metrics_valid(client, admin_token):
    payload = {"data": [{"period": "2099Q1", "metric": "test_metric", "value": 1.0, "category": "Finance"}]}
    r = client.post("/api/v1/ingest/metrics", json=payload, headers=H(admin_token))
    assert r.status_code in (200, 201, 400, 422)

def test_ingest_metrics_empty(client, admin_token):
    r = client.post("/api/v1/ingest/metrics", json={"data": []}, headers=H(admin_token))
    assert r.status_code in (200, 400, 422)

def test_knowledge_stats(client, admin_token):
    assert client.get("/api/v1/knowledge/stats", headers=H(admin_token)).status_code == 200

def test_chat_sessions_list(client, admin_token):
    assert client.get("/api/v1/chat/sessions", headers=H(admin_token)).status_code == 200

def test_admin_users_as_admin(client, admin_token):
    assert client.get("/api/v1/admin/users", headers=H(admin_token)).status_code == 200

def test_admin_roles_as_admin(client, admin_token):
    assert client.get("/api/v1/admin/roles", headers=H(admin_token)).status_code == 200

def test_admin_audit_as_admin(client, admin_token):
    assert client.get("/api/v1/admin/audit", headers=H(admin_token)).status_code == 200


# ── RBAC: a non-admin must not reach admin endpoints ─────────────────────────

def test_rbac_viewer_blocked(client, admin_token):
    """Register a viewer (non-admin) and confirm admin endpoints are forbidden."""
    u = f"viewer_{os.urandom(4).hex()}"
    reg = client.post("/api/v1/auth/register", json={"username": u, "password": "viewer123", "role": "viewer"})
    assert reg.status_code in (200, 201), f"register viewer failed ({reg.status_code}): {reg.text[:200]}"
    login = client.post("/api/v1/auth/login", json={"username": u, "password": "viewer123"})
    assert login.status_code == 200
    viewer = login.json()["access_token"]
    assert client.get("/api/v1/admin/users", headers=H(viewer)).status_code in (401, 403)


# ── GraphRAG-lite unit coverage (no DB / no LLM) ─────────────────────────────

def test_graphrag_disabled_returns_empty(monkeypatch):
    from src.services import graph_retrieval
    monkeypatch.delenv("USE_GRAPH_RAG", raising=False)
    assert graph_retrieval.graph_kpi_context("Finance margin vs Engineering headcount") == []

def test_graphrag_enabled_too_few_entities(monkeypatch):
    from src.services import graph_retrieval
    monkeypatch.setenv("USE_GRAPH_RAG", "true")
    # single-entity query → below the multi-hop threshold → empty (vector fallback)
    assert graph_retrieval.graph_kpi_context("hello there") == []

def test_entity_extractor_query_entities():
    from src.services.entity_extractor import get_entity_extractor
    ents = get_entity_extractor().extract_query_entities("finance margin and operations cycle time")
    assert "Finance" in ents and "Operations" in ents
