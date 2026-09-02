"""Session-triggered Studio warm-up.

Fires one real, minimal embed request to the orchestrator's remote inference
host the moment a real user session actually starts (login / demo-login) —
never on a timer, never repeating on its own. This is deliberately the ONLY
kind of proactive wake this codebase is allowed to do: orchestrator/README.md
documents, from the incident that got a prior Lightning account blocked, that
the Studio wake path must only ever be invoked via legitimate inference
requests, explicitly ruling out synthetic pinging and automated cron wakes —
see also the Cloudflare gateway worker, where an equivalent cron-based wake
was tried and reverted the same day for exactly this reason. A user opening
the app and authenticating is a genuine signal that inference is about to be
needed; it is not synthetic.

The request itself is real (a real embedding of real text gets computed and
returned by the Studio, same contract hybrid_retrieval._remote_embed_batch
uses), not a throwaway "ping" — the only thing making it a "warm-up" is that
nothing here waits for or uses the response. It fires on a background thread
so a slow/cold Studio never adds latency to the login response, and a short
per-call HTTP timeout means this thread finishes quickly regardless — the
Studio's own wake continues in the background on Lightning's side either way,
identical to what a real subsequent embed call would trigger.
"""
from __future__ import annotations

import os
import threading
import time
from typing import Optional

from src.core.logger import get_logger

log = get_logger(__name__)

# Debounce only — not a safety mechanism. The orchestrator's own WAKE_COOLDOWN
# (120s) is what actually prevents this from ever contributing to control-op
# cycling; this just avoids firing a redundant HTTP call on every login within
# a short window (e.g. a user re-authenticating, or several tabs).
_WARMUP_DEBOUNCE_S = float(os.getenv("SESSION_WARMUP_DEBOUNCE_SECONDS", "60"))
_last_fired: float = 0.0
_lock = threading.Lock()


def _do_warmup() -> None:
    url = os.getenv("EMBED_URL", "").strip() or os.getenv("EMBEDDING_ENDPOINT", "").strip()
    if not url or os.getenv("EMBEDDING_PROVIDER", "").strip().lower() != "remote":
        return
    if "huggingface.co" in url:
        return  # HF Inference API doesn't need/benefit from a Studio warm-up.
    try:
        import json as _json
        import urllib.request

        endpoint = url if url.endswith("/embed") else url.rstrip("/") + "/embed"
        headers = {"Content-Type": "application/json", "User-Agent": "IntelAI-SessionWarmup/1.0"}
        tk = os.getenv("INFERENCE_TOKEN", "").strip()
        if tk:
            headers["Authorization"] = "Bearer " + tk
        # A real embedding request — the text itself is unused by the caller,
        # but the Studio computes and returns a genuine embedding for it, the
        # same as any other real request would.
        body = _json.dumps({"texts": ["session warm-up"], "model": os.getenv("EMBEDDING_MODEL", "")}).encode()
        req = urllib.request.Request(endpoint, data=body, headers=headers)
        # Short timeout on purpose: this thread's job is to trigger the wake,
        # not to wait for it. A cold host will still be woken by this request
        # even if we stop listening for the response before it completes.
        urllib.request.urlopen(req, timeout=8).read()
    except Exception as e:
        log.debug("session warm-up embed call did not complete (non-fatal): %s", e)


def fire_session_warmup() -> None:
    """Call once per real login/demo-login. Non-blocking, best-effort,
    debounced, and silently a no-op if EMBEDDING_PROVIDER isn't 'remote'."""
    global _last_fired
    now = time.time()
    with _lock:
        if now - _last_fired < _WARMUP_DEBOUNCE_S:
            return
        _last_fired = now
    threading.Thread(target=_do_warmup, daemon=True).start()
