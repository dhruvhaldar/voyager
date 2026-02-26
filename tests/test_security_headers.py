from fastapi.testclient import TestClient
from api.index import app

client = TestClient(app)

def test_security_headers_present():
    """
    Test that security headers are present in the response.
    We check both a successful response (if possible) and an error response.
    Even 401 Unauthorized should have security headers.
    """
    # We don't clear dependency_overrides because it breaks other tests (e.g. test_security_time.py)
    # running in the same session.

    # unauthorized request (or authorized if overridden)
    response = client.get("/api/status")

    # Check headers
    headers = response.headers

    # X-Content-Type-Options: nosniff
    assert headers.get("X-Content-Type-Options") == "nosniff"

    # X-Frame-Options: DENY
    assert headers.get("X-Frame-Options") == "DENY"

    # X-XSS-Protection: 1; mode=block
    # Note: Modern browsers ignore this, but it's good for legacy.
    # We'll check if it's there.
    assert "1; mode=block" in headers.get("X-XSS-Protection", "")

    # Referrer-Policy: strict-origin-when-cross-origin
    assert headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"

    # Content-Security-Policy
    csp = headers.get("Content-Security-Policy", "")
    assert "default-src 'self'" in csp
    assert "script-src" in csp
    assert "object-src 'none'" in csp

    # Permissions-Policy
    assert headers.get("Permissions-Policy") == "geolocation=(), microphone=(), camera=(), payment=(), usb=()"

def test_api_cache_control():
    """
    Test that API endpoints have strict cache control.
    """
    response = client.get("/api/health")
    headers = response.headers

    assert headers.get("Cache-Control") == "no-store"
