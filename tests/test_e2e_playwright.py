"""
E2E Playwright tests for IntelAI — core scoped flow
(login → dashboard → chat → analytics → forecasting → risk).

Requires a live stack (frontend :5173 + API :8000) and a Playwright browser.
Skips automatically when Playwright isn't installed or the stack isn't running,
so the default in-process suite (test_api.py / test_smoke.py) stays green in CI.
Run on the Studio with the stack up:  pytest tests/test_e2e_playwright.py
"""
import os
import re
from pathlib import Path

import pytest
import httpx
from dotenv import load_dotenv

pytest.importorskip("playwright", reason="Playwright not installed — e2e skipped")
from playwright.sync_api import sync_playwright, expect  # noqa: E402

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

BASE_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
API_BASE = os.getenv("FASTAPI_HOST", "http://localhost:8000")
ADMIN_USER = os.getenv("BOOTSTRAP_ADMIN_USERNAME", "admin")
ADMIN_PASS = os.getenv("BOOTSTRAP_ADMIN_PASSWORD", "admin123")


def _stack_running() -> bool:
    try:
        return httpx.get(f"{API_BASE}/health", timeout=2).status_code == 200
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _stack_running(), reason="live stack not running on :8000")


@pytest.fixture(scope="module")
def page():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        pg = browser.new_page()
        yield pg
        browser.close()


def _login(page):
    page.goto(BASE_URL, wait_until="networkidle")
    page.fill("input[type='text'], input[name='username']", ADMIN_USER)
    page.fill("input[type='password']", ADMIN_PASS)
    page.click("button[type='submit']")
    page.wait_for_url(re.compile(r"/dashboard"), timeout=15000)


def test_login_and_dashboard(page):
    _login(page)
    expect(page).to_have_url(re.compile(r"/dashboard"))


@pytest.mark.parametrize("path", ["/chat", "/analytics", "/forecasting", "/risk", "/knowledge"])
def test_core_pages_load(page, path):
    _login(page)
    page.goto(f"{BASE_URL}{path}", wait_until="networkidle")
    expect(page.locator("body")).to_be_visible()


def test_cut_pages_redirect(page):
    """Pages removed during the IntelAI scope-down should not resolve."""
    _login(page)
    page.goto(f"{BASE_URL}/scanner", wait_until="networkidle")
    # App routes unknown paths back to the dashboard.
    expect(page).to_have_url(re.compile(r"/dashboard"))
