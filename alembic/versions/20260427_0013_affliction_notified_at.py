"""strain_afflictions: cured_notified_at

Revision ID: 20260427_0013
Revises: 20260427_0012
Create Date: 2026-04-27
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260427_0013"
down_revision = "20260427_0012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("strain_afflictions", sa.Column("cured_notified_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("strain_afflictions", "cured_notified_at")

