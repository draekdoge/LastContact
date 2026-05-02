"""opaque referral start-payload (no telegram id in URL)

Revision ID: 0004
Revises: 0003
Create Date: 2026-04-22

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("referral_token", sa.String(length=64), nullable=True))
    op.create_index(op.f("ix_users_referral_token"), "users", ["referral_token"], unique=True)
    op.execute(
        sa.text(
            "UPDATE users SET referral_token = REPLACE(gen_random_uuid()::text, '-', '') "
            "WHERE referral_token IS NULL"
        )
    )
    op.alter_column("users", "referral_token", existing_type=sa.String(length=64), nullable=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_users_referral_token"), table_name="users")
    op.drop_column("users", "referral_token")
