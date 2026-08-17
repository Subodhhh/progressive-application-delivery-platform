import os
import socket
import time
from fastapi import FastAPI, Response

app = FastAPI(title="ReleaseForge Demo App")

# Version is injected via env var so we can build v1.0, v1.1, v1.2 etc.
# without changing code every time.
VERSION = os.getenv("APP_VERSION", "v1.0")
ENVIRONMENT = os.getenv("APP_ENV", "local")

# Simple in-memory counter to prove request routing/traffic splitting works
request_count = 0

# Toggle to simulate a broken release (used in failure-injection demo)
SIMULATE_FAILURE = os.getenv("SIMULATE_FAILURE", "false").lower() == "true"


@app.get("/")
def root():
    global request_count
    request_count += 1
    return {
        "message": "ReleaseForge Demo Application",
        "version": VERSION,
        "hostname": socket.gethostname(),
        "environment": ENVIRONMENT,
        "request_count": request_count,
    }


@app.get("/version")
def version():
    return {"version": VERSION}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/payment")
def payment(response: Response):
    global request_count
    request_count += 1

    if SIMULATE_FAILURE:
        import random

        if random.random() < 0.3:
            response.status_code = 500
            return {"status": "error", "message": "payment processing failed"}

    time.sleep(0.05)
    return {"status": "success", "version": VERSION}


@app.get("/metrics-info")
def metrics_info():
    return {"request_count": request_count, "version": VERSION}