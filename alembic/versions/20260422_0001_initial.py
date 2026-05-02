"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-04-22

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("side", sa.String(length=16), nullable=False),
        sa.Column("state", sa.String(length=32), nullable=False),
        sa.Column("infected_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("timer_ends_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("xp", sa.Integer(), nullable=False),
        sa.Column("mutation_tree", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("streak_days", sa.Integer(), nullable=False),
        sa.Column("is_npc", sa.Boolean(), nullable=False),
        sa.Column("direct_infections_count", sa.Integer(), nullable=False),
        sa.Column("subtree_infections_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["infected_by_user_id"],
            ["users.id"],
            name=op.f("fk_users_infected_by_user_id_users"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
    )
    op.create_index(op.f("ix_users_telegram_id"), "users", ["telegram_id"], unique=True)

    op.create_table(
        "infections",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("infector_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("infected_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("strength", sa.Float(), nullable=False),
        sa.Column("chain_depth", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["infected_user_id"],
            ["users.id"],
            name=op.f("fk_infections_infected_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["infector_user_id"],
            ["users.id"],
            name=op.f("fk_infections_infector_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_infections")),
        sa.UniqueConstraint("infected_user_id", name=op.f("uq_infections_infected_user_id")),
    )

    op.create_table(
        "global_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("type", sa.String(length=64), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_global_events")),
    )
    op.create_index(op.f("ix_global_events_type"), "global_events", ["type"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_global_events_type"), table_name="global_events")
    op.drop_table("global_events")
    op.drop_table("infections")
    op.drop_index(op.f("ix_users_telegram_id"), table_name="users")
    op.drop_table("users")
