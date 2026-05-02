"""users.lab_sample_collection: вернуть server_default '{}'::jsonb

Иначе INSERT без явного значения даёт NULL при NOT NULL (вебхук 500).

Revision ID: 20260426_0011
Revises: 20260426_0010
Create Date: 2026-04-26
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260426_0011"
down_revision = "20260426_0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "users",
        "lab_sample_collection",
        server_default=sa.text("'{}'::jsonb"),
    )


def downgrade() -> None:
    op.alter_column("users", "lab_sample_collection", server_default=None)
