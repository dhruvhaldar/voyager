from fastapi.testclient import TestClient
from api.index import app, VOYAGER_API_KEY

client = TestClient(app)

def test_batched_telemetry():
    response = client.get("/api/telemetry/latest", headers={"X-API-Key": VOYAGER_API_KEY})
    assert response.status_code == 200
    data = response.json()
    assert "hex" in data
    assert "status" in data
    assert "mode" in data["status"]
    assert "reboot_count" in data["status"]
    assert "watchdog_timer" in data["status"]
    assert "frozen" in data["status"]
