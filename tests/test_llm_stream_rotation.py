import asyncio
import types

import pytest

from src.services import omnismart_chatbot as bot

pytestmark = pytest.mark.unit


class _RateLimit(Exception):
    def __str__(self):
        return "429 rate limit exceeded"


def test_stream_falls_back_when_primary_fails_before_any_text(monkeypatch):
    calls = []

    async def fake_stream(messages, temperature, max_tokens, top_p, model, persona_name):
        calls.append(model)
        if model == "groq/primary":
            raise _RateLimit()
        for piece in ("hello ", "world"):
            yield piece

    monkeypatch.setattr(bot, "_llm_stream_model", fake_stream)
    import src.services.llm_router as router
    monkeypatch.setattr(router, "_resolve", lambda tier: "groq/primary")
    monkeypatch.setattr(router, "_fallback_for", lambda tier: "gemini/fallback")
    monkeypatch.setattr(router, "_should_fallback", lambda exc: True)

    async def run():
        return [p async for p in bot.llm_stream([{"role": "user", "content": "hi"}])]

    assert asyncio.run(run()) == ["hello ", "world"]
    assert calls == ["groq/primary", "gemini/fallback"]


def test_groq_call_rotates_keys_on_rate_limit(monkeypatch):
    leases = iter([(types.SimpleNamespace(name="a"), "lease-a"), (types.SimpleNamespace(name="b"), "lease-b")])
    monkeypatch.setattr(bot, "_groq_lease_client", lambda: next(leases))
    monkeypatch.setattr(bot, "_groq_attempts", lambda: 2)
    import src.core.keypool as keypool
    parked = []
    monkeypatch.setattr(keypool, "note_failure", lambda lease, exc: parked.append(lease) or True)

    def fn(client):
        if client.name == "a":
            raise _RateLimit()
        return "ok"

    assert bot._groq_call(fn) == "ok"
    assert parked == ["lease-a"]
