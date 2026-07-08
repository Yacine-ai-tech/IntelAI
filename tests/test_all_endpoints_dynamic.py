import pytest
from fastapi.testclient import TestClient
import re

# We will import the app dynamically based on the project structure
def get_app():
    try:
        from src.api.server import app
        return app
    except ImportError:
        pass
    try:
        from api import app
        return app
    except ImportError:
        pass
    try:
        from web_app import app
        return app
    except ImportError:
        pass
    try:
        from main import app
        return app
    except ImportError:
        pass
    try:
        from src.main import app
        return app
    except ImportError:
        pass
    try:
        from api.server import app
        return app
    except ImportError:
        pass
    try:
        from server import app
        return app
    except ImportError:
        pass
    try:
        from app import app
        return app
    except ImportError:
        raise ImportError("Could not find FastAPI app to test.")

app = get_app()
client = TestClient(app)

def get_all_routes():
    routes = []
    if not hasattr(app, "routes"):
        return routes
    for route in app.routes:
        if hasattr(route, "methods"):
            for method in route.methods:
                if method in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                    routes.append((method, route.path))
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
