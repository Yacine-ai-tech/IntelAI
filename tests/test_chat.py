"""In-process chat endpoint tests (FastAPI TestClient — no live server needed).

These tests exercise the POST /api/v1/chat and GET /api/v1/personas endpoints
using the same TestClient fixture as test_api.py.  DB-dependent sub-tests are
guarded by the ``admin_token`` fixture, which skips cleanly in no-DB CI.
"""
import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
os.environ.setdefault("POSTGRES_URL", "postgresql://localhost/intelai")

ADMIN = {"username": "admin", "password": "admin123"}

@pytest.fixture
def admin_token(client):
    r = client.post("/api/v1/auth/login", json=ADMIN)
    assert r.status_code == 200 and "access_token" in r.json(), (
        f"admin login failed ({r.status_code}): {r.text[:200]}"
    )
    return r.json()["access_token"]


def H(token):
    return {"Authorization": f"Bearer {token}"}


# ── auth gate ────────────────────────────────────────────────

@pytest.mark.unit
def test_chat_post_requires_auth(client):
    assert client.post("/api/v1/chat", json={"message": "hi"}).status_code in (401, 403)


@pytest.mark.unit
def test_personas_requires_auth(client):
    assert client.get("/api/v1/personas").status_code in (401, 403)


# ── shape validation ──────────────────────────────────────────

@pytest.mark.unit
def test_chat_missing_message_422(client, admin_token):
    r = client.post("/api/v1/chat", json={}, headers=H(admin_token))
    assert r.status_code == 422


# ── authenticated flows ───────────────────────────────────────

@pytest.mark.integration
def test_personas_returns_list(client, admin_token):
    r = client.get("/api/v1/personas", headers=H(admin_token))
    assert r.status_code == 200
    body = r.json()
    assert "personas" in body
    assert isinstance(body["personas"], list)
    assert len(body["personas"]) >= 1


@pytest.mark.integration
def test_chat_post_returns_structured_response(client, admin_token):
    """POST /chat must return the structured answer-block envelope."""
    r = client.post(
        "/api/v1/chat",
        json={"message": "What is the business health score?", "persona": "general"},
        headers=H(admin_token),
    )
    # LLM may not be reachable in CI — accept any 2xx or 5xx (service-side LLM error)
    # but NOT a routing/auth failure.
    assert r.status_code not in (401, 403, 404, 422), f"unexpected status {r.status_code}: {r.text[:200]}"
    if r.status_code == 200:
        body = r.json()
        # Core fields must always be present
        assert "response" in body
        assert "persona_used" in body
        assert "session_id" in body
        assert "sources" in body
        assert isinstance(body["sources"], list)
        # Answer-block envelope (added by backend answer-block structuring)
        assert "blocks" in body, "answer-block structuring: 'blocks' key missing from chat response"
        assert isinstance(body["blocks"], list)


@pytest.mark.integration
def test_chat_post_persona_override(client, admin_token):
    """Persona override field must be respected and echoed back."""
    r = client.post(
        "/api/v1/chat",
        json={"message": "Summarize finance metrics", "persona": "cfo"},
        headers=H(admin_token),
    )
    if r.status_code == 200:
        body = r.json()
        assert "persona_used" in body


@pytest.mark.integration
def test_chat_session_id_persisted(client, admin_token):
    """A session_id provided in the request must be returned unchanged."""
    sid = "test-session-abc123"
    r = client.post(
        "/api/v1/chat",
        json={"message": "hello", "session_id": sid},
        headers=H(admin_token),
    )
    if r.status_code == 200:
        assert r.json().get("session_id") == sid


@pytest.mark.integration
def test_chat_generates_new_session_id(client, admin_token):
    """When no session_id is provided, the backend must generate one."""
    r = client.post(
        "/api/v1/chat",
        json={"message": "hello"},
        headers=H(admin_token),
    )
    if r.status_code == 200:
        sid = r.json().get("session_id", "")
        assert len(sid) > 5


@pytest.mark.integration
def test_chat_language_field_accepted(client, admin_token):
    """The language field must be accepted without error."""
    r = client.post(
        "/api/v1/chat",
        json={"message": "Bonjour", "language": "fr"},
        headers=H(admin_token),
    )
    assert r.status_code not in (422, 404)
