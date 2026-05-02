"""strains + users.strain_id + strain_afflictions

Revision ID: 20260427_0012
Revises: 20260426_0011
Create Date: 2026-04-27
"""

from __future__ import annotations

import random
import uuid
from datetime import UTC, datetime

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "20260427_0012"
down_revision = "20260426_0011"
branch_labels = None
depends_on = None


_ADJ = [
    "Чёрный",
    "Белый",
    "Алый",
    "Пепельный",
    "Туманный",
    "Серый",
    "Янтарный",
    "Ледяной",
    "Горящий",
    "Ночной",
    "Солнечный",
    "Глухой",
]
_NOUN = [
    "Лотос",
    "Шторм",
    "Сигнал",
    "Пульс",
    "Спора",
    "Туман",
    "Клинок",
    "Иней",
    "Омут",
    "Хор",
    "Пепел",
    "Кристалл",
]


def _make_code(strain_id: uuid.UUID) -> str:
    # Короткий читаемый код из uuid; коллизии крайне маловероятны.
    s = strain_id.hex.upper()
    return f"X-{s[:4]}{s[4:6]}"


def upgrade() -> None:
    op.create_table(
        "strains",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("code", sa.String(length=16), nullable=False, unique=True),
        sa.Column("title", sa.String(length=64), nullable=False),
        sa.Column(
            "root_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
            index=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # users.strain_id — сначала nullable, потом заполним и сделаем NOT NULL.
    op.add_column("users", sa.Column("strain_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_index("ix_users_strain_id", "users", ["strain_id"])

    op.create_table(
        "strain_afflictions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column(
            "strain_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("strains.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("type", sa.String(length=32), nullable=False),
        sa.Column("severity", sa.SmallInteger(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("cure_progress", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("cure_required", sa.Integer(), nullable=False),
        sa.Column("cured_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_strain_afflictions_active",
        "strain_afflictions",
        ["strain_id", "cured_at", "ends_at"],
    )
    op.alter_column("strain_afflictions", "cure_progress", server_default=None)

    # ── Backfill strain_id для существующих пользователей ───────────────────────
    bind = op.get_bind()

    # Маппинг user_id -> root_id по дереву заражения
    rows = bind.execute(
        sa.text(
            """
            WITH RECURSIVE chain AS (
              SELECT id, infected_by_user_id, id AS root_id
              FROM users
              WHERE infected_by_user_id IS NULL
              UNION ALL
              SELECT u.id, u.infected_by_user_id, c.root_id
              FROM users u
              JOIN chain c ON u.infected_by_user_id = c.id
            )
            SELECT id, root_id FROM chain
            """
        )
    ).fetchall()

    if rows:
        user_to_root: dict[uuid.UUID, uuid.UUID] = {r[0]: r[1] for r in rows}
        roots = sorted({r[1] for r in rows})

        root_to_strain: dict[uuid.UUID, uuid.UUID] = {}
        for root_id in roots:
            sid = uuid.uuid4()
            code = _make_code(sid)
            # "покрасивее": имя штамма + эпитет
            epithet = f"{random.choice(_ADJ)} {random.choice(_NOUN)}"
            title = f"Штамм {code} «{epithet}»"
            bind.execute(
                sa.text(
                    """
                    INSERT INTO strains (id, code, title, root_user_id, created_at)
                    VALUES (:id, :code, :title, :root_user_id, :created_at)
                    """
                ),
                {
                    "id": sid,
                    "code": code,
                    "title": title,
                    "root_user_id": root_id,
                    "created_at": datetime.now(UTC),
                },
            )
            root_to_strain[root_id] = sid

        # массовое обновление users.strain_id
        for user_id, root_id in user_to_root.items():
            bind.execute(
                sa.text("UPDATE users SET strain_id = :sid WHERE id = :uid"),
                {"sid": root_to_strain[root_id], "uid": user_id},
            )

    # FK + NOT NULL
    op.create_foreign_key(
        "fk_users_strain_id",
        "users",
        "strains",
        ["strain_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.alter_column("users", "strain_id", nullable=False)


def downgrade() -> None:
    op.drop_constraint("fk_users_strain_id", "users", type_="foreignkey")
    op.drop_index("ix_users_strain_id", table_name="users")
    op.drop_column("users", "strain_id")

    op.drop_index("ix_strain_afflictions_active", table_name="strain_afflictions")
    op.drop_table("strain_afflictions")
    op.drop_table("strains")

