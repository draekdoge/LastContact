"""make cyclic users/strains FKs deferrable

Revision ID: 20260429_0015
Revises: 20260427_0014
Create Date: 2026-04-29
"""

from __future__ import annotations

from alembic import op

revision = "20260429_0015"
down_revision = "20260427_0014"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # users.strain_id -> strains.id
    op.drop_constraint("fk_users_strain_id", "users", type_="foreignkey")
    op.create_foreign_key(
        "fk_users_strain_id",
        "users",
        "strains",
        ["strain_id"],
        ["id"],
        ondelete="RESTRICT",
        deferrable=True,
        initially="DEFERRED",
    )

    # strains.root_user_id -> users.id
    op.drop_constraint("strains_root_user_id_fkey", "strains", type_="foreignkey")
    op.create_foreign_key(
        "strains_root_user_id_fkey",
        "strains",
        "users",
        ["root_user_id"],
        ["id"],
        ondelete="CASCADE",
        deferrable=True,
        initially="DEFERRED",
    )


def downgrade() -> None:
    op.drop_constraint("strains_root_user_id_fkey", "strains", type_="foreignkey")
    op.create_foreign_key(
        "strains_root_user_id_fkey",
        "strains",
        "users",
        ["root_user_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_constraint("fk_users_strain_id", "users", type_="foreignkey")
    op.create_foreign_key(
        "fk_users_strain_id",
        "users",
        "strains",
        ["strain_id"],
        ["id"],
        ondelete="RESTRICT",
    )

