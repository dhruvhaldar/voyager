import sys
import os
# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, status, Query, Request, Security, Depends
from fastapi.security import APIKeyHeader
from voyager.obc import OnBoardComputer
from voyager.ccsds import TelemetryPacket
import time
import secrets
from pathlib import Path

# Security Configuration
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

VOYAGER_API_KEY = os.environ.get("VOYAGER_API_KEY")
if not VOYAGER_API_KEY:
    # Generate a secure random key if not provided
    VOYAGER_API_KEY = secrets.token_urlsafe(32)
    print(f"SECURITY WARNING: VOYAGER_API_KEY not set. Using generated key: {VOYAGER_API_KEY}")

async def get_api_key(api_key_header: str = Security(api_key_header)):
    """Validates the API Key from the request header."""
    if not api_key_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key",
        )
    # constant-time comparison to prevent timing attacks
    if not secrets.compare_digest(api_key_header, VOYAGER_API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
    return api_key_header

app = FastAPI()

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' https://d3js.org; style-src 'self' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; object-src 'none'"
    return response

# Global OBC instance
obc = OnBoardComputer()
obc.boot()

# API Routes
@app.get("/api/status")
def get_status():
    return {
        "mode": obc.mode,
        "reboot_count": obc.reboot_count,
        "watchdog_timer": obc.watchdog_timer,
        "frozen": obc.frozen
    }

@app.post("/api/command/reboot", dependencies=[Depends(get_api_key)])
def command_reboot():
    obc.reboot()
    return {"message": "OBC Rebooted"}

@app.post("/api/command/freeze", dependencies=[Depends(get_api_key)])
def command_freeze():
    obc.freeze()
    return {"message": "OBC Frozen"}

@app.post("/api/tick", dependencies=[Depends(get_api_key)])
def tick_simulation(dt: float = Query(1.0, ge=0)):
    obc.tick(dt)
    return {"message": f"Simulation advanced by {dt}s", "status": get_status()}

@app.get("/api/telemetry/latest")
def get_telemetry():
    # Simulate generating a packet
    packet = TelemetryPacket(
        apid=0x10,
        sequence_count=int(time.time()) % 16384,
        data=b"VoyagerStatus"
    )
    raw_bytes = packet.to_bytes()
    return {
        "hex": raw_bytes.hex(sep=' ').upper(),
        "apid": packet.apid,
        "sequence_count": packet.sequence_count,
        "valid_crc": True 
    }
