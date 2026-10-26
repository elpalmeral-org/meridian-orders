"""Reglas de negocio de los pedidos."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from meridian_orders.models import Order, OrderStatus
from meridian_orders.schemas import OrderCreate

# Máquina de estados: qué transiciones están permitidas desde cada estado.
ALLOWED_TRANSITIONS: dict[OrderStatus, frozenset[OrderStatus]] = {
    OrderStatus.PENDING: frozenset({OrderStatus.CONFIRMED, OrderStatus.CANCELLED}),
    OrderStatus.CONFIRMED: frozenset({OrderStatus.SHIPPED, OrderStatus.CANCELLED}),
    OrderStatus.SHIPPED: frozenset(),
    OrderStatus.CANCELLED: frozenset(),
}


class OrderNotFoundError(Exception):
    pass


class InvalidTransitionError(Exception):
    def __init__(self, current: OrderStatus, target: OrderStatus) -> None:
        super().__init__(f"No se puede pasar de '{current}' a '{target}'")
        self.current = current
        self.target = target


def create_order(session: Session, data: OrderCreate) -> Order:
    order = Order(**data.model_dump())
    session.add(order)
    session.commit()
    session.refresh(order)
    return order


def list_orders(
    session: Session, status: OrderStatus | None, limit: int, offset: int
) -> tuple[list[Order], int]:
    query = select(Order)
    count = select(func.count()).select_from(Order)
    if status is not None:
        query = query.where(Order.status == status)
        count = count.where(Order.status == status)
    query = query.order_by(Order.created_at.desc()).limit(limit).offset(offset)
    return list(session.scalars(query)), session.scalar(count) or 0


def get_order(session: Session, order_id: uuid.UUID) -> Order:
    order = session.get(Order, order_id)
    if order is None:
        raise OrderNotFoundError(str(order_id))
    return order


def change_status(session: Session, order_id: uuid.UUID, target: OrderStatus) -> Order:
    order = get_order(session, order_id)
    if target not in ALLOWED_TRANSITIONS[order.status]:
        raise InvalidTransitionError(order.status, target)
    order.status = target
    session.commit()
    session.refresh(order)
    return order
