import asyncio

import pytest

pytestmark = pytest.mark.unit


def test_failed_model_call_is_a_failed_turn(monkeypatch):
    from src.api import server
    from src.core.jwt_auth import TokenData

    class _Factory:
        def chat(self, **kwargs):
            return {"response": "apology", "error": "model_provider_error: Timeout", "sources": []}

    monkeypatch.setattr("src.services.omnismart_chatbot.get_persona_factory", lambda: _Factory())
    monkeypatch.setattr(server, "_load_chat_history", lambda *a, **k: [])
    stored = []
    monkeypatch.setattr("src.services.pg_store.store_message", lambda *a, **k: stored.append(a))
    monkeypatch.setattr("src.services.pg_store.ensure_session_exists", lambda *a, **k: None)

    req = server.ChatRequest(message="hello")
    user = TokenData(user_id="u1", username="u1", role="ceo", language="en")
    with pytest.raises(server.ChatProviderError):
        asyncio.run(server._run_chat_turn(req, user))
    assert stored == []


def test_internal_service_token_is_not_administrator(monkeypatch):
    """The gateway's service token must not widen a visitor's scope to every user."""
    import inspect
    from src.api import server

    for fn in (server.get_chat_messages, server.get_chat_sessions, server.get_user_files):
        src = inspect.getsource(fn)
        assert "x_intelai_token and admin_secret" not in src
        assert "INTELAI_INTERNAL_TOKEN" not in src
