"""
Comprehensive E2E Playwright Tests for OmniIntelOS
Tests all frontend pages, backend API endpoints, and integrations
"""
import pytest
from playwright.sync_api import Page, expect
import httpx
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

BASE_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
API_BASE = os.getenv("FASTAPI_HOST", "http://localhost:8000")


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        viewport: {"width": 1920, "height": 1080},
    }


@pytest.fixture(scope="function")
def page(page: Page):
    page.goto(BASE_URL)
    return page


class TestAuth:
    """Test authentication flows"""
    
    def test_login_page_loads(self, page: Page):
        page.goto(f"{BASE_URL}/login")
        expect(page).to_have_title(/OmniIntelOS/)
        expect(page.locator("input[type='text']")).to_be_visible()
        expect(page.locator("input[type='password']")).to_be_visible()
    
    def test_login_with_valid_credentials(self, page: Page):
        page.goto(f"{BASE_URL}/login")
        page.fill("input[type='text']", "admin")
        page.fill("input[type='password']", "admin123")
        page.click("button[type='submit']")
        # Should redirect to dashboard
        expect(page).to_have_url(f"{BASE_URL}/dashboard")
    
    def test_login_with_invalid_credentials(self, page: Page):
        page.goto(f"{BASE_URL}/login")
        page.fill("input[type='text']", "admin")
        page.fill("input[type='password']", "wrongpassword")
        page.click("button[type='submit']")
        # Should show error and stay on login page
        expect(page).to_have_url(f"{BASE_URL}/login")


class TestDashboard:
    """Test dashboard functionality"""
    
    def test_dashboard_loads(self, page: Page):
        self._login(page)
        expect(page.locator("h1")).to_contain_text("Dashboard")
        expect(page.locator(".kpi-card")).to_have_count(4)
    
    def test_kpi_cards_display(self, page: Page):
        self._login(page)
        cards = page.locator(".kpi-card")
        expect(cards).to_have_count(4)
        for card in cards:
            expect(card.locator(".kpi-value")).to_be_visible()
            expect(card.locator(".kpi-label")).to_be_visible()
    
    def test_health_gauge_displays(self, page: Page):
        self._login(page)
        expect(page.locator(".health-gauge")).to_be_visible()
        expect(page.locator(".health-gauge-value")).to_be_visible()
    
    def test_executive_summary_displays(self, page: Page):
        self._login(page)
        expect(page.locator("text=Executive Summary")).to_be_visible()
    
    def _login(self, page: Page):
        page.goto(f"{BASE_URL}/login")
        page.fill("input[type='text']", "admin")
        page.fill("input[type='password']", "admin123")
        page.click("button[type='submit']")
        page.wait_for_url(f"{BASE_URL}/dashboard")


class TestChat:
    """Test chat functionality"""
    
    def test_chat_page_loads(self, page: Page):
        self._login(page)
        page.goto(f"{BASE_URL}/chat")
        expect(page.locator("text=AI Intelligence Assistant")).to_be_visible()
        expect(page.locator("textarea")).to_be_visible()
    
    def test_send_message(self, page: Page):
        self._login(page)
        page.goto(f"{BASE_URL}/chat")
        page.fill("textarea", "What is the current revenue?")
        page.click("button[aria-label='Send']")
        # Should show message in chat
        expect(page.locator(".chat-message.user")).to_be_visible()
    
    def test_persona_selection(self, page: Page):
        self._login(page)
        page.goto(f"{BASE_URL}/chat")
        expect(page.locator("select")).to_be_visible()
        page.select_option("select", "financial-analyst")
        expect(page.locator("select")).to_have_value("financial-analyst")
    
    def test_chat_history_displays(self, page: Page):
        self._login(page)
        page.goto(f"{BASE_URL}/chat")
        expect(page.locator("text=Conversation History")).to_be_visible()
    
    def _login(self, page: Page):
        page.goto(f"{BASE_URL}/login")
        page.fill("input[type='text']", "admin")
        page.fill("input[type='password']", "admin123")
        page.click("button[type='submit']")
        page.wait_for_url(f"{BASE_URL}/dashboard")


class TestAnalytics:
    """Test analytics functionality"""
    
    def test_analytics_page_loads(self, page: Page):
        self._login(page)
        page.goto(f"{BASE_URL}/analytics")
        expect(page.locator("text=Analytics")).to_be_visible()
        expect(page.locator(".kpi-card")).to_be_visible()
    
    def test_chart_displays(self, page: Page):
        self._login(page)
        page.goto(f"{BASE_URL}/analytics")
        expect(page.locator(".recharts-wrapper")).to_be_visible()
    
    def test_forecast_interface(self, page: Page):
        self._login(page)
        page.goto(f"{BASE_URL}/analytics")
        expect(page.locator("text=Forecasting")).to_be_visible()
        expect(page.locator("select")).to_be_visible()
    
    def test_metrics_table_loads(self, page: Page):
        self._login(page)
        page.goto(f"{BASE_URL}/analytics")
        expect(page.locator(".table")).to_be_visible()
    
    def _login(self, page: Page):
        page.goto(f"{BASE_URL}/login")
        page.fill("input[type='text']", "admin")
        page.fill("input[type='password']", "admin123")
        page.click("button[type='submit']")
        page.wait_for_url(f"{BASE_URL}/dashboard")


class TestDomainPages:
    """Test domain-specific pages"""
    
    @pytest.mark.parametrize("page_path,expected_title", [
        ("/hr", "Human Resources"),
        ("/logistics", "Logistics"),
        ("/it", "IT Operations"),
        ("/operations", "Operations"),
        ("/esg", "ESG Dashboard"),
        ("/risk", "Risk Radar"),
        ("/financial", "Financial"),
    ])
    def test_domain_pages_load(self, page: Page, page_path: str, expected_title: str):
        self._login(page)
        page.goto(f"{BASE_URL}{page_path}")
        expect(page.locator("h1")).to_contain_text(expected_title)
    
    def _login(self, page: Page):
        page.goto(f"{BASE_URL}/login")
        page.fill("input[type='text']", "admin")
        page.fill("input[type='password']", "admin123")
        page.click("button[type='submit']")
        page.wait_for_url(f"{BASE_URL}/dashboard")


class TestNewPages:
    """Test newly created pages"""
    
    def test_voice_page_loads(self, page: Page):
        self._login(page)
        page.goto(f"{BASE_URL}/voice")
        expect(page.locator("text=Voice Intelligence")).to_be_visible()
        expect(page.locator("button:has-text('Start Recording')")).to_be_visible()
    
    def test_knowledge_page_loads(self, page: Page):
        self._login(page)
        page.goto(f"{BASE_URL}/knowledge")
        expect(page.locator("text=Knowledge Base")).to_be_visible()
        expect(page.locator("input[placeholder*='Search']")).to_be_visible()
    
    def test_workflow_page_loads(self, page: Page):
        self._login(page)
        page.goto(f"{BASE_URL}/workflows")
        expect(page.locator("text=Workflow Automation")).to_be_visible()
        expect(page.locator("text=Active Workflows")).to_be_visible()
    
    def _login(self, page: Page):
        page.goto(f"{BASE_URL}/login")
        page.fill("input[type='text']", "admin")
        page.fill("input[type='password']", "admin123")
        page.click("button[type='submit']")
        page.wait_for_url(f"{BASE_URL}/dashboard")


class TestBackendAPI:
    """Test backend API endpoints"""
    
    def test_health_endpoint(self):
        r = httpx.get(f"{API_BASE}/health", timeout=5)
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "healthy"
    
    def test_login_endpoint(self):
        r = httpx.post(
            f"{API_BASE}/api/v1/auth/login",
            json={"username": "admin", "password": "admin123"},
            timeout=5
        )
        assert r.status_code == 200
        data = r.json()
        assert "access_token" in data
    
    def test_kpis_endpoint(self):
        r = httpx.get(f"{API_BASE}/api/v1/kpis", timeout=5)
        assert r.status_code == 200
        data = r.json()
        assert "metrics" in data or len(data) > 0
    
    def test_insights_health_endpoint(self):
        r = httpx.get(f"{API_BASE}/api/v1/insights/health", timeout=5)
        assert r.status_code == 200
        data = r.json()
        assert "health_index" in data or "score" in data
    
    def test_personas_endpoint(self):
        r = httpx.get(f"{API_BASE}/api/v1/personas", timeout=5)
        assert r.status_code in [200, 404]  # 404 acceptable if no personas configured
    
    def test_hr_summary_endpoint(self):
        r = httpx.get(f"{API_BASE}/api/v1/hr/summary", timeout=5)
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, dict)
    
    def test_knowledge_stats_endpoint(self):
        r = httpx.get(f"{API_BASE}/api/v1/knowledge/stats", timeout=5)
        assert r.status_code in [200, 404]
    
    def test_n8n_nodes_endpoint(self):
        r = httpx.get(f"{API_BASE}/api/v1/n8n/nodes", timeout=5)
        assert r.status_code in [200, 404]
    
    def test_integrations_status_endpoint(self):
        r = httpx.get(f"{API_BASE}/api/v1/integrations/status", timeout=5)
        assert r.status_code == 200
        data = r.json()
        assert "statuses" in data


class TestIntegrations:
    """Test third-party integrations"""
    
    def test_n8n_connection(self):
        """Test n8n workflow automation connection"""
        n8n_url = os.getenv("N8N_BASE_URL", "http://localhost:5678")
        n8n_api_key = os.getenv("N8N_API_KEY", "")
        
        if not n8n_api_key:
            pytest.skip("N8N_API_KEY not set")
        
        try:
            r = httpx.get(f"{n8n_url}/rest/workflows", 
                        headers={"Authorization": f"Bearer {n8n_api_key}"},
                        timeout=10)
            assert r.status_code == 200
        except httpx.ConnectError:
            pytest.skip("N8N server not reachable")
    
    def test_clickup_integration(self):
        """Test ClickUp integration configuration"""
        clickup_api_key = os.getenv("CLICKUP_API_KEY", "")
        
        if not clickup_api_key:
            pytest.skip("CLICKUP_API_KEY not set")
        
        # Test basic API connectivity
        try:
            r = httpx.get("https://api.clickup.com/api/v2/team",
                        headers={"Authorization": clickup_api_key},
                        timeout=10)
            assert r.status_code == 200
        except httpx.ConnectError:
            pytest.skip("ClickUp API not reachable")
    
    def test_google_integration(self):
        """Test Google services integration"""
        google_credentials = os.getenv("GOOGLE_CREDENTIALS_PATH", "")
        google_api_key = os.getenv("GOOGLE_API_KEY", "")
        
        if not google_credentials and not google_api_key:
            pytest.skip("Google credentials not set")
        
        # Test Google Sheets API if configured
        if google_api_key:
            try:
                r = httpx.get(f"https://www.googleapis.com/auth/spreadsheets",
                            timeout=10)
                # This will likely fail auth but proves connectivity
                assert r.status_code in [401, 403]  # Expected without full auth
            except httpx.ConnectError:
                pytest.skip("Google API not reachable")


class TestEnvironmentConfiguration:
    """Test that all required environment variables are set"""
    
    def test_database_connection(self):
        """Test database connectivity"""
        postgres_url = os.getenv("POSTGRES_URL", "")
        assert postgres_url != "", "POSTGRES_URL must be set"
        assert "postgresql://" in postgres_url, "POSTGRES_URL must be a valid PostgreSQL connection string"
    
    def test_llm_configuration(self):
        """Test LLM provider configuration"""
        groq_key = os.getenv("GROQ_API_KEY", "")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
        
        assert groq_key != "", "GROQ_API_KEY must be set"
        assert anthropic_key != "", "ANTHROPIC_API_KEY must be set"
    
    def test_secret_key(self):
        """Test secret key is properly configured"""
        secret_key = os.getenv("SECRET_KEY", "")
        assert secret_key != "", "SECRET_KEY must be set"
        assert secret_key != "change-this-to-a-secure-random-string-in-production", "SECRET_KEY must be changed from default"
    
    def test_tavily_configuration(self):
        """Test Tavily search API configuration"""
        tavily_key = os.getenv("TAVILY_API_KEY", "")
        assert tavily_key != "", "TAVILY_API_KEY must be set"
    
    def test_frontend_url(self):
        """Test frontend URL configuration"""
        frontend_url = os.getenv("FRONTEND_URL", "")
        assert frontend_url != "", "FRONTEND_URL must be set"
    
    def test_feature_flags(self):
        """Test feature flags are properly configured"""
        assert os.getenv("FEATURE_VOICE", "false").lower() == "true", "FEATURE_VOICE should be enabled"
        assert os.getenv("FEATURE_N8N", "false").lower() == "true", "FEATURE_N8N should be enabled"
        assert os.getenv("FEATURE_RAG", "false").lower() == "true", "FEATURE_RAG should be enabled"


class TestNavigation:
    """Test navigation between pages"""
    
    def test_sidebar_navigation(self, page: Page):
        self._login(page)
        
        # Test navigation to different pages
        nav_items = [
            ("Dashboard", "/dashboard"),
            ("Assistant", "/chat"),
            ("Analytics", "/analytics"),
        ]
        
        for item_name, expected_path in nav_items:
            page.click(f"text={item_name}")
            expect(page).to_have_url(f"{BASE_URL}{expected_path}")
    
    def test_breadcrumb_navigation(self, page: Page):
        self._login(page)
        page.goto(f"{BASE_URL}/analytics")
        # Navigate to sub-page if exists
        # Then test breadcrumb navigation
        expect(page.locator(".breadcrumb")).to_be_visible()
    
    def _login(self, page: Page):
        page.goto(f"{BASE_URL}/login")
        page.fill("input[type='text']", "admin")
        page.fill("input[type='password']", "admin123")
        page.click("button[type='submit']")
        page.wait_for_url(f"{BASE_URL}/dashboard")


class TestResponsiveDesign:
    """Test responsive design on different screen sizes"""
    
    def test_mobile_view(self, page: Page):
        page.set_viewport_size({"width": 375, "height": 667})
        self._login(page)
        
        # On mobile, sidebar should be hidden or collapsible
        expect(page.locator(".sidebar")).to_have_css("display", "none")
        expect(page.locator(".mobile-menu-toggle")).to_be_visible()
    
    def test_tablet_view(self, page: Page):
        page.set_viewport_size({"width": 768, "height": 1024})
        self._login(page)
        
        # On tablet, sidebar should be visible
        expect(page.locator(".sidebar")).to_be_visible()
    
    def test_desktop_view(self, page: Page):
        page.set_viewport_size({"width": 1920, "height": 1080})
        self._login(page)
        
        # On desktop, all components should be visible
        expect(page.locator(".sidebar")).to_be_visible()
        expect(page.locator(".main-content")).to_be_visible()
    
    def _login(self, page: Page):
        page.goto(f"{BASE_URL}/login")
        page.fill("input[type='text']", "admin")
        page.fill("input[type='password']", "admin123")
        page.click("button[type='submit']")
        page.wait_for_url(f"{BASE_URL}/dashboard")


class TestPerformance:
    """Test page load performance"""
    
    def test_dashboard_load_time(self, page: Page):
        self._login(page)
        start_time = page.evaluate("() => Date.now()")
        page.goto(f"{BASE_URL}/dashboard")
        end_time = page.evaluate("() => Date.now()")
        load_time = end_time - start_time
        
        # Dashboard should load in less than 3 seconds
        assert load_time < 3000, f"Dashboard load time {load_time}ms exceeds 3000ms threshold"
    
    def test_analytics_load_time(self, page: Page):
        self._login(page)
        start_time = page.evaluate("() => Date.now()")
        page.goto(f"{BASE_URL}/analytics")
        end_time = page.evaluate("() => Date.now()")
        load_time = end_time - start_time
        
        # Analytics should load in less than 4 seconds (charts take longer)
        assert load_time < 4000, f"Analytics load time {load_time}ms exceeds 4000ms threshold"
    
    def _login(self, page: Page):
        page.goto(f"{BASE_URL}/login")
        page.fill("input[type='text']", "admin")
        page.fill("input[type='password']", "admin123")
        page.click("button[type='submit']")
        page.wait_for_url(f"{BASE_URL}/dashboard")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])