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

def test_rate_limit_wipe_bypass():
    """
    Test that an attacker cannot wipe the rate limit history by flooding
    the server with spoofed IPs.
    """
    headers = {"X-API-Key": VOYAGER_API_KEY}

    # Temporarily set max_entries to a small number for testing
    original_max = limit_sensitive.max_entries
    limit_sensitive.max_entries = 5

    try:
        # 1. Attacker (IP A) sends a request and is tracked
        headers["X-Forwarded-For"] = "1.1.1.1"
        response = client.post("/api/command/freeze", headers=headers)
        assert response.status_code == 200

        # 2. Attacker spoofs enough IPs to fill the history to max_entries
        for i in range(5):
            headers["X-Forwarded-For"] = f"2.2.2.{i}"
            client.post("/api/command/freeze", headers=headers)

        # 3. Attacker sends one more request from a new spoofed IP
        # This should hit the max_entries limit and fail securely (429)
        headers["X-Forwarded-For"] = "3.3.3.3"
        response = client.post("/api/command/freeze", headers=headers)
        assert response.status_code == 429
        assert "Server at capacity" in response.json()["detail"]

        # 4. The original IP A should still be in the history and subject to its own rate limit
        # If the history was wiped, IP A would be able to bypass the limit.
        # But we haven't hit IP A's limit yet (it only sent 1 request, limit is 10).
        # We can just verify IP A is still in the history map.
        assert "1.1.1.1" in limit_sensitive.history

    finally:
        # Restore original max_entries
        limit_sensitive.max_entries = original_max
