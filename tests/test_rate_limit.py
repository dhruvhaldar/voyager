import pytest
import time
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Import the app and key
from api.index import app, VOYAGER_API_KEY, limit_sensitive

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Reset the rate limiter state before each test."""
    limit_sensitive.history.clear()
    yield

def test_rate_limiting_enforcement():
    """Test that requests are blocked after exceeding the limit."""
    headers = {"X-API-Key": VOYAGER_API_KEY}

    # Patch time where it is used. api.index imports time, so we patch api.index.time.time
    # Or simply patch time.time globally for the test duration.
    with patch("time.time", return_value=1000.0):
        # The limit is 10 calls per 60 seconds.
        # Make 10 allowed requests
        for i in range(10):
            response = client.post("/api/command/freeze", headers=headers)
            assert response.status_code == 200, f"Request {i+1} failed with {response.status_code}"
            assert response.json()["message"] == "OBC Frozen"

        # Make the 11th request, should fail
        response = client.post("/api/command/freeze", headers=headers)
        assert response.status_code == 429, "Expected 429 Too Many Requests"
        assert "Rate limit exceeded" in response.json()["detail"]

def test_rate_limit_reset():
    """Test that the rate limit resets after the period expires."""
    headers = {"X-API-Key": VOYAGER_API_KEY}

    # Use side_effect or just manipulate return_value between calls if we control the flow
    # But patching time.time is tricky if we want it to advance.
    # So we use a MagicMock where we can set return_value dynamically?
    # Or just patch it with a function or property?

    # Let's use a mutable list to simulate time flow if needed, or just patch for blocks.

    with patch("time.time") as mock_time:
        mock_time.return_value = 1000.0

        # Exhaust limit
        for _ in range(10):
            client.post("/api/command/reboot", headers=headers)

        # Verify blocked
        response = client.post("/api/command/reboot", headers=headers)
        assert response.status_code == 429

        # Advance time by 61 seconds (beyond window)
        mock_time.return_value = 1061.0

        # Should be allowed again
        response = client.post("/api/command/reboot", headers=headers)
        assert response.status_code == 200
        assert response.json()["message"] == "OBC Rebooted"

def test_rate_limit_distinct_endpoints_share_limit():
    """
    Test that distinct endpoints share the same limiter instance if configured that way.
    In our case, we reused `limit_sensitive` for both reboot and freeze.
    So calls to reboot should count against freeze quota.
    """
    headers = {"X-API-Key": VOYAGER_API_KEY}

    with patch("time.time", return_value=2000.0):
        # 5 reboots
        for _ in range(5):
            client.post("/api/command/reboot", headers=headers)

        # 5 freezes
        for _ in range(5):
            client.post("/api/command/freeze", headers=headers)

        # 11th request (reboot) should fail
        response = client.post("/api/command/reboot", headers=headers)
        assert response.status_code == 429
