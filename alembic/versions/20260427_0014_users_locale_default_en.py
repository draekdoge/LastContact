"""users: locale default en

Revision ID: 20260427_0014
Revises: 20260427_0013
Create Date: 2026-04-27
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260427_0014"
down_revision = "20260427_0013"
branch_labels = None
depends_on = None


_SUPPORTED = ("ru", "en", "uk", "de", "es", "pt", "ko", "ja", "zh")


def upgrade() -> None:
    # DB-level default (code-level fallback is handled in app/i18n/messages.py)
    op.alter_column("users", "locale", existing_type=sa.String(length=8), server_default="en")

    # Safety backfill (should be no-op for healthy DBs).
    op.execute("UPDATE users SET locale = 'en' WHERE locale IS NULL OR locale = ''")
    op.execute(
        "UPDATE users SET locale = 'en' "
        "WHERE locale IS NOT NULL AND locale <> '' AND locale NOT IN "
        f"{_SUPPORTED}"
    )


def downgrade() -> None:
    op.alter_column("users", "locale", existing_type=sa.String(length=8), server_default=None)

