# Spec Delta

## MODIFIED Requirements

### Requirement: Consulta de pedidos

El sistema MUST permitir consultar un pedido por su identificador y listar pedidos ordenados del
más reciente al más antiguo, con filtro opcional por estado, filtro opcional por correo exacto del
cliente (sin distinguir mayúsculas/minúsculas) y paginación (`limit` 1-100, `offset`). Los filtros
de estado y correo se combinan con AND cuando se usan a la vez.

#### Scenario: Pedido existente

- **WHEN** se pide `GET /api/orders/{id}` de un pedido que existe
- **THEN** se responde `200` con el pedido

#### Scenario: Pedido inexistente

- **WHEN** se pide un `id` que no existe
- **THEN** se responde `404`

#### Scenario: Filtro por estado

- **WHEN** se pide `GET /api/orders?status=confirmed`
- **THEN** solo se devuelven pedidos en estado `confirmed` y `total` cuenta solo esos

#### Scenario: Filtro por correo del cliente

- **WHEN** se pide `GET /api/orders?customer_email=compras@acme.example` y hay pedidos de ese
  cliente y de otros
- **THEN** solo se devuelven los pedidos cuyo `customer_email` coincide exactamente (ignorando
  mayúsculas/minúsculas) y `total` cuenta solo esos

#### Scenario: Filtro por correo sin coincidencias

- **WHEN** se pide `GET /api/orders?customer_email=nadie@ejemplo.example` y ningún pedido tiene ese
  correo
- **THEN** se responde `200` con `items` vacío y `total: 0`

#### Scenario: Correo con formato inválido en el filtro

- **WHEN** se pide `GET /api/orders?customer_email=no-es-un-email`
- **THEN** se responde `422` y no se filtra nada
