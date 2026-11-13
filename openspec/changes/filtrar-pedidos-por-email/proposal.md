# Proposal

## Why

Atención al cliente necesita encontrar los pedidos de un cliente concreto sin conocer su `id`. Hoy
`GET /api/orders` solo filtra por `status`; buscar por `customer_email` obliga a paginar a mano por
todo el listado.

## What Changes

`GET /api/orders` admite un parámetro opcional `customer_email` que filtra por coincidencia exacta
(normalizada a minúsculas, igual que al crear el pedido). Combina con el filtro `status` existente
(AND) y con la paginación actual. No se introduce ningún campo, tabla ni endpoint nuevo: es una
capacidad de consulta más sobre un dato que el pedido ya guarda.

## Capabilities

### New Capabilities

(ninguna)

### Modified Capabilities

- `orders`: el requisito «Consulta de pedidos» añade un escenario de filtro por `customer_email`.

## Impact

- `apps/backend/src/meridian_orders/api.py`: nuevo parámetro de consulta en `list_orders`.
- `apps/backend/src/meridian_orders/service.py`: `list_orders` filtra también por `customer_email`.
- `apps/backend/tests/test_orders.py`: escenarios nuevos.
- Sin migración: `customer_email` ya es una columna de `orders`.

## Grounding y cumplimiento

- `[[corpus/01-engineering-standards.md]] §4` — el filtro vive en `service.list_orders` (dominio),
  no en el *router*; consecuencia: `api.py` solo añade el parámetro y lo pasa, sin lógica.
- `[[corpus/01-engineering-standards.md]] §6` — cada escenario nuevo trae su test; consecuencia:
  tests parametrizados junto a los de `status` ya existentes, mismo fichero.
- `[[corpus/03-data-classification.md]] §1-§3` — `customer_email` es dato personal directamente
  identificativo, igual de sensible que `customer_name` (ya clasificado C3 en el corpus):
  consecuencia, se trata como **C3**. No hay Nota DPIA: no se introduce un campo, un almacenamiento
  ni un destinatario nuevo — se añade una vía de consulta de solo lectura sobre un dato que el
  sistema ya almacena y ya devuelve en cada pedido individual; la finalidad (buscar pedidos de un
  cliente) es la misma para la que se recogió el dato. No cambia a quién llega el dato (sigue sin
  salir de la respuesta HTTP de la propia API), así que no hay un "modelo nuevo que lo reciba"
  (`[[corpus/03-data-classification.md]] §4`): ningún LLM interviene en esta ruta.
- `[[corpus/02-security-baseline.md]] §3` — entrada validada en la frontera: se reutiliza el tipo
  `Email` ya existente en `schemas.py` para el parámetro de consulta, no una cadena libre.
- `[[corpus/02-security-baseline.md]] §4` — no es un endpoint nuevo: el ya existente `GET
  /api/orders` no tenía autorización antes de este cambio (fuera de alcance de esta propuesta).
