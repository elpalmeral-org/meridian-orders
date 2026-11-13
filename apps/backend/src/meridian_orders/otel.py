"""Trazas OTel hacia el obs-stack de docker01 (F6.1, ADR 0032). Instrumentación manual, no
"zero-code" (opentelemetry-instrument): necesitamos un server_request_hook para sanear la URL
antes de instrumentation_app, y zero-code no permite pasar hooks."""

import os
from typing import Any

from fastapi import FastAPI
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, set_tracer_provider
from sqlalchemy import Engine


def _strip_query_string(span: Span, scope: dict[str, Any]) -> None:
    """GET /api/orders acepta customer_email (dato C3, corpus/03-data-classification.md §2) en
    la query string. El instrumentador la mete sin cifrar en http.url/url.full; no debe salir de
    la app hacia el obs-stack, igual que ya se evita en el log de acceso (--no-access-log) y en
    los errores de SQLAlchemy (hide_parameters, meridian_orders.db.get_engine)."""
    if not span.is_recording():
        return
    path = scope.get("path", "")
    for attribute in ("http.target", "http.url", "url.full"):
        span.set_attribute(attribute, path)
    span.set_attribute("url.query", "")


def setup_otel(app: FastAPI, engine: Engine) -> None:
    """No hace nada si OTEL_EXPORTER_OTLP_ENDPOINT no está puesto (tests, CI): solo dev/
    staging/prod lo traen vía ConfigMap (platform-gitops). Variable estándar del SDK de OTel,
    sin el prefijo MERIDIAN_ de meridian_orders.config: no es configuración de la app."""
    if not os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT"):
        return

    provider = TracerProvider(resource=Resource.create())
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    set_tracer_provider(provider)

    FastAPIInstrumentor.instrument_app(app, server_request_hook=_strip_query_string)
    SQLAlchemyInstrumentor().instrument(engine=engine)
