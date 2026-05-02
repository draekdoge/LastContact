"""invite_boosts.consumed_at — синхронизация с ORM

Revision ID: 20260502_0018
Revises: 20260430_0017
Create Date: 2026-05-02
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260502_0018"
down_revision = "20260430_0017"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "invite_boosts",
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("invite_boosts", "consumed_at")
