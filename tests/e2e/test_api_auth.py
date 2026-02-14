from fastapi.testclient import TestClient
from api.index import app
import os

client = TestClient(app)

API_KEY = os.getenv("VOYAGER_API_KEY", "voyager-secret-123")

def test_public_endpoints():
    """Verify that public endpoints are accessible without authentication."""
    response = client.get("/api/status")
    assert response.status_code == 200

    response = client.get("/api/telemetry/latest")
    assert response.status_code == 200

def test_protected_endpoints_no_auth():
    """Verify that protected endpoints reject requests without API Key."""
    # Reboot
    response = client.post("/api/command/reboot")
    assert response.status_code == 403
    assert response.json() == {"detail": "Invalid or missing API Key"}

    # Freeze
    response = client.post("/api/command/freeze")
    assert response.status_code == 403

    # Tick
    response = client.post("/api/tick?dt=1.0")
    assert response.status_code == 403

def test_protected_endpoints_with_auth():
    """Verify that protected endpoints accept requests with correct API Key."""
    headers = {"X-API-Key": API_KEY}

    # Tick first (least destructive)
    response = client.post("/api/tick?dt=0.1", headers=headers)
    assert response.status_code == 200
    assert "Simulation advanced" in response.json()["message"]

    # Freeze
    response = client.post("/api/command/freeze", headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "OBC Frozen"

    # Reboot
    response = client.post("/api/command/reboot", headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "OBC Rebooted"

def test_protected_endpoints_wrong_key():
    """Verify that protected endpoints reject requests with wrong API Key."""
    headers = {"X-API-Key": "wrong-key"}

    response = client.post("/api/command/reboot", headers=headers)
    assert response.status_code == 403
