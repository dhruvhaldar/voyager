from fastapi.testclient import TestClient
from api.index import app

client = TestClient(app)

def test_docs_exposure():
    """
    Test that automatic API documentation is disabled.
    """
    # /docs (Swagger UI)
    response = client.get("/docs")
    assert response.status_code == 404, f"Expected 404 Not Found for /docs, got {response.status_code}"

    # /redoc (ReDoc)
    response = client.get("/redoc")
    assert response.status_code == 404, f"Expected 404 Not Found for /redoc, got {response.status_code}"

    # /openapi.json (OpenAPI schema)
    response = client.get("/openapi.json")
    assert response.status_code == 404, f"Expected 404 Not Found for /openapi.json, got {response.status_code}"
