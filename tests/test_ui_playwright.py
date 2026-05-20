import httpx

"""
Fallback UI smoke test (HTTP-only) for environments where Playwright
browser binaries are not available. It loads the frontend index and
verifies basic HTML content is present.
"""

BASE = "http://127.0.0.1:5173"


def test_homepage_basic_http():
    r = httpx.get(BASE, timeout=10)
    assert r.status_code == 200
    text = r.text
    # expect an HTML document
    assert "<html" in text.lower()
    assert "</body>" in text.lower()
