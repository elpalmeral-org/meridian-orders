# Design

## Context

`service.list_orders` ya construye la consulta con SQLAlchemy a partir de un filtro opcional de
`status`; `api.py` solo traduce los parámetros de consulta y delega. Ver `proposal.md` - Why.

## Goals / Non-Goals

**Goals:**
- Filtrar por `customer_email` con coincidencia exacta, insensible a mayúsculas/minúsculas.
- Combinarlo con el filtro de `status` y la paginación existentes, sin tocar su comportamiento.

**Non-Goals:**
- Búsqueda parcial o por otros campos (nombre, importe, fechas): no lo pide esta propuesta.
- Autorización del endpoint: ya es una carencia preexistente, fuera de alcance (`proposal.md` -
  Grounding).

## Decisions

- **Coincidencia exacta e insensible a mayúsculas, no `LIKE`.** `customer_email` ya se guarda
  normalizado a minúsculas al crear el pedido (`Email` en `schemas.py` con `strip_whitespace`, y
  Pydantic no fuerza minúsculas — lo confirma `conftest.py`/el modelo: se compara con
  `func.lower()` en la consulta en vez de asumir que el dato ya está en minúsculas, por si entraron
  filas antes de esta propuesta). Alternativa descartada: `ILIKE` con comodines — abre a búsqueda
  parcial, que es un *Non-Goal* y cambia el contrato de la API más de lo que pide esta propuesta.
- **El parámetro reutiliza el tipo `Email` de `schemas.py`**, no un `str` libre: así un correo con
  formato inválido da `422` en la frontera (Pydantic), igual que en la creación del pedido, sin
  lógica de validación nueva.
- **El filtro vive en `service.list_orders`**, como el de `status`: `api.py` solo añade el
  parámetro de consulta y lo pasa.
- **Sin log de acceso de uvicorn** (`CMD` del `Dockerfile` añade `--no-access-log`), en vez de
  enmascarar `customer_email` dentro de él. Un `logging.Filter` que reescribe el *record* de
  `uvicorn.access` se probó y se descartó: **no cierra la vía**, solo la tapa parcialmente —
  Starlette decodifica el parámetro de consulta sin distinguir mayúsculas ni *percent-encoding* del
  propio nombre (`customer%5Femail=...` sigue resolviendo a `customer_email`), así que cualquier
  grafía que el filtro no anticipe pasa de largo. Enmascarar **después** de que el dato ya está en
  camino de escribirse en un log es, en la práctica, una lista negra que falla en abierto; no
  enmascara «en la frontera» (`corpus/03-data-classification.md §2`). La observabilidad de
  peticiones que daba el log de acceso ya la cubre `meridian_http_requests_total`
  (`main.py`, Prometheus): método, ruta (plantilla, sin *query string*) y estado — suficiente para
  lo que hoy consume el *obs-stack* de la plataforma.
- **Motor de SQLAlchemy con `hide_parameters=True`** (`db.py`, `create_engine`). Si una consulta
  falla, SQLAlchemy incluye por defecto los valores de los parámetros enlazados en el mensaje de la
  excepción — `customer_email` entre ellos — que terminaría en el logger de errores de la
  aplicación. `hide_parameters=True` sustituye esos valores por `'[SQL parameters hidden due to
  hide_parameters=True]'` sin perder el resto del mensaje de diagnóstico (la consulta en sí, sin
  datos). Coste aceptado: depurar un fallo real de BD en desarrollo exige reproducirlo con
  `hide_parameters=False` a propósito; no hay alternativa que cierre la fuga de otro modo sin
  envolver cada llamada a la BD en su propio `try/except` (más superficie, más fácil de olvidar en
  el próximo filtro por un campo C3).

## Risks / Trade-offs

- [Sin índice en `customer_email`] → Aceptable: la tabla de un demo no tiene volumen que lo
  justifique; si se necesitara, sería un cambio de rendimiento aparte, no de esta propuesta.
