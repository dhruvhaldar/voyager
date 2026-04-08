import time
import requests
import multiprocessing
import uvicorn
from fastapi import FastAPI
import threading

app = FastAPI()

@app.get("/sync")
def sync_endpoint():
    return {"status": "ok"}

@app.get("/async")
async def async_endpoint():
    return {"status": "ok"}

def run_server():
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="critical")

if __name__ == "__main__":
    server_process = multiprocessing.Process(target=run_server)
    server_process.start()
    time.sleep(2) # wait for server to start

    # benchmark sync
    start = time.time()
    for _ in range(1000):
        requests.get("http://127.0.0.1:8001/sync")
    sync_time = time.time() - start

    # benchmark async
    start = time.time()
    for _ in range(1000):
        requests.get("http://127.0.0.1:8001/async")
    async_time = time.time() - start

    print(f"Sync time: {sync_time:.4f}s")
    print(f"Async time: {async_time:.4f}s")

    server_process.terminate()
    server_process.join()
