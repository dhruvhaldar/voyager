import pytest
from fastapi.testclient import TestClient
from api.index import app, VOYAGER_API_KEY, limit_sensitive

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_rate_limiter():
    limit_sensitive.history.clear()
    yield

def test_rate_limit_bypass_prevention_via_x_forwarded_for():
    headers = {"X-API-Key": VOYAGER_API_KEY}

    # Send 10 requests simulating a user trying to spoof their IP behind a proxy.
    # The proxy (e.g. Vercel) appends the real IP ("203.0.113.1") to the end of the chain.
    for i in range(10):
        # The attacker sends "10.0.0.X", and the proxy appends the real IP.
        headers["X-Forwarded-For"] = f"10.0.0.{i}, 203.0.113.1"
        response = client.post("/api/command/freeze", headers=headers)
        assert response.status_code == 200

    # The 11th request from the same real IP should be blocked,
    # even if the attacker continues to spoof the first IP in the chain.
    headers["X-Forwarded-For"] = "10.0.0.99, 203.0.113.1"
    response = client.post("/api/command/freeze", headers=headers)

    # We expect 429 Too Many Requests because the rate limiter should correctly
    # identify the real IP (203.0.113.1) and block the request.
    assert response.status_code == 429, "Rate limit should block the real IP despite spoofing attempts."

def test_rate_limit_bypass_prevention_single_ip():
    headers = {"X-API-Key": VOYAGER_API_KEY}

    # If there is no proxy appending an IP, the single IP provided is treated as the client IP.
    for i in range(10):
        headers["X-Forwarded-For"] = "192.168.1.100"
        response = client.post("/api/command/freeze", headers=headers)
        assert response.status_code == 200

    # 11th request from same IP should be blocked
    headers["X-Forwarded-For"] = "192.168.1.100"
    response = client.post("/api/command/freeze", headers=headers)
    assert response.status_code == 429
