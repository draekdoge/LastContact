"""mini_app last_seen, invite temp regen window, cached online counts for regen

Revision ID: 20260502_0020
Revises: 20260502_0019
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260502_0020"
down_revision = "20260502_0019"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("mini_app_last_seen_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("invite_regen_boost_ends_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("mini_regen_online_direct", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "users",
        sa.Column("mini_regen_online_subtree", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index(
        "ix_users_mini_app_last_seen_at",
        "users",
        ["mini_app_last_seen_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_users_mini_app_last_seen_at", table_name="users")
    op.drop_column("users", "mini_regen_online_subtree")
    op.drop_column("users", "mini_regen_online_direct")
    op.drop_column("users", "invite_regen_boost_ends_at")
    op.drop_column("users", "mini_app_last_seen_at")
