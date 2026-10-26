"""Rutas HTTP de pedidos (montadas bajo /api)."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from meridian_orders import service
from meridian_orders.db import get_session
from meridian_orders.models import OrderStatus
from meridian_orders.schemas import OrderCreate, OrderList, OrderRead, OrderStatusUpdate

router = APIRouter(prefix="/api/orders", tags=["orders"])
SessionDep = Annotated[Session, Depends(get_session)]


@router.get("", response_model=OrderList)
def list_orders(
    session: SessionDep,
    status_filter: Annotated[OrderStatus | None, Query(alias="status")] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> OrderList:
    items, total = service.list_orders(session, status_filter, limit, offset)
    return OrderList(items=[OrderRead.model_validate(o) for o in items], total=total)


@router.post("", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order(session: SessionDep, data: OrderCreate) -> OrderRead:
    return OrderRead.model_validate(service.create_order(session, data))


@router.get("/{order_id}", response_model=OrderRead)
def get_order(session: SessionDep, order_id: uuid.UUID) -> OrderRead:
    try:
        return OrderRead.model_validate(service.get_order(session, order_id))
    except service.OrderNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Pedido no encontrado") from exc


@router.patch("/{order_id}/status", response_model=OrderRead)
def change_status(session: SessionDep, order_id: uuid.UUID, data: OrderStatusUpdate) -> OrderRead:
    try:
        return OrderRead.model_validate(service.change_status(session, order_id, data.status))
    except service.OrderNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Pedido no encontrado") from exc
    except service.InvalidTransitionError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc
