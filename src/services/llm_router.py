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


DEFAULT_MODEL = os.getenv("LLM_DEFAULT", "groq/llama-3.3-70b-versatile")
REASONING_MODEL = os.getenv("LLM_REASONING", "anthropic/claude-sonnet-4-6")
JUDGE_MODEL = os.getenv("LLM_JUDGE", "anthropic/claude-haiku-4-5")
LOCAL_MODEL = os.getenv("LLM_LOCAL", "ollama/llama3.3")


PERSONA_TIER_MAP: Dict[str, str] = {
    "ceo": "reasoning",
    "cfo": "reasoning",
    "cto": "reasoning",
    "risk": "reasoning",
    "coo": "default",
    "chro": "default",
    "esg": "default",
    "analyst": "default",
    "general": "default",
}


def _resolve(tier: str) -> str:
    return {
        "default": DEFAULT_MODEL,
        "reasoning": REASONING_MODEL,
        "judge": JUDGE_MODEL,
        "local": LOCAL_MODEL,
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
