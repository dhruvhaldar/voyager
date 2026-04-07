import pytest
import logging
from fastapi.testclient import TestClient
from api.index import app

client = TestClient(app)

def test_log_injection_prevention(caplog):
    """
    Test that CRLF characters in the client IP (via X-Forwarded-For)
    are sanitized and do not result in log injection.
    """
    # Send a request with a malicious X-Forwarded-For header containing CRLF
    malicious_ip = "127.0.0.1\n[CRITICAL] HACKED\r\n"

    with caplog.at_level(logging.WARNING):
        response = client.post("/api/command/freeze", headers={"X-Forwarded-For": malicious_ip})

        # The request should fail due to missing/invalid API key
        assert response.status_code == 401

        # Verify the log message does not contain the injected newline
        log_messages = [record.message for record in caplog.records if "Unauthorized API access attempt" in record.message]
        assert len(log_messages) == 1

        logged_message = log_messages[0]
        # The newlines should have been removed by the sanitization
        assert "\n" not in logged_message
        assert "\r" not in logged_message
        assert "127.0.0.1[CRITICAL] HACKED" in logged_message
