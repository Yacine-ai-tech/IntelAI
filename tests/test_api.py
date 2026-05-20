import httpx
import os
from pathlib import Path
from dotenv import load_dotenv

BASE = "http://127.0.0.1:8000"

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def _test_login_credentials():
    return {
        "username": os.getenv("BOOTSTRAP_ADMIN_USERNAME", "admin"),
        "password": os.getenv("BOOTSTRAP_ADMIN_PASSWORD", "admin123"),
    }


def test_health():
    r = httpx.get(f"{BASE}/health", timeout=5)
    assert r.status_code == 200


def test_login():
    r = httpx.post(
        f"{BASE}/api/v1/auth/login",
        json=_test_login_credentials(),
        timeout=5,
    )
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
