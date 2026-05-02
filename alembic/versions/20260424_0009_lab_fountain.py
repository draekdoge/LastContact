"""lab_cycles table + fountain_contributions + users lab/zombie fields

Revision ID: 20260424_0009
Revises: 20260424_0008
Create Date: 2026-04-24
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "20260424_0009"
down_revision = "20260424_0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── users: новые поля ──────────────────────────────────────────────────────
    op.add_column("users", sa.Column("lab_cycles_today", sa.SmallInteger(), nullable=False, server_default="0"))
    op.add_column("users", sa.Column("lab_last_cycle_date", sa.Date(), nullable=True))
    op.add_column("users", sa.Column("lab_revival_streak", sa.SmallInteger(), nullable=False, server_default="0"))
    op.add_column("users", sa.Column("zombie_manual_infections", sa.SmallInteger(), nullable=False, server_default="0"))
    op.add_column("users", sa.Column("fountain_revival_ready", sa.Boolean(), nullable=False, server_default="false"))

    # ── lab_cycles ─────────────────────────────────────────────────────────────
    op.create_table(
        "lab_cycles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("state", sa.String(32), nullable=False, server_default="analyzing"),
        # analyzing | ready | claimed | expired
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("result_ready_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("claimed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reward_type", sa.String(32), nullable=True),
        # timer_hours | mutation_point | revival_streak
        sa.Column("reward_hours", sa.Float(), nullable=True),
        sa.Column("is_revival", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.create_index("ix_lab_cycles_user_id", "lab_cycles", ["user_id"])
    op.create_index("ix_lab_cycles_state", "lab_cycles", ["state"])

    # ── fountain_contributions ────────────────────────────────────────────────
    op.create_table(
        "fountain_contributions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("global_events.id", ondelete="CASCADE"), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False),
        sa.Column("action_type", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_fountain_contrib_user_event", "fountain_contributions", ["user_id", "event_id"])
    op.create_index("ix_fountain_contrib_event", "fountain_contributions", ["event_id"])


def downgrade() -> None:
    op.drop_table("fountain_contributions")
    op.drop_table("lab_cycles")
    op.drop_column("users", "fountain_revival_ready")
    op.drop_column("users", "zombie_manual_infections")
    op.drop_column("users", "lab_revival_streak")
    op.drop_column("users", "lab_last_cycle_date")
    op.drop_column("users", "lab_cycles_today")
