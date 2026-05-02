"""users: timer_history jsonb

Revision ID: 20260424_0008
Revises: 20260422_0007
Create Date: 2026-04-24
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "20260424_0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "timer_history",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="Последние 3 события роста таймера [{delta_h, reason, ts}]",
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "timer_history")
