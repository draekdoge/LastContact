"""users: reagents + sample collection + fountain pour daily

Revision ID: 20260426_0010
Revises: 20260424_0009
Create Date: 2026-04-26
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "20260426_0010"
down_revision = "20260424_0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("reagent_dna", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("users", sa.Column("reagent_rna", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("users", sa.Column("reagent_cat", sa.Integer(), nullable=False, server_default="0"))
    op.add_column(
        "users",
        sa.Column(
            "lab_sample_collection",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )
    op.add_column("users", sa.Column("fountain_pour_units_today", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("users", sa.Column("fountain_pour_last_date", sa.Date(), nullable=True))

    op.alter_column("users", "reagent_dna", server_default=None)
    op.alter_column("users", "reagent_rna", server_default=None)
    op.alter_column("users", "reagent_cat", server_default=None)
    op.alter_column("users", "lab_sample_collection", server_default=None)
    op.alter_column("users", "fountain_pour_units_today", server_default=None)


def downgrade() -> None:
    op.drop_column("users", "fountain_pour_last_date")
    op.drop_column("users", "fountain_pour_units_today")
    op.drop_column("users", "lab_sample_collection")
    op.drop_column("users", "reagent_cat")
    op.drop_column("users", "reagent_rna")
    op.drop_column("users", "reagent_dna")
