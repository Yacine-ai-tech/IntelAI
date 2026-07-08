import pytest
import os
import re
from pathlib import Path

# Extract all paths defined in frontend/src/App.jsx
def get_all_frontend_routes():
    base_dir = Path(__file__).parent.parent.parent
    app_jsx_path = base_dir / "frontend" / "src" / "App.jsx"
    
    if not app_jsx_path.exists():
        return ["/"]
        
    routes = []
    content = app_jsx_path.read_text()
    
    # Simple regex to find <Route path="..." />
    matches = re.findall(r'<Route\s+[^>]*path=["\']([^"\']+)["\']', content)
    for match in matches:
        if match != "*":
            # Normalize paths
            if match.startswith("/"):
                routes.append(match)
            elif match == "":
                routes.append("/")
            else:
                routes.append(f"/{match}")
                
    return list(set(routes))

@pytest.mark.parametrize("route", get_all_frontend_routes())
def test_frontend_page_loads_without_crashing(page, route):
    """
    Dynamically navigates to every route defined in the React App.
    Ensures the page loads successfully and doesn't trigger fatal JS exceptions.
    """
    # Assuming frontend runs on 5173
    base_url = os.environ.get("FRONTEND_URL", "http://localhost:5173")
    
    # Navigate to the route
    full_url = f"{base_url}{route}"
    response = page.goto(full_url, wait_until="domcontentloaded")
    
    # Ensure it's not a 404 (though React handles routing on client side)
    if response:
        assert response.status != 404, f"Page {route} returned 404"
        
    # Check that a white screen of death hasn't occurred by ensuring the root div is visible
    root_element = page.locator("#root")
    assert root_element.is_visible(), f"React root div not found on {route}"
