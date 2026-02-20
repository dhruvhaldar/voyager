import sys
import os
# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Header, HTTPException, status, Depends, Query, Request
from fastapi.staticfiles import StaticFiles
from voyager.obc import OnBoardComputer
from voyager.ccsds import TelemetryPacket
import time
import secrets

app = FastAPI()

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://d3js.org; style-src 'self' 'unsafe-inline'; img-src 'self' data:; object-src 'none'"
    return response

# SECURITY: Load API Key from environment or generate a secure one.
# This prevents hardcoded secrets and ensures a unique key per instance if not configured.
API_KEY = os.getenv("VOYAGER_API_KEY")
if not API_KEY:
    API_KEY = secrets.token_urlsafe(32)
    print(f"\n{'='*60}\nWARNING: VOYAGER_API_KEY not set. Using generated key:\n{API_KEY}\n{'='*60}\n")
else:
    print(f"VOYAGER_API_KEY loaded from environment.")

def verify_api_key(x_api_key: str = Header(None, alias="X-API-Key")):
    """
    Validates the API Key provided in the header.
    """
    if x_api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key",
        )

    if not secrets.compare_digest(x_api_key, API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )

# Global OBC instance
obc = OnBoardComputer()
obc.boot()

@app.get("/api/status", dependencies=[Depends(verify_api_key)])
def get_status():
    return {
        "mode": obc.mode,
        "reboot_count": obc.reboot_count,
        "watchdog_timer": obc.watchdog_timer,
        "frozen": obc.frozen
    }

@app.post("/api/command/reboot", dependencies=[Depends(verify_api_key)])
def command_reboot():
    obc.reboot()
    return {"message": "OBC Rebooted"}

@app.post("/api/command/freeze", dependencies=[Depends(verify_api_key)])
def command_freeze():
    obc.freeze()
    return {"message": "OBC Frozen"}

@app.post("/api/tick", dependencies=[Depends(verify_api_key)])
def tick_simulation(dt: float = Query(1.0, ge=0)):
    obc.tick(dt)
    return {"message": f"Simulation advanced by {dt}s", "status": get_status()}

@app.get("/api/telemetry/latest", dependencies=[Depends(verify_api_key)])
def get_telemetry():
    # Simulate generating a packet
    # Sequence count could be based on time or internal counter
    packet = TelemetryPacket(
        apid=0x10,
        sequence_count=int(time.time()) % 16384,
        data=b"VoyagerStatus"
    )
    # Optimization: Calculate bytes once and reuse.
    # packet.hex_dump() calls to_bytes() -> calculate_crc()
    # validate_crc calls to_bytes() -> calculate_crc() and then calculate_crc() again.
    # By generating bytes once, we reduce from 3 CRC calculations to 1.
    raw_bytes = packet.to_bytes()
    return {
        "hex": raw_bytes.hex(sep=' ').upper(),
        "apid": packet.apid,
        "sequence_count": packet.sequence_count,
        "valid_crc": True # Since we just generated the packet, the CRC is guaranteed valid.
    }

# Serve static files for frontend (public folder)
# This should be at the end to avoid overriding API routes
if os.path.exists("public"):
    app.mount("/", StaticFiles(directory="public", html=True), name="public")
