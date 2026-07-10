import pytest
from fastapi.testclient import TestClient
import re

# We will import the app dynamically based on the project structure
def get_app():
    from src.api.server import app
    return app

app = get_app()
client = TestClient(app)

def get_all_routes():
    routes = []
    if not hasattr(app, "routes"):
        return routes
    for route in app.routes:
        if hasattr(route, "methods") and hasattr(route, "path"):
            for method in route.methods:
                if method in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                    routes.append((method, getattr(route, "path")))
    return routes

@pytest.mark.parametrize("method, path", get_all_routes())
def test_all_endpoints_prevent_500_errors(method, path):
    """
    Dynamically tests every single endpoint in the FastAPI application.
    Ensures that no endpoint returns a 500 Internal Server Error when called
    without authentication or with dummy path variables.
    """
    test_path = re.sub(r'\{.*?\}', 'test_dummy_param', path)
    
    # Send empty JSON for POST/PUT/PATCH to trigger 422 instead of 500
    # when body is required
    json_payload = {} if method in ["POST", "PUT", "PATCH"] else None
    
    response = client.request(method, test_path, json=json_payload)
    
    # 500 means the server crashed, any other status code means 
    # the request was handled properly (even if unauthorized or validation failed)
    assert response.status_code != 500, f"Endpoint {method} {path} returned 500 Internal Server Error"
