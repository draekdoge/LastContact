from __future__ import annotations

import math
import random
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Literal

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db.models import Strain, StrainAffliction, User


AfflictionType = Literal["necrosis_bloom", "signal_spoof", "enzyme_leak", "latency_fog"]


@dataclass(frozen=True, slots=True)
class AfflictionEffect:
    lab_reward_mult: float = 1.0
    fountain_weight_mult: float = 1.0
    fountain_pour_cap_delta_units: int = 0
    lab_analysis_minutes_delta: int = 0


def active_affliction_effect(a: StrainAffliction | None) -> AfflictionEffect:
    if a is None:
        return AfflictionEffect()
    sev = int(a.severity)
    t = a.type
    if t == "necrosis_bloom":
        # -15% / severity, cap 45%
        return AfflictionEffect(lab_reward_mult=max(0.55, 1.0 - 0.15 * sev))
    if t == "signal_spoof":
        # -20% / severity, cap 60%
        return AfflictionEffect(fountain_weight_mult=max(0.4, 1.0 - 0.2 * sev))
    if t == "enzyme_leak":
        # -2 units per severity (min cap handled outside)
        return AfflictionEffect(fountain_pour_cap_delta_units=-(2 * sev))
    if t == "latency_fog":
        # +10 min per severity, cap +30
        return AfflictionEffect(lab_analysis_minutes_delta=min(30, 10 * sev))
    return AfflictionEffect()


async def get_active_affliction(session: AsyncSession, *, strain_id: uuid.UUID, now: datetime | None = None) -> StrainAffliction | None:
    if now is None:
        now = datetime.now(UTC)
    return await session.scalar(
        select(StrainAffliction)
        .where(
            StrainAffliction.strain_id == strain_id,
            StrainAffliction.cured_at.is_(None),
            StrainAffliction.ends_at > now,
        )
        .order_by(StrainAffliction.started_at.desc())
    )


def affliction_spawn_chance(*, size: int) -> float:
    s = get_settings()
    if size < int(getattr(s, "affliction_min_strain_size", 4)):
        return 0.0
    base = float(getattr(s, "affliction_base_chance", 0.03))
    cap = float(getattr(s, "affliction_chance_cap", 0.08))
    # base + 0.01 * log2(size)
    chance = base + 0.01 * (math.log(size, 2) if size > 0 else 0.0)
    return max(0.0, min(cap, chance))


def pick_affliction_type() -> AfflictionType:
    return random.choice(["necrosis_bloom", "signal_spoof", "enzyme_leak", "latency_fog"])


def required_research_points(*, severity: int, size: int) -> int:
    # MVP: базово 6..12, растёт с severity и размером (мягко).
    base = 6 + (severity - 1) * 4
    size_bonus = min(8, int(math.log(max(size, 1), 2)))
    return base + size_bonus


async def create_affliction_for_strain(session: AsyncSession, *, strain: Strain, size: int) -> StrainAffliction:
    now = datetime.now(UTC)
    s = get_settings()
    dur_h = int(getattr(s, "affliction_duration_hours", 18))
    severity = random.choice([1, 1, 2, 2, 3])
    a_type = pick_affliction_type()
    req = required_research_points(severity=severity, size=size)
    aff = StrainAffliction(
        id=uuid.uuid4(),
        strain_id=strain.id,
        type=a_type,
        severity=severity,
        started_at=now,
        ends_at=now + timedelta(hours=dur_h),
        cure_progress=0,
        cure_required=req,
        cured_at=None,
    )
    session.add(aff)
    return aff


async def tick_afflictions(session: AsyncSession) -> list[StrainAffliction]:
    """
    Вызывается из Celery beat.
    Возвращает список созданных дебаффов (для последующей рассылки).
    """
    now = datetime.now(UTC)
    s = get_settings()
    cooldown_h = int(getattr(s, "affliction_cooldown_hours", 36))
    spawned: list[StrainAffliction] = []

    strains = list(await session.scalars(select(Strain)))
    if not strains:
        return spawned

    for strain in strains:
        # если есть активный — пропускаем
        active = await get_active_affliction(session, strain_id=strain.id, now=now)
        if active is not None:
            continue

        # cooldown: смотрим последнее окончание/вылечивание
        last_end = await session.scalar(
            select(func.max(StrainAffliction.ends_at)).where(StrainAffliction.strain_id == strain.id)
        )
        last_cured = await session.scalar(
            select(func.max(StrainAffliction.cured_at)).where(StrainAffliction.strain_id == strain.id)
        )
        last_ts = max([t for t in [last_end, last_cured] if t is not None], default=None)
        if last_ts is not None and (now - last_ts) < timedelta(hours=cooldown_h):
            continue

        size = int(
            await session.scalar(
                select(func.count()).where(User.strain_id == strain.id)
            )
            or 0
        )
        chance = affliction_spawn_chance(size=size)
        if chance <= 0:
            continue
        if random.random() > chance:
            continue

        spawned.append(await create_affliction_for_strain(session, strain=strain, size=size))

    return spawned

