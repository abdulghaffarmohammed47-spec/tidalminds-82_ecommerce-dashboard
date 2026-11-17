"""add return uniqueness and reason"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "d0e1f2a3b456"
down_revision: Union[str, None] = "c9d0e1f2a345"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column("returns", sa.Column("reason", sa.String(), nullable=True))
    op.create_unique_constraint("uq_return_seller_order", "returns", ["seller_order_id"])

def downgrade() -> None:
    op.drop_constraint("uq_return_seller_order", "returns", type_="unique")
    op.drop_column("returns", "reason")