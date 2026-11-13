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

## Risks / Trade-offs

- [Sin índice en `customer_email`] → Aceptable: la tabla de un demo no tiene volumen que lo
  justifique; si se necesitara, sería un cambio de rendimiento aparte, no de esta propuesta.
