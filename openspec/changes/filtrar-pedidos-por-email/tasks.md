# Tasks

## 1. Filtro por correo en el servicio de dominio

- [ ] 1.1 Añadir el parámetro `customer_email: Email | None` a `service.list_orders`, filtrando
  con `func.lower(Order.customer_email) == customer_email.lower()` cuando se pasa, combinado con
  el filtro de `status` existente. Verificar con `test_list_orders_filters_by_customer_email`
  (coincidencia, sin coincidencias, combinado con `status`).

## 2. Parámetro de consulta en la API

- [ ] 2.1 Añadir el parámetro de consulta opcional `customer_email` (tipo `Email` de
  `schemas.py`) a `GET /api/orders` en `api.py`, pasándolo a `service.list_orders`. Verificar con
  `test_list_orders_rejects_invalid_customer_email_filter` (`422` con un correo sin formato
  válido).

## Workflow follow-up

- Archivar el cambio cuando se fusione el PR de código (puerta 2).
