"""add shipments and tracking"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "c9d0e1f2a345"
down_revision: Union[str, None] = "b8c9d0e1f234"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "shipments",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("seller_order_id", sa.UUID(), nullable=False),
        sa.Column("provider", sa.String(), nullable=False, server_default="MOCK"),
        sa.Column("tracking_number", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="LABEL_CREATED"),
        sa.Column("estimated_delivery", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["seller_order_id"], ["seller_orders.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("seller_order_id"),
        sa.UniqueConstraint("tracking_number"),
    )

def downgrade() -> None:
    op.drop_table("shipments")