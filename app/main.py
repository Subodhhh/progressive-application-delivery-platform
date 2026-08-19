import os
import socket
import time
from fastapi import FastAPI, Response, Request
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI(title="ReleaseForge Demo App")

# --- Manual Prometheus instrumentation ---
# We instrument manually instead of using prometheus-fastapi-instrumentator
# because that library hard-pins starlette<1.0.0, which conflicts with the
# patched starlette version we need for known CVEs (see requirements.txt).

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status_code"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
)


@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    path = request.url.path
    REQUEST_COUNT.labels(
        method=request.method,
        path=path,
        status_code=response.status_code,
    ).inc()
    REQUEST_LATENCY.labels(method=request.method, path=path).observe(duration)

    return response


@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


# Version is injected via env var so we can build v1.0, v1.1, v1.2 etc.
# without changing code every time.
VERSION = os.getenv("APP_VERSION", "v2.0")
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