"""
LLM Router — Multi-provider LLM routing via LiteLLM.

Routes calls across Groq / Anthropic / OpenAI / Ollama based on a `tier`
argument. Used by omnismart_chatbot and any service needing LLM calls.

Tiers:
  - default:    LLM_DEFAULT     (Groq Llama 3.3 70B by default — fast + cheap)
  - reasoning:  LLM_REASONING   (Claude Sonnet 4.6 — deep analysis)
  - judge:      LLM_JUDGE       (Claude Haiku 4.5 — eval/grading)
  - local:      LLM_LOCAL       (Ollama Llama 3.3 — offline fallback)
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from src.core.logger import get_logger

log = get_logger(__name__)

try:
    from litellm import acompletion, completion
    _LITELLM = True
except ImportError:
    _LITELLM = False
    log.warning("litellm not installed — llm_router stub mode")


DEFAULT_MODEL    = os.getenv("LLM_DEFAULT",    "groq/llama-3.3-70b-versatile")
FAST_MODEL       = os.getenv("LLM_FAST",       "groq/llama-3.1-8b-instant")
REASONING_MODEL  = os.getenv("LLM_REASONING",  "anthropic/claude-sonnet-4-6")
JUDGE_MODEL      = os.getenv("LLM_JUDGE",      "anthropic/claude-haiku-4-5")
LOCAL_MODEL      = os.getenv("LLM_LOCAL",      "ollama/llama3.3")

# ── Persona → tier mapping ─────────────────────────────────────────────────
# ALL personas start at "default" (Groq 70B, ~2s round-trip).
# "reasoning" (Claude Sonnet, ~12-18s) is reserved for genuinely complex
# multi-step analysis detected by smart_tier() at query time.
# This is the #1 fix for IntelAI latency: CFO/CEO were previously routing
# ALL queries — including simple "what is gross margin?" — to Claude Sonnet.
PERSONA_TIER_MAP: Dict[str, str] = {
    "ceo":      "default",   # was: reasoning → 18s; now: default → 2s
    "cfo":      "default",   # was: reasoning → 18s; now: default → 2s
    "cto":      "default",   # was: reasoning → 18s; now: default → 2s
    "risk":     "default",   # was: reasoning → 18s; now: default → 2s
    "coo":      "default",
    "chro":     "default",
    "esg":      "default",
    "analyst":  "default",
    "general":  "default",
}

# Patterns that genuinely need Claude Sonnet deep reasoning
_COMPLEX_PATTERNS = [
    "compare", "contrast", "explain why", "root cause", "scenario analysis",
    "monte carlo", "sensitivity", "what would happen if", "strategic",
    "recommend", "board report", "full analysis", "deep dive",
    "forecast next", "multi-step", "simulate", "model the",
]


def smart_tier(message: str, persona: Optional[str] = None) -> str:
    """Auto-detect whether a query warrants Claude Sonnet (reasoning) or Groq (default).

    Simple KPI lookups, dashboard queries, and conversational questions → default (Groq 70B, ~2s).
    Complex analysis, scenario modeling, board reports → reasoning (Claude Sonnet, ~12s).

    This is the key latency fix: previously ALL CFO/CEO queries went to Claude Sonnet.
    """
    msg_lower = message.lower()
    word_count = len(msg_lower.split())

    # Very short queries are always fast-path
    if word_count <= 8:
        return "default"

    # Complex pattern detection → escalate to reasoning
    if any(pat in msg_lower for pat in _COMPLEX_PATTERNS):
        return "reasoning"

    # Long, multi-clause questions → reasoning
    if word_count > 60:
        return "reasoning"

    return "default"


def _resolve(tier: str) -> str:
    return {
        "fast":      FAST_MODEL,
        "default":   DEFAULT_MODEL,
        "reasoning": REASONING_MODEL,
        "judge":     JUDGE_MODEL,
        "local":     LOCAL_MODEL,
    }.get(tier, DEFAULT_MODEL)


def _apply_cache_control(messages: List[Dict[str, Any]], model: str) -> List[Dict[str, Any]]:
    """Mark the stable system prefix with Anthropic prompt-cache breakpoints so repeated
    system prompts / large context are billed at the cached rate (~0.1x reads). No-op for
    non-Claude providers — Groq caches matching prefixes automatically with no markup needed.
    litellm translates the block-with-cache_control shape to the Anthropic Messages API.
    """
    if "claude" not in model.lower() and not model.lower().startswith("anthropic/"):
        return messages
    out: List[Dict[str, Any]] = []
    breakpoints = 0
    for m in messages:
        content = m.get("content")
        if m.get("role") == "system" and isinstance(content, str) and breakpoints < 4:
            out.append({"role": "system", "content": [
                {"type": "text", "text": content, "cache_control": {"type": "ephemeral"}},
            ]})
            breakpoints += 1
        else:
            out.append(m)
    return out


async def llm_call(
    messages: List[Dict[str, str]],
    tier: str = "default",
    persona: Optional[str] = None,
    temperature: float = 0.3,
    max_tokens: Optional[int] = None,
    **kwargs: Any,
) -> Any:
    """
    Route an LLM call to the appropriate tier.

    Args:
        messages: List of {"role": "system|user|assistant", "content": "..."}.
        tier: One of default | reasoning | judge | local. Overridden by persona if provided.
        persona: When set, looks up the persona's preferred tier in PERSONA_TIER_MAP.
        temperature: Sampling temperature.
        max_tokens: Max output tokens (optional).
        **kwargs: Forwarded to litellm.acompletion.

    Returns:
        The litellm response (or a stub dict if litellm is unavailable).
    """
    if persona and persona.lower() in PERSONA_TIER_MAP:
        tier = PERSONA_TIER_MAP[persona.lower()]

    model = _resolve(tier)

    if not _LITELLM:
        return {"choices": [{"message": {"content": "stub: litellm not installed"}}], "model": model}

    messages = _apply_cache_control(messages, model)
    params: Dict[str, Any] = {"model": model, "messages": messages, "temperature": temperature, **kwargs}
    if max_tokens:
        params["max_tokens"] = max_tokens
    return await acompletion(**params)


def llm_call_sync(
    messages: List[Dict[str, str]],
    tier: str = "default",
    persona: Optional[str] = None,
    temperature: float = 0.3,
    max_tokens: Optional[int] = None,
    **kwargs: Any,
) -> Any:
    """Synchronous variant of llm_call (for non-async contexts)."""
    if persona and persona.lower() in PERSONA_TIER_MAP:
        tier = PERSONA_TIER_MAP[persona.lower()]

    model = _resolve(tier)

    if not _LITELLM:
        return {"choices": [{"message": {"content": "stub: litellm not installed"}}], "model": model}

    messages = _apply_cache_control(messages, model)
    params: Dict[str, Any] = {"model": model, "messages": messages, "temperature": temperature, **kwargs}
    if max_tokens:
        params["max_tokens"] = max_tokens
    return completion(**params)
