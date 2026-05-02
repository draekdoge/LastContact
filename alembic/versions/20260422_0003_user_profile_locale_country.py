"""user profile: locale, country, telegram display, avatar file id

Revision ID: 0003
Revises: 0002
Create Date: 2026-04-22

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("locale", sa.String(length=8), nullable=False, server_default="ru"),
    )
    op.add_column("users", sa.Column("country_code", sa.String(length=2), nullable=True))
    op.add_column("users", sa.Column("tg_username", sa.String(length=255), nullable=True))
    op.add_column("users", sa.Column("display_first_name", sa.String(length=255), nullable=True))
    op.add_column("users", sa.Column("avatar_small_file_id", sa.String(length=255), nullable=True))
    op.create_index(op.f("ix_users_country_code"), "users", ["country_code"], unique=False)
    op.alter_column("users", "locale", server_default=None)


def downgrade() -> None:
    op.drop_index(op.f("ix_users_country_code"), table_name="users")
    op.drop_column("users", "avatar_small_file_id")
    op.drop_column("users", "display_first_name")
    op.drop_column("users", "tg_username")
    op.drop_column("users", "country_code")
    op.drop_column("users", "locale")
