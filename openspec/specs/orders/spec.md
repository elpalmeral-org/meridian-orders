# orders Specification

## Purpose

Gestión del ciclo de vida de los pedidos de Meridian Orders: alta, consulta y cambios de estado,
expuestos en la API `/api/orders` y en el panel web.

## Requirements

### Requirement: Alta de pedidos

El sistema MUST permitir crear un pedido con cliente, correo de contacto e importe, y MUST
asignarle el estado `pending`. La moneda por defecto MUST ser `EUR`.

#### Scenario: Pedido válido

- **WHEN** se envía `POST /api/orders` con `customer_name`, `customer_email` válido y `total_amount` mayor que 0
- **THEN** se responde `201` con el pedido creado, su `id`, `status: pending` y `currency: EUR`

#### Scenario: Datos inválidos

- **WHEN** el importe es 0 o negativo, el correo no tiene formato válido, el nombre está vacío o la moneda no son 3 letras mayúsculas
- **THEN** se responde `422` y no se crea ningún pedido

### Requirement: Consulta de pedidos

El sistema MUST permitir consultar un pedido por su identificador y listar pedidos ordenados del
más reciente al más antiguo, con filtro opcional por estado y paginación (`limit` 1-100, `offset`).

#### Scenario: Pedido existente

- **WHEN** se pide `GET /api/orders/{id}` de un pedido que existe
- **THEN** se responde `200` con el pedido

#### Scenario: Pedido inexistente

- **WHEN** se pide un `id` que no existe
- **THEN** se responde `404`

#### Scenario: Filtro por estado

- **WHEN** se pide `GET /api/orders?status=confirmed`
- **THEN** solo se devuelven pedidos en estado `confirmed` y `total` cuenta solo esos

### Requirement: Ciclo de vida del pedido

El sistema MUST aplicar esta máquina de estados y MUST rechazar cualquier otra transición:
`pending → confirmed | cancelled`, `confirmed → shipped | cancelled`; `shipped` y `cancelled` son
estados finales.

#### Scenario: Transición permitida

- **WHEN** se envía `PATCH /api/orders/{id}/status` con un estado permitido desde el actual
- **THEN** se responde `200` y el pedido queda en el nuevo estado

#### Scenario: Transición prohibida

- **WHEN** se intenta enviar un pedido `pending`, cancelar uno `shipped`, reabrir uno `cancelled` o volver a `pending`
- **THEN** se responde `409` con un mensaje que explica la transición rechazada y el pedido no cambia

### Requirement: Panel web de pedidos

El panel MUST mostrar los pedidos con cliente, importe formateado en la moneda del pedido, estado e
instante de creación, y MUST ofrecer únicamente las acciones permitidas por la máquina de estados.

#### Scenario: Acciones según estado

- **WHEN** se muestra un pedido `pending`
- **THEN** aparecen las acciones Confirmar y Cancelar, y no aparece Enviar

#### Scenario: Error de la API

- **WHEN** la API rechaza una acción
- **THEN** el panel muestra el motivo devuelto por la API

### Requirement: Operabilidad

El servicio MUST exponer `/healthz` (proceso vivo), `/readyz` (base de datos accesible) y
`/metrics` en formato Prometheus con peticiones y latencias por ruta, sin incluir identificadores
de pedido en las etiquetas.

#### Scenario: Base de datos caída

- **WHEN** la base de datos no responde
- **THEN** `/readyz` responde `503` y `/healthz` sigue respondiendo `200`
