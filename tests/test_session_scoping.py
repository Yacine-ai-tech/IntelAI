"""Unit tests for demo session scoping and admin bypass in IntelAI."""
import os
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
def test_load_default_users_in_demo_mode():
    with patch.dict(os.environ, {"DEMO_MODE": "true", "ALLOW_INSECURE_DEFAULT_USERS": "false"}, clear=False):
        users = _load_default_users()
        assert "analyst" in users
        assert users["analyst"]["password"] == "analyst123"
        assert "admin" in users


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
