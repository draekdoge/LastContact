"""add invite clicker economy

Revision ID: 20260430_0017
Revises: 20260429_0016
Create Date: 2026-04-30
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "20260430_0017"
down_revision = "20260429_0016"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("clicker_max_energy_bonus", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("users", sa.Column("clicker_regen_bonus_bps", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("users", sa.Column("clicker_power_bps", sa.Integer(), nullable=False, server_default="0"))

    op.create_table(
        "invite_boosts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("owner_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("token", sa.String(length=64), nullable=False),
        sa.Column("kind", sa.String(length=32), nullable=False, server_default="strain_boost"),
        sa.Column("dna_spent", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("rna_spent", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("bonus_multiplier", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("mutation_bonus_chance", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("max_uses", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("uses", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("token"),
    )
    op.create_index("ix_invite_boosts_owner_user_id", "invite_boosts", ["owner_user_id"])
    op.create_index("ix_invite_boosts_token", "invite_boosts", ["token"])


def downgrade() -> None:
    op.drop_index("ix_invite_boosts_token", table_name="invite_boosts")
    op.drop_index("ix_invite_boosts_owner_user_id", table_name="invite_boosts")
    op.drop_table("invite_boosts")
    op.drop_column("users", "clicker_power_bps")
    op.drop_column("users", "clicker_regen_bonus_bps")
    op.drop_column("users", "clicker_max_energy_bonus")
