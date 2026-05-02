"""Бонус регена: временный после инвайта + сеть только пока рефералы онлайн в Mini App."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.config import get_settings
from app.db.models import User

# Скорость ~ (1 + bps/10000) к базе; 10000 ≈ ×2, 20000 ≈ ×3 при базе 6 с.
BPS_PER_DIRECT_ONLINE = 10_000
BPS_PER_INDIRECT_ONLINE = 4_000
INDIRECT_SECOND_RING_MULT = 1.5

MAX_NETWORK_REGEN_BPS = 80_000
MAX_TOTAL_REGEN_BPS = 120_000


def _naive_utc(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt


def invite_temp_regen_bonus_bps(user: User, now: datetime) -> int:
    ends = _naive_utc(user.invite_regen_boost_ends_at)
    if ends is None:
        return 0
    now_u = now if now.tzinfo else now.replace(tzinfo=UTC)
    if now_u >= ends:
        return 0
    return max(0, int(get_settings().invite_regen_boost_bps))


def extend_invite_regen_boost_window(user: User, now: datetime | None = None) -> None:
    if now is None:
        now = datetime.now(UTC)
    settings = get_settings()
    hours = float(settings.invite_regen_boost_hours)
    now_u = now if now.tzinfo else now.replace(tzinfo=UTC)
    base = _naive_utc(user.invite_regen_boost_ends_at)
    if base is None or base < now_u:
        base = now_u
    user.invite_regen_boost_ends_at = base + timedelta(hours=hours)


def network_regen_bonus_bps(user: User) -> int:
    d = max(0, int(user.mini_regen_online_direct or 0))
    subtree = max(0, int(user.mini_regen_online_subtree or 0))
    indirect = max(0, subtree - d)
    direct_part = d * BPS_PER_DIRECT_ONLINE
    mult = INDIRECT_SECOND_RING_MULT if indirect > 0 else 1.0
    indirect_part = int(round(indirect * BPS_PER_INDIRECT_ONLINE * mult))
    raw = direct_part + indirect_part
    return min(raw, MAX_NETWORK_REGEN_BPS)


def effective_regen_bonus_bps(user: User, now: datetime | None = None) -> int:
    if now is None:
        now = datetime.now(UTC)
    it = invite_temp_regen_bonus_bps(user, now)
    net = network_regen_bonus_bps(user)
    return min(it + net, MAX_TOTAL_REGEN_BPS)
