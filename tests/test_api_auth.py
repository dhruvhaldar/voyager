import pytest
from fastapi.testclient import TestClient
from api.index import app, verify_api_key

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_overrides():
    # If test_security_time.py ran, it set overrides.
    # We clear them for OUR tests.
    original_overrides = app.dependency_overrides.copy()
    app.dependency_overrides = {}
    yield
    # Restore for other tests (though typically redundant if pytest isolation works)
    app.dependency_overrides = original_overrides

def test_status_requires_auth():
    # Currently this fails because it's public (200)
    # After fix, it should be 401
    response = client.get("/api/status")
    if response.status_code == 200:
        pytest.fail("Endpoint is public! Fix required.")
    assert response.status_code == 401
    assert response.json() == {"detail": "Missing API Key"}

def test_telemetry_requires_auth():
    # Currently this fails because it's public (200)
    # After fix, it should be 401
    response = client.get("/api/telemetry/latest")
    if response.status_code == 200:
        pytest.fail("Endpoint is public! Fix required.")
    assert response.status_code == 401
    assert response.json() == {"detail": "Missing API Key"}

def test_status_authorized():
    app.dependency_overrides[verify_api_key] = lambda: True
    response = client.get("/api/status")
    assert response.status_code == 200
    # Clean up locally
    del app.dependency_overrides[verify_api_key]

def test_telemetry_authorized():
    app.dependency_overrides[verify_api_key] = lambda: True
    response = client.get("/api/telemetry/latest")
    assert response.status_code == 200
    # Clean up locally
    del app.dependency_overrides[verify_api_key]
