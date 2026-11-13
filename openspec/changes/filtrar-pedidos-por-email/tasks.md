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

## 3. Sin fuga de C3 en los registros de la aplicación

- [ ] 3.1 `apps/backend/src/meridian_orders/db.py`: `create_engine(..., hide_parameters=True)` en
  las dos ramas de `get_engine`. Verificar con un test que fuerza un error de BD filtrando por
  `customer_email` y comprueba que el mensaje de la excepción no contiene el valor del correo.
- [ ] 3.2 `apps/backend/Dockerfile`: añadir `--no-access-log` al `CMD` de `uvicorn`. Verificar
  leyendo el `CMD` resultante (no hay forma de probar en pytest que el proceso real no escriba el
  log; se verifica el argumento, no el comportamiento del proceso).

## Workflow follow-up

- Archivar el cambio cuando se fusione el PR de código (puerta 2).
