"""Esquemas de entrada y salida de la API."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from meridian_orders.models import OrderStatus

Email = Annotated[
    str,
    StringConstraints(strip_whitespace=True, max_length=320, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$"),
]
Currency = Annotated[str, StringConstraints(pattern=r"^[A-Z]{3}$")]


class OrderCreate(BaseModel):
    customer_name: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)
    ]
    customer_email: Email
    total_amount: Annotated[Decimal, Field(gt=0, max_digits=12, decimal_places=2)]
    currency: Currency = "EUR"


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    customer_name: str
    customer_email: str
    total_amount: Decimal
    currency: str
    status: OrderStatus
    created_at: datetime
    updated_at: datetime


class OrderList(BaseModel):
    items: list[OrderRead]
    total: int
