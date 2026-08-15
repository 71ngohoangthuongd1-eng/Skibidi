"""add bought_goods.payment_id for exactly-once SePay item delivery

Revision ID: 7d0a4e8b2c9f
Revises: e5f6a7b8c9d0
Create Date: 2026-08-15

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = "7d0a4e8b2c9f"
down_revision: Union[str, None] = "e5f6a7b8c9d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_exists(conn, table_name: str, column_name: str) -> bool:
    insp = inspect(conn)
    if table_name not in insp.get_table_names():
        return False
    return any(c["name"] == column_name for c in insp.get_columns(table_name))


def upgrade() -> None:
    conn = op.get_bind()
    if _column_exists(conn, "bought_goods", "payment_id"):
        return

    op.add_column(
        "bought_goods",
        sa.Column("payment_id", sa.Integer, sa.ForeignKey("payments.id", ondelete="SET NULL"), nullable=True),
    )
    op.create_index("ix_bought_goods_payment_id", "bought_goods", ["payment_id"], unique=False)
    op.create_unique_constraint("uq_bought_goods_payment_id", "bought_goods", ["payment_id"])


def downgrade() -> None:
    conn = op.get_bind()
    if not _column_exists(conn, "bought_goods", "payment_id"):
        return

    op.drop_constraint("uq_bought_goods_payment_id", "bought_goods", type_="unique")
    op.drop_index("ix_bought_goods_payment_id", table_name="bought_goods")
    op.drop_column("bought_goods", "payment_id")