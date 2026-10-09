"""Tests for resilient LLM completion and model fallback in chat."""
from unittest.mock import MagicMock, patch
import pytest

from src.services.llm_router import _tune_params_for_model, _should_fallback, _fallback_for
from src.services.omnismart_chatbot import llm_complete


@pytest.mark.unit
def test_tune_params_gemini_timeout():
    """Verify that Gemini timeout is kept within responsive bounds rather than stalling for 60s."""
    params = {"model": "gemini/gemini-3.5-flash-lite", "timeout": 30.0}
    tuned = _tune_params_for_model(params, "gemini/gemini-3.5-flash-lite")
    assert tuned["timeout"] <= 20.0
    assert tuned["timeout"] >= 10.0


@pytest.mark.unit
def test_should_fallback_error_detection():
    """Verify detection of rate limit, timeout, and authentication errors."""
    class RateLimitError(Exception):
        pass

    assert _should_fallback(RateLimitError("429 Resource Exhausted"))
    assert _should_fallback(Exception("503 Service Unavailable"))
    assert not _should_fallback(ValueError("invalid JSON syntax"))


@pytest.mark.unit
@patch("src.services.omnismart_chatbot._litellm_completion")
@patch("src.services.omnismart_chatbot._groq_client")
def test_llm_complete_fallback_recovery(mock_groq, mock_litellm):
    """Verify llm_complete falls back when the primary reasoning model hits rate limit."""
    mock_groq.return_value = None  # Force litellm route

    # Primary model throws 429
    class MockRateLimit(Exception):
        pass

    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock(message=MagicMock(content="Fallback response"))]
    mock_resp.usage = MagicMock(total_tokens=42)

    def side_effect(**kwargs):
        if "gemini" in kwargs.get("model", ""):
            raise MockRateLimit("429 RateLimitError: Resource Exhausted")
        return mock_resp

    mock_litellm.side_effect = side_effect

    messages = [{"role": "user", "content": "Hello"}]
    reply, tokens, used_model = llm_complete(
        messages=messages,
        model="gemini/gemini-3.5-flash-lite",
        persona_name="ceo",
    )

    assert reply == "Fallback response"
    assert tokens == 42
    assert "gemini" not in used_model or used_model == _fallback_for("reasoning")
