from fastapi.testclient import TestClient
from api.index import app

client = TestClient(app)

def test_csp_no_unsafe_inline():
    """
    Test that 'unsafe-inline' is NOT present in the Content-Security-Policy header.
    This ensures that our security enhancement is effective.
    """
    response = client.get("/api/status")
    csp = response.headers.get("Content-Security-Policy", "")

    assert "unsafe-inline" not in csp, "CSP should not contain 'unsafe-inline'"
    assert "default-src 'self'" in csp
    assert "script-src 'self' https://d3js.org" in csp
    assert "style-src 'self'" in csp
