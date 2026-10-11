"""Unit tests for demo session scoping and admin bypass in IntelAI."""
import os
import json
import secrets
import pytest
from unittest.mock import MagicMock, patch

from src.core.jwt_auth import _load_default_users
from src.services import pg_store


class _MockConn:
    def __init__(self):
        self.last_query = ""
        self.last_params = None

    def execute(self, sql, params=None):
        self.last_query = sql
        self.last_params = params
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        return mock_cursor

    def close(self):
        pass


@pytest.mark.unit
def test_demo_mode_does_not_create_builtin_users():
    with patch.dict(os.environ, {
        "DEMO_MODE": "true",
        "ALLOW_INSECURE_DEFAULT_USERS": "true",
        "OMNI_DEFAULT_USERS_JSON": "",
        "BOOTSTRAP_ADMIN_USERNAME": "",
        "BOOTSTRAP_ADMIN_PASSWORD": "",
    }, clear=True):
        users = _load_default_users()
    assert users == {}


@pytest.mark.unit
def test_bootstrap_users_require_explicit_environment_credentials():
    password = secrets.token_urlsafe(24)
    configured = {"analyst": {"password": password, "role": "analyst"}}
    with patch.dict(os.environ, {
        "DEMO_MODE": "true",
        "OMNI_DEFAULT_USERS_JSON": json.dumps(configured),
        "BOOTSTRAP_ADMIN_USERNAME": "",
        "BOOTSTRAP_ADMIN_PASSWORD": "",
    }, clear=True):
        users = _load_default_users()
    assert users == configured


@pytest.mark.unit
def test_demo_login_never_issues_admin_token(monkeypatch):
    from fastapi.testclient import TestClient
    from src.api.server import app

    monkeypatch.setenv("DEMO_MODE", "true")
    response = TestClient(app).post("/api/v1/auth/demo-login?role=admin")
    assert response.status_code == 403


@pytest.mark.unit
def test_demo_login_is_disabled_when_setting_is_missing(monkeypatch):
    from fastapi.testclient import TestClient
    from src.api.server import app

    monkeypatch.delenv("DEMO_MODE", raising=False)
    response = TestClient(app).post("/api/v1/auth/demo-login?role=cfo")
    assert response.status_code == 403


@pytest.mark.unit
def test_get_user_sessions_scoping():
    mock_conn = _MockConn()
    with patch.object(pg_store, "_get_conn", return_value=mock_conn):
        # Visitor session query
        pg_store.get_user_sessions("visitor-session-abc", limit=20)
        assert "WHERE s.user_id = %s" in mock_conn.last_query
        assert mock_conn.last_params == ["visitor-session-abc", 20]

        # Admin global query
        pg_store.get_user_sessions("*", limit=50)
        assert "WHERE s.user_id = %s" not in mock_conn.last_query
        assert mock_conn.last_params == [50]


@pytest.mark.unit
def test_get_session_messages_scoping():
    mock_conn = _MockConn()
    with patch.object(pg_store, "_get_conn", return_value=mock_conn):
        # Visitor message query
        pg_store.get_session_messages("sess-1", "user-123", limit=30)
        assert "s.user_id = %s" in mock_conn.last_query
        assert mock_conn.last_params == ["sess-1", "user-123", 30]

        # Admin wildcard query
        pg_store.get_session_messages("sess-1", "*", limit=100)
        assert "s.user_id = %s" not in mock_conn.last_query
        assert mock_conn.last_params == ["sess-1", 100]


@pytest.mark.unit
def test_get_user_files_scoping():
    mock_conn = _MockConn()
    with patch.object(pg_store, "_get_conn", return_value=mock_conn):
        # Visitor files query
        pg_store.get_user_files("analyst-123", limit=10, offset=0)
        assert "WHERE username = %s" in mock_conn.last_query
        assert mock_conn.last_params == ["analyst-123", 10, 0]

        # Admin wildcard files query
        pg_store.get_user_files("*", limit=10, offset=0)
        assert "WHERE username = %s" not in mock_conn.last_query
        assert mock_conn.last_params == [10, 0]
