"""add outbox processing state

Revision ID: f4d2a9e6c701
Revises: c112b3ac0313
Create Date: 2026-09-17
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "f4d2a9e6c701"
down_revision: Union[str, None] = "c112b3ac0313"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("outbox_events", sa.Column("status", sa.String(), nullable=False, server_default="PENDING"))
    op.add_column("outbox_events", sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("outbox_events", sa.Column("max_attempts", sa.Integer(), nullable=False, server_default="5"))
    op.add_column(
        "outbox_events",
        sa.Column("available_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.add_column("outbox_events", sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("outbox_events", sa.Column("last_error", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("outbox_events", "last_error")
    op.drop_column("outbox_events", "processed_at")
    op.drop_column("outbox_events", "available_at")
    op.drop_column("outbox_events", "max_attempts")
    op.drop_column("outbox_events", "attempt_count")
    op.drop_column("outbox_events", "status")