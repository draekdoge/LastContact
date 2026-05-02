"""Синхронизация энергии кликера с учётом регенерации — общая логика для Mini App и админки."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.db.models import User
from app.services.clicker_network_regen import effective_regen_bonus_bps

CLICKER_MAX_ENERGY = 1200
CLICKER_REGEN_SECONDS = 6


def clicker_max_energy(user: User) -> int:
    return CLICKER_MAX_ENERGY + max(0, int(user.clicker_max_energy_bonus or 0))


def clicker_regen_seconds(user: User, *, now: datetime | None = None) -> int:
    if now is None:
        now = datetime.now(UTC)
    bonus = max(0, effective_regen_bonus_bps(user, now))
    if bonus <= 0:
        return CLICKER_REGEN_SECONDS
    return max(2, int(round(CLICKER_REGEN_SECONDS / (1 + bonus / 10000))))


def clicker_regen_energy(user: User, now: datetime) -> None:
    updated = user.clicker_energy_updated_at or now
    if updated.tzinfo is None:
        updated = updated.replace(tzinfo=UTC)
    max_energy = clicker_max_energy(user)
    regen_seconds = clicker_regen_seconds(user, now=now)
    energy = max(0, min(max_energy, int(user.clicker_energy or 0)))
    if energy >= max_energy:
        user.clicker_energy = max_energy
        user.clicker_energy_updated_at = now
        return
    elapsed = max(0, int((now - updated).total_seconds()))
    gained = elapsed // regen_seconds
    if gained <= 0:
        user.clicker_energy = energy
        return
    user.clicker_energy = min(max_energy, energy + gained)
    user.clicker_energy_updated_at = updated + timedelta(seconds=gained * regen_seconds)
    if user.clicker_energy >= max_energy:
        user.clicker_energy_updated_at = now


def clicker_next_energy_at(user: User, now: datetime) -> datetime | None:
    if int(user.clicker_energy or 0) >= clicker_max_energy(user):
        return None
    updated = user.clicker_energy_updated_at or now
    if updated.tzinfo is None:
        updated = updated.replace(tzinfo=UTC)
    nxt = updated + timedelta(seconds=clicker_regen_seconds(user, now=now))
    return max(nxt, now)
