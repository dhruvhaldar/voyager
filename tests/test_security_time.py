import pytest
from fastapi.testclient import TestClient
from api.index import app
from voyager.obc import OnBoardComputer

client = TestClient(app)

def test_tick_negative_dt_api():
    """
    Test that sending a negative dt via the API returns a 422 error.
    """
    response = client.post("/api/tick", params={"dt": -1.0})
    assert response.status_code == 422

    # Verify that positive dt still works
    response = client.post("/api/tick", params={"dt": 1.0})
    assert response.status_code == 200

def test_tick_negative_dt_internal():
    """
    Test that calling obc.tick() with a negative dt raises a ValueError.
    """
    obc = OnBoardComputer()
    obc.boot()

    with pytest.raises(ValueError, match="Time step must be non-negative"):
        obc.tick(-1.0)
