"""add user clicker state

Revision ID: 20260429_0016
Revises: 20260429_0015
Create Date: 2026-04-29
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260429_0016"
down_revision = "20260429_0015"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("clicker_energy", sa.Integer(), nullable=False, server_default="1200"))
    op.add_column(
        "users",
        sa.Column("clicker_energy_updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.add_column("users", sa.Column("clicker_progress", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("users", sa.Column("clicker_daily_rolls", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("users", sa.Column("clicker_daily_reset_date", sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "clicker_daily_reset_date")
    op.drop_column("users", "clicker_daily_rolls")
    op.drop_column("users", "clicker_progress")
    op.drop_column("users", "clicker_energy_updated_at")
    op.drop_column("users", "clicker_energy")
