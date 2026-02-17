import sys
import os
# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Header, HTTPException, status, Depends, Query
from fastapi.staticfiles import StaticFiles
from voyager.obc import OnBoardComputer
from voyager.ccsds import TelemetryPacket
import time
import secrets

app = FastAPI()

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

@app.get("/api/status")
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

@app.get("/api/telemetry/latest")
def get_telemetry():
    # Simulate generating a packet
    # Sequence count could be based on time or internal counter
    packet = TelemetryPacket(
        apid=0x10,
        sequence_count=int(time.time()) % 16384,
        data=b"VoyagerStatus"
    )
    return {
        "hex": packet.hex_dump(),
        "apid": packet.apid,
        "sequence_count": packet.sequence_count,
        "valid_crc": TelemetryPacket.validate_crc(packet.to_bytes())
    }

# Serve static files for frontend (public folder)
# This should be at the end to avoid overriding API routes
if os.path.exists("public"):
    app.mount("/", StaticFiles(directory="public", html=True), name="public")
