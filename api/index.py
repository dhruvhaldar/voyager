import sys
import os
# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, status, Query, Request
from fastapi.staticfiles import StaticFiles
from voyager.obc import OnBoardComputer
from voyager.ccsds import TelemetryPacket
import time

from pathlib import Path

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

# Resilient path discovery for Vercel
def find_static_file(filename: str) -> Path:
    # Potential locations relative to this file (api/index.py)
    search_paths = [
        Path(__file__).parent.parent / "public" / filename,  # Local/Standard
        Path(__file__).parent.parent / filename,           # Flattened
        Path.cwd() / "public" / filename,                  # CWD based
        Path.cwd() / filename,                             # Root based
    ]
    for path in search_paths:
        if path.exists():
            return path
    return None

@app.get("/", include_in_schema=False)
async def read_root():
    from fastapi.responses import FileResponse
    path = find_static_file("index.html")
    if path:
        return FileResponse(path)
    # If not found, list directory to help debug (or just 404)
    raise HTTPException(status_code=404, detail=f"index.html not found. CWD: {os.getcwd()}")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    from fastapi.responses import FileResponse
    path = find_static_file("favicon.ico")
    if path:
        return FileResponse(path)
    from fastapi import Response
    return Response(status_code=204)

# API Routes
@app.get("/api/status")
def get_status():
    return {
        "mode": obc.mode,
        "reboot_count": obc.reboot_count,
        "watchdog_timer": obc.watchdog_timer,
        "frozen": obc.frozen
    }

@app.post("/api/command/reboot")
def command_reboot():
    obc.reboot()
    return {"message": "OBC Rebooted"}

@app.post("/api/command/freeze")
def command_freeze():
    obc.freeze()
    return {"message": "OBC Frozen"}

@app.post("/api/tick")
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

# Serve static files for frontend fallback
base_dir = Path(__file__).resolve().parent.parent
public_dir = base_dir / "public"
if not public_dir.exists():
    public_dir = base_dir # Hard fallback to root

app.mount("/", StaticFiles(directory=str(public_dir), html=True), name="public")
