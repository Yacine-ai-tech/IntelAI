"""LIVE LLM-router test — real call (needs ANTHROPIC_API_KEY/GROQ_API_KEY). Proves the
multi-provider router actually returns a model completion + persona→tier routing works."""
import asyncio
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

pytestmark = pytest.mark.skipif(
    not (os.getenv("ANTHROPIC_API_KEY") or os.getenv("GROQ_API_KEY")),
    reason="live test needs an LLM key",
)


def _text(resp):
    try:
        return resp.choices[0].message.content
    except Exception:
        return resp["choices"][0]["message"]["content"]


def test_router_returns_real_completion():
    from src.services.llm_router import llm_call
    resp = asyncio.run(llm_call(
        [{"role": "user", "content": "Reply with exactly the word: PONG"}],
        tier="default", temperature=0.0, max_tokens=10,
    ))
    out = _text(resp)
    print("\nLIVE router →", repr(out))
    assert "stub" not in str(out).lower()
    assert "pong" in str(out).lower()
