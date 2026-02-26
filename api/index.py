import sys
import os
# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, status, Query, Request, Security, Depends
from fastapi.security import APIKeyHeader
from fastapi.staticfiles import StaticFiles
from voyager.obc import OnBoardComputer
from voyager.ccsds import TelemetryPacket
import time
import secrets
from pathlib import Path

# Security Configuration
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def get_api_key():
    key = os.environ.get("VOYAGER_API_KEY")
    if not key:
        key = secrets.token_hex(32)
        # Log only if explicitly requested, otherwise secure default
        if os.environ.get("VOYAGER_SHOW_KEY") == "1":
            print(f"WARNING: VOYAGER_API_KEY not set. Generated key: {key}")
        else:
            print("WARNING: VOYAGER_API_KEY not set. Generated secure key (hidden). Set VOYAGER_SHOW_KEY=1 to see it.")
        os.environ["VOYAGER_API_KEY"] = key
    return key

# Initialize key once
VOYAGER_API_KEY = get_api_key()

async def verify_api_key(api_key: str = Security(api_key_header)):
    if not api_key or not secrets.compare_digest(api_key, VOYAGER_API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
        )
    return api_key

# Rate Limiting Logic
class RateLimiter:
    def __init__(self, calls: int, period: float):
        self.calls = calls
        self.period = period
        self.history = {}  # ip -> [timestamps]

    async def __call__(self, request: Request):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()

        # Initialize history for new IP
        if client_ip not in self.history:
            self.history[client_ip] = []

        # Filter timestamps to keep only those within the rolling window
        self.history[client_ip] = [t for t in self.history[client_ip] if now - t < self.period]

        # Check limit
        if len(self.history[client_ip]) >= self.calls:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )

        # Log new request
        self.history[client_ip].append(now)

# Security: Limit sensitive state-changing commands to prevent abuse/DoS
limit_sensitive = RateLimiter(calls=10, period=60.0)

app = FastAPI()

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' https://d3js.org; style-src 'self' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; object-src 'none'"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=(), payment=(), usb=()"

    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"

    return response

# Global OBC instance
obc = OnBoardComputer()
obc.boot()

# Health Check
@app.get("/api/health")
def health_check():
    return {"status": "ok", "timestamp": time.time()}


# API Routes
@app.get("/api/status", dependencies=[Depends(verify_api_key)])
def get_status():
    return {
        "mode": obc.mode,
        "reboot_count": obc.reboot_count,
        "watchdog_timer": obc.watchdog_timer,
        "frozen": obc.frozen
    }

@app.post("/api/command/reboot", dependencies=[Depends(verify_api_key), Depends(limit_sensitive)])
def command_reboot():
    obc.reboot()
    return {"message": "OBC Rebooted"}

@app.post("/api/command/freeze", dependencies=[Depends(verify_api_key), Depends(limit_sensitive)])
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

# Serve static files from the 'public' directory
# Mount this LAST so it doesn't shadow API routes
BASE_DIR = Path(__file__).resolve().parent.parent
public_path = BASE_DIR / "public"

if public_path.exists():
    print(f"Mounting static files from {public_path}")
    app.mount("/", StaticFiles(directory=str(public_path), html=True), name="public")
else:
    # On Vercel, static files are usually served by the edge, so they might not 
    # be present in the Python runtime environment. We skip mounting to avoid RuntimeError.
    print(f"Note: Static directory {public_path} not found. Skipping mount.")


