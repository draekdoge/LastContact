"""Начисления админу самому себе (reply-кнопки бота)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.db.models import User
from app.services.clicker_energy import clicker_max_energy, clicker_regen_energy
from app.services.user_service import append_timer_history

_CAP = 2_000_000_000

_SELF_DNA = 500
_SELF_RNA = 500
_SELF_CAT = 50
_SELF_TIMER_H = 24.0


def grant_self_full_clicker_energy(user: User, now: datetime) -> tuple[int, int]:
    clicker_regen_energy(user, now)
    mx = clicker_max_energy(user)
    user.clicker_energy = mx
    user.clicker_energy_updated_at = now
    return mx, mx


def grant_self_reagents(user: User) -> tuple[int, int, int]:
    d = min(_CAP, int(user.reagent_dna or 0) + _SELF_DNA)
    r = min(_CAP, int(user.reagent_rna or 0) + _SELF_RNA)
    c = min(_CAP, int(user.reagent_cat or 0) + _SELF_CAT)
    user.reagent_dna = d
    user.reagent_rna = r
    user.reagent_cat = c
    return d, r, c


def grant_self_timer_hours(user: User, now: datetime) -> tuple[bool, float]:
    if user.state != "infected" or user.timer_ends_at is None:
        return False, 0.0
    te = user.timer_ends_at
    if te.tzinfo is None:
        te = te.replace(tzinfo=UTC)
    base = max(te, now)
    user.timer_ends_at = base + timedelta(hours=_SELF_TIMER_H)
    user.timer_alert_level = 0
    append_timer_history(user, _SELF_TIMER_H, "admin_self_grant")
    return True, _SELF_TIMER_H
