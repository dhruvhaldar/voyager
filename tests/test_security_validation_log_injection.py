import pytest
import logging
from fastapi.testclient import TestClient
from api.index import app, VOYAGER_API_KEY

client = TestClient(app)

def test_validation_log_injection_prevention(caplog):
    """
    Test that malicious input causing a validation error does not result in
    log injection (CRLF or ANSI escapes) in the server logs.
    """
    malicious_input = "\x1b[31m HACKED \x1b[0m\nCRLF_INJECTION"
    headers = {"X-API-Key": VOYAGER_API_KEY}

    with caplog.at_level(logging.ERROR):
        response = client.post("/api/tick", params={"dt": malicious_input}, headers=headers)

        assert response.status_code == 400

        log_messages = [record.message for record in caplog.records if "Validation error" in record.message]
        assert len(log_messages) == 1

        logged_message = log_messages[0]

        # Newlines and ANSI should be escaped, so they appear as \n and \x1b literally, not actually executing
        assert "\n" not in logged_message
        assert "\x1b" not in logged_message
        assert "\\n" in logged_message
        assert "\\x1b" in logged_message
