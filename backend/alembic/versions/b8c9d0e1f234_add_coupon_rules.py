"""add coupon rules

Revision ID: b8c9d0e1f234
Revises: a7b8c9d0e123
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "b8c9d0e1f234"
down_revision: Union[str, None] = "a7b8c9d0e123"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("coupons", sa.Column("discount_type", sa.String(), nullable=False, server_default="PERCENTAGE"))
    op.add_column("coupons", sa.Column("discount_value", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("coupons", sa.Column("min_order_amount", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("coupons", sa.Column("max_discount_amount", sa.Integer(), nullable=True))
    op.add_column("coupons", sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("coupons", "expires_at")
    op.drop_column("coupons", "max_discount_amount")
    op.drop_column("coupons", "min_order_amount")
    op.drop_column("coupons", "discount_value")
    op.drop_column("coupons", "discount_type")