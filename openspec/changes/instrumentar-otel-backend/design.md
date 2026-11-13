# Design

## Context

El obs-stack real ya existe en `docker01` (ClickHouse + OTel Collector + Grafana + Prometheus,
`homelab-containers/obs-stack`) y ya tiene un precedente de integración (`ai-stack/
OBSERVABILITY.md`, Open WebUI por *push* OTLP nativo). ADR 0032 (`agentic-platform-lab`) decide
reutilizarlo tal cual, sin desplegar nada nuevo, y descarta Langfuse (ya evaluado y rechazado por
sus requisitos de infraestructura propia). Conectividad LAN desde la red de *pods* de k3s01 hacia
el colector (`192.168.0.6:4317`) verificada de verdad con un *pod* efímero de diagnóstico antes de
escribir este cambio: `HTTP 200`.

## Goals / Non-Goals

**Goals:**
- Trazas de peticiones HTTP y consultas SQL, visibles en el mismo obs-stack que ya usa el resto del
  homelab.
- Ninguna fuga nueva de datos C3 (`customer_email`) hacia un sistema fuera del proceso.

**Non-Goals:**
- Métricas o logs vía OTel: esta propuesta es solo trazas. `/metrics` (Prometheus) sigue igual.
- Un *dashboard* de Grafana dedicado: el obs-stack ya permite explorar trazas por `service.name`
  contra ClickHouse sin un *dashboard* nuevo; añadir uno es un cambio de infraestructura de
  `docker01`, fuera de alcance de este repo.
- El puente HarnessRouter → OTel: diferido hasta F4.7 (ADR 0032), no hay ninguna ejecución real del
  motor A que trazar todavía.

## Decisions

- **Instrumentación manual, no *zero-code* (`opentelemetry-instrument`).** El mecanismo *zero-code*
  no permite pasar un `server_request_hook` personalizado — y ese *hook* es imprescindible (ver
  más abajo). Alternativa descartada: `opentelemetry-bootstrap -a install` en el `Dockerfile`; no
  aporta nada aquí porque de todos modos hace falta código propio para el *hook*, y las
  dependencias de instrumentación ya declaradas a mano (`opentelemetry-instrumentation-fastapi`,
  `opentelemetry-instrumentation-sqlalchemy`) son suficientes para que `FastAPIInstrumentor`/
  `SQLAlchemyInstrumentor` encuentren todo lo que necesitan sin ese paso.
- **`server_request_hook` que sustituye `http.target`/`http.url`/`url.full` por la ruta sin query
  string, y vacía `url.query`.** Verificado contra el código real de
  `opentelemetry-instrumentation-asgi` (`collect_request_attributes`): por defecto, la query string
  decodificada se concatena a `http.url`/`url.full` sin ninguna opción para desactivarlo aparte de
  un *hook*. La alternativa de enmascarar solo `customer_email` con una expresión regular se
  descartó por el mismo motivo que ya se descartó en `filtrar-pedidos-por-email` (ver ese
  `design.md` archivado): es una lista negra que falla en abierto ante cualquier grafía no
  anticipada. Aquí se va más lejos que en esa propuesta: no se intenta reconocer el parámetro
  sensible, se quita la query string entera — cualquier parámetro que se añada en el futuro queda
  cubierto sin tocar este código.
- **`SQLAlchemyInstrumentor` sin *hook* adicional.** Su atributo `db.statement` es la consulta
  compilada con marcadores de posición (`:customer_email`), no los valores enlazados — mismo motivo
  por el que `hide_parameters=True` ya protege los mensajes de error: SQLAlchemy no mete valores en
  el texto de la consulta en ningún caso que no sea el de una excepción.
- **`setup_otel` no hace nada si `OTEL_EXPORTER_OTLP_ENDPOINT` no está en el entorno** (tests, CI):
  variable estándar del SDK de OTel, no una opción de `meridian_orders.config` — no lleva el
  prefijo `MERIDIAN_`, a propósito, para no inventar una capa de configuración que el SDK ya trae.
- **`OTEL_RESOURCE_ATTRIBUTES=environment=<entorno>`, no `deployment.environment`.** El procesador
  `resource` del colector compartido (`homelab-containers/obs-stack/otel-collector/config.yaml`)
  hace `upsert` de `deployment.environment=production` sobre **toda** la telemetría que recibe, sin
  distinguir origen — usar esa misma clave haría que las trazas de `orders-dev`/`orders-staging`
  aparecieran como `production`. Verificado leyendo la configuración real del colector, no asumido.
- **Sin `OTEL_EXPORTER_OTLP_INSECURE`.** El exportador gRPC de Python detecta por sí solo que un
  `endpoint` con esquema `http://` es sin TLS (comprobado en el código real del paquete); fijar la
  variable sería redundante.

## Risks / Trade-offs

- [Sin *dashboard* dedicado todavía] → Aceptable para esta propuesta: las trazas ya llegan y se
  pueden explorar; un *dashboard* específico es trabajo de `docker01`/`homelab-containers`, con su
  propio ciclo de cambio, no de este repo.
- [Coste de memoria del *pod*] → El SDK de OTel y el cliente gRPC añaden un consumo modesto; los
  límites actuales (`backend.yaml`, 256Mi) no se tocan de forma preventiva sin evidencia real tras
  el despliegue.
