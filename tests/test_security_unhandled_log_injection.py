import pytest
import logging
from fastapi.testclient import TestClient
from api.index import app, VOYAGER_API_KEY
from unittest.mock import patch

# IMPORTANT: we must override the default Starlette raise_server_exceptions logic
client = TestClient(app, raise_server_exceptions=False)

def test_unhandled_exception_log_injection_prevention(caplog):
    malicious_input = "\x1b[31m HACKED \x1b[0m\nCRLF_INJECTION"
    headers = {"X-API-Key": VOYAGER_API_KEY}

    with patch("api.index.obc.reboot", side_effect=ValueError(malicious_input)):
        with caplog.at_level(logging.ERROR):
            response = client.post("/api/command/reboot", headers=headers)

            assert response.status_code == 500

            log_messages = [record.message for record in caplog.records if "Unhandled exception" in record.message]
            assert len(log_messages) == 1

            record = [r for r in caplog.records if "Unhandled exception" in r.message][0]
            assert record.exc_info is None or record.exc_info == False

            logged_message = record.message

            assert "\n" not in logged_message
            assert "\x1b" not in logged_message
            assert "\\n" in logged_message
            assert "\\x1b" in logged_message
