import pytest
from fastapi.testclient import TestClient
from api.index import app, VOYAGER_API_KEY

client = TestClient(app)

def test_unauthenticated_command_access():
    """
    Test that critical command endpoints are protected.
    """
    response = client.post("/api/command/freeze")
    assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}"

def test_unauthenticated_telemetry_access():
    """
    Test that sensitive telemetry endpoints are protected.
    """
    response = client.get("/api/telemetry/latest")
    assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}"

def test_authenticated_access():
    """
    Test that authenticated requests succeed with the correct key.
    """
    headers = {"X-API-Key": VOYAGER_API_KEY}

    # Test Command
    response = client.post("/api/command/freeze", headers=headers)
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    assert response.json()["message"] == "OBC Frozen"

    # Test Telemetry
    response = client.get("/api/telemetry/latest", headers=headers)
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    data = response.json()
    assert "hex" in data
    assert "apid" in data
