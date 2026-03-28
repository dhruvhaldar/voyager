import pytest
from fastapi.testclient import TestClient
from api.index import app, limit_tick

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Reset the rate limiter state before each test."""
    limit_tick.history.clear()
    yield

def test_unauthenticated_status_polling_blocked_by_rate_limit():
    """
    Test that unauthenticated requests to status endpoint are subject to the rate limiter before auth rejection.
    """
    # Make enough requests to trigger the limit_tick limit
    for _ in range(100):
        response = client.get("/api/status")
        assert response.status_code == 401, f"Expected 401 Unauthorized for initial requests, got {response.status_code}"

    # The 101st request should hit the 429 Too Many Requests limit instead of 401
    response = client.get("/api/status")
    assert response.status_code == 429, f"Expected 429 Too Many Requests, got {response.status_code}"

def test_unauthenticated_telemetry_polling_blocked_by_rate_limit():
    """
    Test that unauthenticated requests to telemetry endpoint are subject to the rate limiter before auth rejection.
    """
    # Make enough requests to trigger the limit_tick limit
    for _ in range(100):
        response = client.get("/api/telemetry/latest")
        assert response.status_code == 401, f"Expected 401 Unauthorized for initial requests, got {response.status_code}"

    # The 101st request should hit the 429 Too Many Requests limit instead of 401
    response = client.get("/api/telemetry/latest")
    assert response.status_code == 429, f"Expected 429 Too Many Requests, got {response.status_code}"