import sys
import os
from pathlib import Path

# Mock FastAPI app for local testing without starting a server
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent))

try:
    from api.index import app
    client = TestClient(app)
    
    print("Attempting to call /api/status...")
    response = client.get("/api/status")
    print(f"Status: {response.status_code}, Body: {response.json()}")
    
    print("Attempting to call /api/command/freeze...")
    response = client.post("/api/command/freeze")
    print(f"Status: {response.status_code}, Body: {response.json()}")
    
    print("Attempting to call /api/tick...")
    response = client.post("/api/tick", params={"dt": 1.0})
    print(f"Status: {response.status_code}, Body: {response.json()}")
    
    print("Reproduction successful - no crashes.")

except Exception as e:
    print(f"Caught exception: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
