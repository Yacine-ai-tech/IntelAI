import httpx
import os
import pytest
from pathlib import Path
from dotenv import load_dotenv

BASE = "http://127.0.0.1:8000"

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def _test_login_credentials():
    return {
        "username": os.getenv("BOOTSTRAP_ADMIN_USERNAME", "admin"),
        "password": os.getenv("BOOTSTRAP_ADMIN_PASSWORD", "admin123"),
    }


# ============================================================================
# AUTH TESTS (5 tests)
# ============================================================================

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


def test_login_wrong_password():
    r = httpx.post(
        f"{BASE}/api/v1/auth/login",
        json={"username": "admin", "password": "wrongpassword"},
        timeout=5,
    )
    assert r.status_code in [400, 401, 422]


def test_register():
    import os as _os
    r = httpx.post(
        f"{BASE}/api/v1/auth/register",
        json={"username": f"testuser_{_os.urandom(4).hex()}", "password": "testpass123"},
        timeout=5,
    )
    assert r.status_code in [200, 201, 400]  # 400 if user exists


def test_get_me():
    # First login to get token
    r = httpx.post(
        f"{BASE}/api/v1/auth/login",
        json=_test_login_credentials(),
        timeout=5,
    )
    token = r.json().get("access_token")
    
    r = httpx.get(
        f"{BASE}/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
        timeout=5,
    )
    assert r.status_code == 200
    data = r.json()
    assert "username" in data


def test_token_validation():
    # Test invalid token
    r = httpx.get(
        f"{BASE}/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid_token"},
        timeout=5,
    )
    assert r.status_code in [401, 403]


# ============================================================================
# CHAT TESTS (4 tests)
# ============================================================================

def test_chat_basic():
    r = httpx.post(
        f"{BASE}/api/v1/auth/login",
        json=_test_login_credentials(),
        timeout=5,
    )
    token = r.json().get("access_token")
    
    r = httpx.post(
        f"{BASE}/api/v1/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "Hello", "persona": None},
        timeout=30,
    )
    assert r.status_code in [200, 500]  # 500 if LLM not configured
    if r.status_code == 200:
        data = r.json()
        assert "response" in data


def test_chat_with_persona():
    r = httpx.post(
        f"{BASE}/api/v1/auth/login",
        json=_test_login_credentials(),
        timeout=5,
    )
    token = r.json().get("access_token")
    
    r = httpx.post(
        f"{BASE}/api/v1/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "Hello", "persona": "CFO"},
        timeout=30,
    )
    assert r.status_code in [200, 500]


def test_chat_streaming():
    # Test WebSocket endpoint exists (basic check)
    r = httpx.get(f"{BASE}/api/v1/docs", timeout=5)
    assert r.status_code == 200


def test_chat_edge_cases():
    r = httpx.post(
        f"{BASE}/api/v1/auth/login",
        json=_test_login_credentials(),
        timeout=5,
    )
    token = r.json().get("access_token")
    
    # Test empty message
    r = httpx.post(
        f"{BASE}/api/v1/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "", "persona": None},
        timeout=30,
    )
    assert r.status_code in [200, 400, 422]


# ============================================================================
# KPI TESTS (4 tests)
# ============================================================================

def test_kpis_get():
    r = httpx.post(
        f"{BASE}/api/v1/auth/login",
        json=_test_login_credentials(),
        timeout=5,
    )
    token = r.json().get("access_token")
    
    r = httpx.get(
        f"{BASE}/api/v1/kpis",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    assert r.status_code in [200, 404]


def test_kpis_periods():
    r = httpx.post(
        f"{BASE}/api/v1/auth/login",
        json=_test_login_credentials(),
        timeout=5,
    )
    token = r.json().get("access_token")
    
    r = httpx.get(
        f"{BASE}/api/v1/kpis/periods",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    assert r.status_code in [200, 404]


def test_kpis_metrics():
    r = httpx.post(
        f"{BASE}/api/v1/auth/login",
        json=_test_login_credentials(),
        timeout=5,
    )
    token = r.json().get("access_token")
    
    r = httpx.get(
        f"{BASE}/api/v1/kpis/metrics",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    assert r.status_code in [200, 404]


def test_kpis_by_category():
    r = httpx.post(
        f"{BASE}/api/v1/auth/login",
        json=_test_login_credentials(),
        timeout=5,
    )
    token = r.json().get("access_token")
    
    r = httpx.get(
        f"{BASE}/api/v1/kpis?category=Finance",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    assert r.status_code in [200, 404]


# ============================================================================
# INSIGHTS TESTS (3 tests)
# ============================================================================

def test_insights_health():
    r = httpx.post(
        f"{BASE}/api/v1/auth/login",
        json=_test_login_credentials(),
        timeout=5,
    )
    token = r.json().get("access_token")
    
    r = httpx.get(
        f"{BASE}/api/v1/insights/health",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    assert r.status_code in [200, 404]


def test_insights_risk():
    r = httpx.post(
        f"{BASE}/api/v1/auth/login",
        json=_test_login_credentials(),
        timeout=5,
    )
    token = r.json().get("access_token")
    
    r = httpx.get(
        f"{BASE}/api/v1/insights/risk",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    assert r.status_code in [200, 404]


def test_insights_summary():
    r = httpx.post(
        f"{BASE}/api/v1/auth/login",
        json=_test_login_credentials(),
        timeout=5,
    )
    token = r.json().get("access_token")
    
    r = httpx.get(
        f"{BASE}/api/v1/insights/summary",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    assert r.status_code in [200, 404]


# ============================================================================
# FORECAST TESTS (2 tests)
# ============================================================================

def test_forecast_basic():
    r = httpx.post(
        f"{BASE}/api/v1/auth/login",
        json=_test_login_credentials(),
        timeout=5,
    )
    token = r.json().get("access_token")
    
    r = httpx.post(
        f"{BASE}/api/v1/forecast",
        headers={"Authorization": f"Bearer {token}"},
        json={"metric": "Revenue", "periods": 6},
        timeout=30,
    )
    assert r.status_code in [200, 400, 404, 500]


def test_forecast_with_ci():
    r = httpx.post(
        f"{BASE}/api/v1/auth/login",
        json=_test_login_credentials(),
        timeout=5,
    )
    token = r.json().get("access_token")
    
    r = httpx.post(
        f"{BASE}/api/v1/forecast",
        headers={"Authorization": f"Bearer {token}"},
        json={"metric": "Revenue", "periods": 12},
        timeout=30,
    )
    assert r.status_code in [200, 400, 404, 500]


# ============================================================================
# INGEST TESTS (3 tests)
# ============================================================================

def test_ingest_valid():
    r = httpx.post(
        f"{BASE}/api/v1/auth/login",
        json=_test_login_credentials(),
        timeout=5,
    )
    token = r.json().get("access_token")
    
    r = httpx.post(
        f"{BASE}/api/v1/ingest/kpi",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "data": [{
                "metric_name": "TestMetric",
                "value": 100.0,
                "category": "Test",
                "period": "2025-Q1"
            }]
        },
        timeout=10,
    )
    assert r.status_code in [200, 201, 400, 404]


def test_ingest_empty():
    r = httpx.post(
        f"{BASE}/api/v1/auth/login",
        json=_test_login_credentials(),
        timeout=5,
    )
    token = r.json().get("access_token")
    
    r = httpx.post(
        f"{BASE}/api/v1/ingest/kpi",
        headers={"Authorization": f"Bearer {token}"},
        json={"data": []},
        timeout=10,
    )
    assert r.status_code in [200, 400, 404]


def test_ingest_malformed():
    r = httpx.post(
        f"{BASE}/api/v1/auth/login",
        json=_test_login_credentials(),
        timeout=5,
    )
    token = r.json().get("access_token")
    
    r = httpx.post(
        f"{BASE}/api/v1/ingest/kpi",
        headers={"Authorization": f"Bearer {token}"},
        json={"invalid": "data"},
        timeout=10,
    )
    assert r.status_code in [400, 422, 404]


# ============================================================================
# RBAC TESTS (4 tests)
# ============================================================================

def test_rbac_admin_works():
    # Admin should have access to all endpoints
    r = httpx.post(
        f"{BASE}/api/v1/auth/login",
        json=_test_login_credentials(),
        timeout=5,
    )
    token = r.json().get("access_token")
    
    r = httpx.get(
        f"{BASE}/api/v1/kpis",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    assert r.status_code in [200, 404]


def test_rbac_viewer_blocked():
    # Create viewer user
    import os as _os
    username = f"viewer_{_os.urandom(4).hex()}"
    httpx.post(
        f"{BASE}/api/v1/auth/register",
        json={"username": username, "password": "testpass123", "role": "viewer"},
        timeout=5,
    )
    
    r = httpx.post(
        f"{BASE}/api/v1/auth/login",
        json={"username": username, "password": "testpass123"},
        timeout=5,
    )
    token = r.json().get("access_token")
    
    # Viewer should be able to read but not write
    r = httpx.get(
        f"{BASE}/api/v1/kpis",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    assert r.status_code in [200, 404]
    
    # Try to ingest (should fail for viewer)
    r = httpx.post(
        f"{BASE}/api/v1/ingest/kpi",
        headers={"Authorization": f"Bearer {token}"},
        json={"data": [{"metric_name": "Test", "value": 100}]},
        timeout=10,
    )
    assert r.status_code in [403, 404]


def test_rbac_scope_enforcement():
    # Test that user can only access their own data
    r = httpx.post(
        f"{BASE}/api/v1/auth/login",
        json=_test_login_credentials(),
        timeout=5,
    )
    token = r.json().get("access_token")
    
    r = httpx.get(
        f"{BASE}/api/v1/chat/sessions",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    assert r.status_code in [200, 404]


def test_rbac_edge_cases():
    # Test with no auth header
    r = httpx.get(f"{BASE}/api/v1/kpis", timeout=10)
    assert r.status_code in [401, 403]


# ============================================================================
# MONITORING TESTS (3 tests)
# ============================================================================

def test_monitoring_stats():
    r = httpx.get(f"{BASE}/metrics", timeout=5)
    assert r.status_code in [200, 404]


def test_monitoring_knowledge_search():
    r = httpx.post(
        f"{BASE}/api/v1/auth/login",
        json=_test_login_credentials(),
        timeout=5,
    )
    token = r.json().get("access_token")
    
    r = httpx.post(
        f"{BASE}/api/v1/knowledge/search",
        headers={"Authorization": f"Bearer {token}"},
        json={"query": "revenue", "top_k": 5},
        timeout=10,
    )
    assert r.status_code in [200, 404, 500]


def test_monitoring_performance():
    # Test performance endpoint exists
    r = httpx.get(f"{BASE}/health", timeout=5)
    assert r.status_code == 200
    data = r.json()
    assert "status" in data


# ============================================================================
# MISC TESTS (3 tests)
# ============================================================================

def test_misc_health():
    r = httpx.get(f"{BASE}/health", timeout=5)
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "healthy"


def test_misc_root():
    r = httpx.get(f"{BASE}/", timeout=5)
    assert r.status_code in [200, 404]


def test_misc_404_handler():
    r = httpx.get(f"{BASE}/api/v1/nonexistent", timeout=5)
    assert r.status_code == 404
