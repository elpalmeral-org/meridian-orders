# Spec Delta

## MODIFIED Requirements

### Requirement: Operabilidad

El servicio MUST exponer `/healthz` (proceso vivo), `/readyz` (base de datos accesible) y
`/metrics` en formato Prometheus con peticiones y latencias por ruta, sin incluir identificadores
de pedido en las etiquetas. El servicio MUST emitir trazas OTel de peticiones HTTP y consultas SQL
hacia el colector configurado, sin que la query string de la petición llegue a ninguna traza.

#### Scenario: Base de datos caída

- **WHEN** la base de datos no responde
- **THEN** `/readyz` responde `503` y `/healthz` sigue respondiendo `200`

#### Scenario: El correo del cliente nunca queda en claro en las trazas

- **WHEN** se pide `GET /api/orders?customer_email=compras@acme.example` con las trazas OTel
  activas
- **THEN** ningún atributo de la traza resultante contiene el valor del correo ni la query string
  completa de la petición
