from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Any

from sqlalchemy import BigInteger, Boolean, Date, DateTime, Float, ForeignKey, Integer, SmallInteger, String, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Strain(Base):
    __tablename__ = "strains"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(16), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(64), nullable=False)
    root_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    referral_token: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    """Непрозрачный payload для deep-link ?start=… (без telegram_id в URL)."""

    side: Mapped[str] = mapped_column(String(16), default="virus", nullable=False)
    state: Mapped[str] = mapped_column(String(32), default="infected", nullable=False)
    infected_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    strain_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("strains.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    timer_ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    immune_ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    """Окно иммунитета (восстановление после зомби); state == immune."""
    last_spread_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    """Когда последний раз кто-то зашёл по твоей реферальной ссылке."""

    timer_alert_level: Mapped[int] = mapped_column(default=0, nullable=False)
    """0 — ещё не слали 2ч; 1 — слали 2ч; 2 — слали 30м; 3 — слали 10м. Сброс при бонусе таймера."""

    timer_history: Mapped[list[dict[str, Any]] | None] = mapped_column(JSONB, nullable=True)
    """Последние 3 события роста таймера: [{delta_h, reason, ts}]. FIFO-3."""

    lab_cycles_today: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)
    """Число начатых циклов Лабы за текущие UTC-сутки."""
    lab_last_cycle_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    """UTC-дата последнего начатого цикла (для сброса lab_cycles_today)."""
    lab_revival_streak: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)
    """Подряд UTC-сутки с циклом Лабы (для зомби — путь воскрешения)."""
    zombie_manual_infections: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)
    """Уникальные заражения вручную в зомби-режиме (путь воскрешения)."""
    fountain_revival_ready: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    """true = зомби воскресает при следующем webhook-событии (выставляет воркер Фонтана)."""

    xp: Mapped[int] = mapped_column(default=0, nullable=False)
    mutation_tree: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    streak_days: Mapped[int] = mapped_column(default=0, nullable=False)
    is_npc: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    direct_infections_count: Mapped[int] = mapped_column(default=0, nullable=False)
    subtree_infections_count: Mapped[int] = mapped_column(default=0, nullable=False)

    locale: Mapped[str] = mapped_column(String(8), default="en", nullable=False)
    country_code: Mapped[str | None] = mapped_column(String(2), nullable=True, index=True)
    """ISO 3166-1 alpha-2; эвристика из language_code Telegram, позже — уточнение по IP/Mini App."""

    tg_username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    display_first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    avatar_small_file_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    last_card_message_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    """Последняя карточка статуса/дашборда в личке — удалить при «Передать штамм» из меню."""

    reagent_dna: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reagent_rna: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reagent_cat: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    lab_sample_collection: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    """Счётчики типов образцов из Лабы: { saliva_trace: n, ... }."""

    fountain_pour_units_today: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    fountain_pour_last_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    """UTC-дата последнего учёта перелива реагентов в Фонтан."""

    clicker_energy: Mapped[int] = mapped_column(Integer, default=1200, nullable=False)
    clicker_energy_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    clicker_progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    clicker_daily_rolls: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    clicker_daily_reset_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    clicker_max_energy_bonus: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    clicker_regen_bonus_bps: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    clicker_power_bps: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    mini_app_first_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    """Первый успешный заход в Mini App (валидация TMA)."""

    mini_app_last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    """Последняя активность Mini App; окно «онлайн» для бонуса регена сети."""

    invite_regen_boost_ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    """До этого момента действует временный bps-ускорение регена после нового инвайта (/start)."""

    mini_regen_online_direct: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    """Кэш: прямые рефералы в окне онлайна Mini App (пересчёт при запросах mini API)."""

    mini_regen_online_subtree: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    """Кэш: все потомки в окне онлайна Mini App (включая прямых)."""

    direct_mini_engaged_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    """[Устарело для регена] Ранее: счётчик engage; больше не обновляется."""

    subtree_mini_engaged_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    """[Устарело для регена] Ранее: счётчик engage; больше не обновляется."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    infected_by: Mapped[User | None] = relationship(
        "User", remote_side=[id], foreign_keys=[infected_by_user_id]
    )
    strain: Mapped[Strain] = relationship("Strain", foreign_keys=[strain_id])


class Infection(Base):
    __tablename__ = "infections"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    infector_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    infected_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    strength: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    chain_depth: Mapped[int] = mapped_column(default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class InviteBoost(Base):
    __tablename__ = "invite_boosts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    token: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    kind: Mapped[str] = mapped_column(String(32), nullable=False)
    dna_spent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rna_spent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    bonus_multiplier: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    mutation_bonus_chance: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    max_uses: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    uses: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    owner: Mapped[User] = relationship("User", foreign_keys=[owner_user_id])


class LabCycle(Base):
    __tablename__ = "lab_cycles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    state: Mapped[str] = mapped_column(String(32), default="analyzing", nullable=False, index=True)
    """analyzing | ready | claimed | expired"""
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    result_ready_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    claimed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reward_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    """timer_hours | mutation_point | revival_streak"""
    reward_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_revival: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    """True для зомби-цикла (Лаба воскрешения)."""


class FountainContribution(Base):
    __tablename__ = "fountain_contributions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("global_events.id", ondelete="CASCADE"), nullable=False
    )
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    action_type: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class GlobalEvent(Base):
    __tablename__ = "global_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)


class StrainAffliction(Base):
    __tablename__ = "strain_afflictions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    strain_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("strains.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type: Mapped[str] = mapped_column(String(32), nullable=False)
    severity: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    cure_progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cure_required: Mapped[int] = mapped_column(Integer, nullable=False)
    cured_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cured_notified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
