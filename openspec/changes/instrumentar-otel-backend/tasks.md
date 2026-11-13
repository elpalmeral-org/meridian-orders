# Tasks

## 1. Instrumentación OTel del backend

- [x] 1.1 Nuevo módulo `meridian_orders/otel.py` con `setup_otel(app, engine)`: `TracerProvider` +
  `BatchSpanProcessor(OTLPSpanExporter())`, `FastAPIInstrumentor.instrument_app` con
  `server_request_hook`, `SQLAlchemyInstrumentor().instrument(engine=...)`. No hace nada si
  `OTEL_EXPORTER_OTLP_ENDPOINT` no está en el entorno.
- [x] 1.2 `main.py` llama a `setup_otel(app, get_engine())` al construir la app.
- [x] 1.3 Dependencias nuevas en `pyproject.toml`/`uv.lock` (`opentelemetry-exporter-otlp`,
  `opentelemetry-instrumentation-fastapi`, `opentelemetry-instrumentation-sqlalchemy`).

## 2. Sin fuga de C3 en las trazas

- [x] 2.1 `_strip_query_string` sustituye `http.target`/`http.url`/`url.full` por la ruta sin query
  string y vacía `url.query`. Verificar con `test_strip_query_string_removes_customer_email`
  (`customer_email` en la URL de entrada, ausente del span resultante).

## 3. Configuración por entorno

- [x] 3.1 `platform-gitops`: `OTEL_SERVICE_NAME`/`OTEL_EXPORTER_OTLP_ENDPOINT` en la `ConfigMap`
  base; `OTEL_RESOURCE_ATTRIBUTES=environment=<entorno>` en cada *overlay* (`dev`/`staging`/`prod`).

## Workflow follow-up

- Archivar este cambio cuando se fusione el PR de código (puerta 2) y se compruebe de verdad
  (ClickHouse/Grafana) que las trazas de `orders-dev` llegan sin `customer_email`.
