"""Aplicación FastAPI: API, salud y métricas."""

import time
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from sqlalchemy import text

from meridian_orders import __version__, api
from meridian_orders.config import get_settings
from meridian_orders.db import get_engine

REQUESTS = Counter("meridian_http_requests_total", "Peticiones HTTP", ["method", "route", "status"])
LATENCY = Histogram("meridian_http_request_seconds", "Latencia HTTP", ["method", "route"])

app = FastAPI(
    title="Meridian Orders API",
    version=__version__,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)
app.include_router(api.router)


@app.middleware("http")
async def metrics_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    start = time.perf_counter()
    response = await call_next(request)
    route = request.scope.get("route")
    path = getattr(route, "path", "unmatched")
    LATENCY.labels(request.method, path).observe(time.perf_counter() - start)
    REQUESTS.labels(request.method, path, str(response.status_code)).inc()
    return response


@app.get("/healthz", include_in_schema=False)
def healthz() -> dict[str, str]:
    """Vivo: el proceso responde (no comprueba dependencias)."""
    return {"status": "ok"}


@app.get("/readyz", include_in_schema=False)
def readyz() -> Response:
    """Listo: la base de datos responde."""
    try:
        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:  # cualquier fallo de BD significa "no listo"
        return JSONResponse({"status": "unavailable"}, status_code=503)
    return JSONResponse({"status": "ok"})


@app.get("/api/info")
def info() -> dict[str, str]:
    return {"version": __version__, "environment": get_settings().environment}


@app.get("/metrics", include_in_schema=False)
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
