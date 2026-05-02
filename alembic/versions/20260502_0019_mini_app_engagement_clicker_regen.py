"""mini app engagement + network regen counters

Revision ID: 0019
Revises: 0018
Create Date: 2026-05-02

"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260502_0019"
down_revision = "20260502_0018"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("mini_app_first_seen_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("direct_mini_engaged_count", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "users",
        sa.Column("subtree_mini_engaged_count", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index(
        "ix_users_mini_app_first_seen_at",
        "users",
        ["mini_app_first_seen_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_users_mini_app_first_seen_at", table_name="users")
    op.drop_column("users", "subtree_mini_engaged_count")
    op.drop_column("users", "direct_mini_engaged_count")
    op.drop_column("users", "mini_app_first_seen_at")
