"""
Fallback UI smoke test (HTTP-only) for environments where Playwright browser
binaries are not available. It loads the frontend index and verifies basic HTML.

Skips automatically when the Vite dev server isn't running, so CI / in-process
runs stay green (the live frontend only exists on the laptop during dev).
"""
import httpx
import pytest

BASE = "http://127.0.0.1:5173"


def test_homepage_basic_http():
    try:
        r = httpx.get(BASE, timeout=5)
    except Exception:
        pytest.skip("frontend dev server not running on :5173")
    assert r.status_code == 200
    text = r.text.lower()
    assert "<html" in text and "</body>" in text
