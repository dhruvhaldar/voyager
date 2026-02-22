import sys
import os
# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, status, Query, Request
from fastapi.staticfiles import StaticFiles
from voyager.obc import OnBoardComputer
from voyager.ccsds import TelemetryPacket
import time

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

# Helper to find static files
def get_static_path(filename):
    # Try relative to CWD and project root
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    paths = [
        os.path.join(base_dir, "public", filename),
        os.path.join(base_dir, filename),
        os.path.join("public", filename),
        filename
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return None

@app.get("/", include_in_schema=False)
async def read_root():
    from fastapi.responses import FileResponse
    path = get_static_path("index.html")
    if path:
        return FileResponse(path)
    raise HTTPException(status_code=404, detail="index.html not found")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    from fastapi.responses import FileResponse
    path = get_static_path("favicon.ico")
    if path:
        return FileResponse(path)
    from fastapi import Response
    return Response(status_code=204)

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

# Serve static files for frontend (public folder)
if os.path.exists("public"):
    app.mount("/", StaticFiles(directory="public", html=True), name="public")
