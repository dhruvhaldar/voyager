from fastapi.testclient import TestClient
from api.index import app, VOYAGER_API_KEY

client = TestClient(app)

def test_prevent_verbose_validation_errors():
    headers = {"X-API-Key": VOYAGER_API_KEY}
    response = client.post("/api/tick", params={"dt": "not_a_number"}, headers=headers)

    # Ensure it's not a 422 and doesn't leak
    assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
    assert "float_parsing" not in response.text
