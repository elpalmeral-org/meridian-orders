# Proposal

## Why

F6 del laboratorio (observabilidad y coste) pide que cada petición sea trazable en el obs-stack
compartido de la plataforma (ADR 0032, `agentic-platform-lab`). Hoy el servicio solo expone
`meridian_http_requests_total`/`meridian_http_request_seconds` (Prometheus, sin *scrape*
configurado todavía) y nada llega al colector OTel real que ya existe en `docker01`. Sin trazas,
depurar una petición lenta o un fallo intermitente en `orders-{dev,staging,prod}` exige leer logs a
mano, sin correlación entre servicios.

## What Changes

El backend emite trazas OTel (peticiones HTTP y consultas SQL) hacia el colector OTLP del obs-stack
(`http://192.168.0.6:4317`), con el entorno (`dev`/`staging`/`prod`) como atributo de recurso para
distinguirlos en el mismo *dashboard*. No cambia ningún contrato de la API ni el comportamiento
observable desde fuera del proceso: es observabilidad interna, no un endpoint ni un campo nuevo.

## Capabilities

### New Capabilities

(ninguna)

### Modified Capabilities

- `orders`: el requisito «Operabilidad» añade trazas OTel a la observabilidad ya exigida, con la
  misma garantía de no fuga de C3 que ya aplica al log de acceso y a `/metrics`.

## Impact

- `apps/backend/src/meridian_orders/otel.py`: nuevo módulo, instrumentación manual (no *zero-code*)
  de FastAPI y SQLAlchemy.
- `apps/backend/src/meridian_orders/main.py`: llama a `setup_otel` al construir la app.
- `apps/backend/pyproject.toml`/`uv.lock`: nuevas dependencias (`opentelemetry-sdk`,
  `opentelemetry-exporter-otlp`, instrumentadores de FastAPI y SQLAlchemy).
- `apps/backend/tests/test_platform.py`: escenario nuevo sobre la ausencia de fuga en las trazas.
- `platform-gitops`: `OTEL_SERVICE_NAME`/`OTEL_EXPORTER_OTLP_ENDPOINT`/`OTEL_RESOURCE_ATTRIBUTES`
  en la `ConfigMap` de cada entorno (sin secretos: la IP es de la LAN interna).
- Sin migración, sin endpoint nuevo, sin campo nuevo en la API.

## Grounding y cumplimiento

- `[[corpus/03-data-classification.md]] §2` — `GET /api/orders?customer_email=...` sigue siendo la
  única vía con un dato C3 en la query string. El instrumentador de FastAPI/ASGI la mete sin cifrar
  en `http.url`/`url.full` por defecto (comprobado contra el código real de
  `opentelemetry-instrumentation-asgi`, no asumido); un `server_request_hook` la sustituye por la
  ruta sin query string antes de que la traza salga del proceso — misma garantía estructural que ya
  existe para el log de acceso (`--no-access-log`) y los errores de SQLAlchemy
  (`hide_parameters=True`), no una lista negra de parámetros.
- `[[corpus/01-engineering-standards.md]] §4` — la instrumentación vive en su propio módulo
  (`otel.py`), no mezclada en `main.py` ni en el dominio.
- No hay Nota DPIA nueva: no cambia a quién llega el dato (sigue sin salir del proceso hacia
  destinos ajenos a la plataforma — el obs-stack es infraestructura propia del laboratorio, nunca
  recibe el valor real); ningún LLM interviene en esta ruta.
