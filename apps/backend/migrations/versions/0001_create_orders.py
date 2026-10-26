"""Crear la tabla de pedidos.

Revision ID: 0001
Revises:
Create Date: 2026-10-26
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

order_status = sa.Enum("pending", "confirmed", "shipped", "cancelled", name="order_status")


def upgrade() -> None:
    op.create_table(
        "orders",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("customer_name", sa.String(200), nullable=False),
        sa.Column("customer_email", sa.String(320), nullable=False),
        sa.Column("total_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("status", order_status, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_orders_status", "orders", ["status"])


def downgrade() -> None:
    op.drop_index("ix_orders_status", table_name="orders")
    op.drop_table("orders")
    order_status.drop(op.get_bind(), checkfirst=True)
