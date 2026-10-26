"""Modelo de datos: pedidos."""

import enum
import uuid
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from meridian_orders.db import Base


class OrderStatus(enum.StrEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"


def _now() -> datetime:
    return datetime.now(UTC)


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    customer_name: Mapped[str] = mapped_column(String(200))
    customer_email: Mapped[str] = mapped_column(String(320))
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, name="order_status", values_callable=lambda e: [m.value for m in e]),
        default=OrderStatus.PENDING,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, onupdate=_now
    )
