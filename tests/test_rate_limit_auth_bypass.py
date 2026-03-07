import pytest
from fastapi.testclient import TestClient
from api.index import app, limit_sensitive

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_rate_limiter():
    limit_sensitive.history.clear()
    yield

def test_rate_limit_enforced_before_auth():
    """
    Test that rate limiting is evaluated before authentication.
    If auth is evaluated first, an attacker can bypass the rate limiter
    by sending unauthenticated requests, allowing them to DoS the endpoint
    by overwhelming the auth mechanism or downstream systems.
    """
    # Send 10 unauthenticated requests
    for i in range(10):
        response = client.post("/api/command/freeze")
        assert response.status_code == 401, f"Expected 401 Unauthorized for request {i+1}, got {response.status_code}"

    # The 11th request should hit the rate limit (429), not the auth check (401)
    response = client.post("/api/command/freeze")
    assert response.status_code == 429, "Rate limit should block the request before auth check"
