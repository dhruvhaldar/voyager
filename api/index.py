import sys
import os
# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, status, Query, Request, Security, Depends
from fastapi.security import APIKeyHeader
from fastapi.staticfiles import StaticFiles
from voyager.obc import OnBoardComputer, SimulationError
from voyager.ccsds import TelemetryPacket
import time
import secrets
from pathlib import Path
from collections import deque

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
    def __init__(self, calls: int, period: float, max_entries: int = 10000):
        self.calls = calls
        self.period = period
        self.max_entries = max_entries
        self.history = {}  # ip -> [timestamps]

    async def __call__(self, request: Request):
        # Extract real IP behind reverse proxies (like Vercel)
        client_ip = request.headers.get("X-Forwarded-For")
        if client_ip:
            # Prevent IP spoofing: use the rightmost IP in the X-Forwarded-For chain,
            # which is the one appended by the last proxy (e.g., Vercel edge).
            client_ip = client_ip.split(",")[-1].strip()
        else:
            client_ip = request.headers.get("X-Real-IP")

        if not client_ip:
            client_ip = request.client.host if request.client else "unknown"

        now = time.time()

        # Security: Prevent Memory Exhaustion (OOM) DoS
        if len(self.history) >= self.max_entries and client_ip not in self.history:
            # Clear old entries to free memory
            self.history = {ip: times for ip, times in self.history.items() if times and now - times[-1] < self.period}
            # If still full, clear entirely to prioritize availability
            if len(self.history) >= self.max_entries:
                self.history.clear()

        # Initialize history for new IP
        if client_ip not in self.history:
            self.history[client_ip] = deque()

        # Filter timestamps to keep only those within the rolling window
        # Optimization: Use deque to pop left in O(1) time instead of O(N) list comprehension
        # This significantly reduces CPU time when N (rate limit calls) is large.
        while self.history[client_ip] and now - self.history[client_ip][0] >= self.period:
            self.history[client_ip].popleft()

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

from fastapi.responses import JSONResponse

app = FastAPI()

@app.exception_handler(SimulationError)
async def simulation_error_handler(request: Request, exc: SimulationError):
    # Sentinel Security Enhancement: Prevent internal exception stack traces
    # from leaking via 500 responses by catching domain SimulationErrors and
    # returning a sanitized 400 Bad Request.
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Invalid parameter value provided."}
    )

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' https://d3js.org; style-src 'self' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; object-src 'none'; frame-ancestors 'none'; base-uri 'none'; upgrade-insecure-requests;"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=(), payment=(), usb=()"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

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

@app.post("/api/command/reboot", dependencies=[Depends(limit_sensitive), Depends(verify_api_key)])
def command_reboot():
    obc.reboot()
    return {"message": "OBC Rebooted"}

@app.post("/api/command/freeze", dependencies=[Depends(limit_sensitive), Depends(verify_api_key)])
def command_freeze():
    obc.freeze()
    return {"message": "OBC Frozen"}

@app.post("/api/tick", dependencies=[Depends(verify_api_key)])
def tick_simulation(dt: float = Query(1.0, ge=0)):
    obc.tick(dt)
    return {"message": f"Simulation advanced by {dt}s", "status": get_status()}

# Optimization: Cache the telemetry response per sequence count.
# The sequence count changes once per second (int(time.time())).
# This avoids redundant packet generation, CRC calculation, and hex formatting
# for multiple clients polling within the same second.
_telemetry_cache = {"seq": -1, "res": None}

@app.get("/api/telemetry/latest", dependencies=[Depends(verify_api_key)])
def get_telemetry():
    seq = int(time.time()) % 16384

    # Always get fresh status, even if telemetry is cached
    current_status = get_status()

    if seq == _telemetry_cache["seq"]:
        res = dict(_telemetry_cache["res"])
        res["status"] = current_status
        return res

    # Simulate generating a packet
    packet = TelemetryPacket(
        apid=0x10,
        sequence_count=seq,
        data=b"VoyagerStatus"
    )
    raw_bytes = packet.to_bytes()

    _telemetry_cache["seq"] = seq
    _telemetry_cache["res"] = {
        "hex": raw_bytes.hex(sep=' ').upper(),
        "apid": packet.apid,
        "sequence_count": packet.sequence_count,
        "valid_crc": True 
    }

    res = dict(_telemetry_cache["res"])
    res["status"] = current_status
    return res

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


