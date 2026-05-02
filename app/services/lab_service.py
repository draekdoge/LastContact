"""Лаборатория — бизнес-логика цикла анализа.

Состояния цикла (lab_cycles.state):
  analyzing → ready → claimed
                    → expired  (Infected: через 24 ч после result_ready_at)

Состояния пользователя, влияющие на Лабу:
  infected: обычный цикл (+4–8 ч)
  zombie:   цикл воскрешения (+1 к lab_revival_streak)
"""
from __future__ import annotations

import random
import uuid
from datetime import UTC, date, datetime, timedelta
from typing import Literal

import redis.asyncio as aioredis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db.models import LabCycle, User
from app.services.affliction_service import active_affliction_effect, get_active_affliction
from app.services.reagent_service import apply_reagent_drop_to_user, pour_units_remaining, reset_fountain_pour_daily_if_needed, roll_reagent_drop
from app.services.user_service import append_timer_history

_LAB_KEY = "lab:{uid}"          # TTL = lab_analysis_minutes * 60
_LAB_RESULT_KEY = "lab_res:{uid}"  # TTL = 24 ч, только для infected


def _redis_client() -> aioredis.Redis:
    return aioredis.from_url(get_settings().redis_url, decode_responses=True)


# ── Вспомогательные ────────────────────────────────────────────────────────────

def _today_utc() -> date:
    return datetime.now(UTC).date()


def _reset_daily_if_needed(user: User) -> None:
    """Сбрасывает lab_cycles_today если UTC-дата изменилась."""
    today = _today_utc()
    if user.lab_last_cycle_date != today:
        user.lab_cycles_today = 0
        user.lab_last_cycle_date = today


def _daily_limit(user: User) -> int:
    settings = get_settings()
    if user.state == "zombie":
        return settings.lab_daily_limit_zombie
    return settings.lab_daily_limit_infected


def _rand_reward_hours() -> float:
    s = get_settings()
    return float(random.randint(s.lab_reward_hours_min, s.lab_reward_hours_max))


# ── Публичный API ──────────────────────────────────────────────────────────────

class LabError(Exception):
    """Ожидаемая ошибка (400-уровня)."""


async def get_lab_state(session: AsyncSession, user: User) -> dict:
    """Возвращает текущее состояние Лабы для данного пользователя."""
    _reset_daily_if_needed(user)
    settings = get_settings()
    now = datetime.now(UTC)

    # Активный цикл (analyzing или ready)
    active = await session.scalar(
        select(LabCycle)
        .where(LabCycle.user_id == user.id, LabCycle.state.in_(["analyzing", "ready"]))
        .order_by(LabCycle.started_at.desc())
    )

    limit = _daily_limit(user)
    can_start = (
        active is None
        and user.lab_cycles_today < limit
        and user.state in ("infected", "zombie")
    )

    result: dict = {
        "can_start": can_start,
        "cycles_today": user.lab_cycles_today,
        "daily_limit": limit,
        "revival_streak": user.lab_revival_streak,
        "revival_streak_needed": settings.lab_revival_streak_needed,
        "active_cycle": None,
    }

    if active:
        ready_at = active.result_ready_at
        remaining_sec = max(0, int((ready_at - now).total_seconds()))
        result["active_cycle"] = {
            "id": str(active.id),
            "state": active.state,
            "started_at": active.started_at.isoformat(),
            "result_ready_at": ready_at.isoformat(),
            "remaining_seconds": remaining_sec,
            "is_revival": active.is_revival,
        }

    reset_fountain_pour_daily_if_needed(user)
    result["reagents"] = {
        "dna": int(user.reagent_dna or 0),
        "rna": int(user.reagent_rna or 0),
        "cat": int(user.reagent_cat or 0),
    }
    result["sample_collection"] = dict(user.lab_sample_collection or {})
    result["fountain_pour"] = {
        "daily_cap": settings.fountain_pour_daily_unit_cap,
        "used_today": int(user.fountain_pour_units_today or 0),
        "remaining_units": pour_units_remaining(user),
    }

    return result


async def start_lab_cycle(session: AsyncSession, user: User) -> dict:
    """Шаг 1 — запускает новый цикл Лабы."""
    _reset_daily_if_needed(user)
    settings = get_settings()
    now = datetime.now(UTC)

    if user.state not in ("infected", "zombie"):
        raise LabError("not_eligible")

    limit = _daily_limit(user)
    if user.lab_cycles_today >= limit:
        raise LabError("daily_limit_reached")

    # Убеждаемся, что нет активного цикла
    existing = await session.scalar(
        select(LabCycle)
        .where(LabCycle.user_id == user.id, LabCycle.state.in_(["analyzing", "ready"]))
    )
    if existing:
        raise LabError("cycle_already_active")

    # Дебафф штамма может замедлить анализ.
    aff = await get_active_affliction(session, strain_id=user.strain_id)
    eff = active_affliction_effect(aff)
    analysis_minutes = int(settings.lab_analysis_minutes) + int(eff.lab_analysis_minutes_delta)
    result_ready_at = now + timedelta(minutes=analysis_minutes)
    cycle = LabCycle(
        id=uuid.uuid4(),
        user_id=user.id,
        state="analyzing",
        started_at=now,
        result_ready_at=result_ready_at,
        is_revival=user.state == "zombie",
    )
    session.add(cycle)
    user.lab_cycles_today += 1
    user.lab_last_cycle_date = now.date()

    # Redis TTL для отслеживания воркером
    async with _redis_client() as r:
        ttl = analysis_minutes * 60
        await r.setex(_LAB_KEY.format(uid=str(user.id)), ttl, str(cycle.id))

    return {
        "cycle_id": str(cycle.id),
        "result_ready_at": result_ready_at.isoformat(),
        "remaining_seconds": analysis_minutes * 60,
    }


async def claim_lab_result(session: AsyncSession, user: User) -> dict:
    """Шаг 3 — забрать результат цикла."""
    settings = get_settings()
    now = datetime.now(UTC)

    cycle = await session.scalar(
        select(LabCycle)
        .where(LabCycle.user_id == user.id, LabCycle.state == "ready")
        .order_by(LabCycle.started_at.desc())
    )
    if cycle is None:
        raise LabError("no_ready_cycle")

    cycle.claimed_at = now
    cycle.state = "claimed"

    reagent_payload = apply_reagent_drop_to_user(user, roll_reagent_drop())

    if cycle.is_revival:
        # Зомби-цикл: +1 к стриику; возможное воскрешение
        user.lab_revival_streak += 1
        cycle.reward_type = "revival_streak"
        was_revived = False
        if user.lab_revival_streak >= settings.lab_revival_streak_needed:
            _apply_resurrection(user, source="lab")
            was_revived = True
        return {
            "reward_type": "revival_streak",
            "streak": user.lab_revival_streak,
            "streak_needed": settings.lab_revival_streak_needed,
            "revived": was_revived,
            **reagent_payload,
        }
    else:
        # Infected: +N часов к таймеру
        hours = _rand_reward_hours()
        # Дебафф штамма может уменьшить награду Лабы.
        aff = await get_active_affliction(session, strain_id=user.strain_id)
        eff = active_affliction_effect(aff)
        hours = round(hours * float(eff.lab_reward_mult), 2)
        cycle.reward_type = "timer_hours"
        cycle.reward_hours = hours
        if user.state == "infected" and user.timer_ends_at is not None:
            user.timer_ends_at += timedelta(hours=hours)
            user.timer_alert_level = 0
            append_timer_history(user, hours, "Лаборатория")
        # Очищаем Redis-результат
        async with _redis_client() as r:
            await r.delete(_LAB_RESULT_KEY.format(uid=str(user.id)))
        # ── Исследование лекарства от дебаффа штамма ───────────────────────────
        aff = await get_active_affliction(session, strain_id=user.strain_id)
        research_added = 0
        cured = False
        if aff is not None:
            # MVP: +1 progress за claim; кап на игрока/сутки — позже (нужен отдельный учёт).
            aff.cure_progress = int(aff.cure_progress or 0) + 1
            research_added = 1
            if int(aff.cure_progress) >= int(aff.cure_required):
                aff.cured_at = now
                cured = True

        return {
            "reward_type": "timer_hours",
            "reward_hours": hours,
            "affliction_research_added": research_added,
            "affliction_cured": cured,
            **reagent_payload,
        }


def _apply_resurrection(user: User, source: Literal["lab", "fountain", "manual"]) -> None:
    """Воскрешение зомби → infected. Вызывается из сервисов и воркеров."""
    settings = get_settings()
    now = datetime.now(UTC)
    bonus = 48.0 if source == "lab" else 24.0
    user.state = "infected"
    user.timer_ends_at = now + timedelta(hours=bonus)
    user.timer_alert_level = 0
    user.lab_revival_streak = 0
    user.zombie_manual_infections = 0
    user.fountain_revival_ready = False
    append_timer_history(user, bonus, f"Воскрешение ({source})")


# ── Воркер: проверка готовых TTL ───────────────────────────────────────────────

async def sweep_ready_labs(session: AsyncSession) -> list[str]:
    """Вызывается Celery-воркером раз в минуту.
    Находит циклы, у которых result_ready_at <= now и state=analyzing,
    переводит в ready, возвращает list[user.telegram_id] для пушей.
    """
    now = datetime.now(UTC)
    from sqlalchemy import and_

    rows = await session.scalars(
        select(LabCycle)
        .where(
            and_(
                LabCycle.state == "analyzing",
                LabCycle.result_ready_at <= now,
            )
        )
    )
    cycles = list(rows)
    notify_tids: list[str] = []
    for cycle in cycles:
        cycle.state = "ready"
        # Пишем Redis-ключ результата для Infected (TTL 24 ч) и пушим
        user = await session.get(User, cycle.user_id)
        if user is not None:
            notify_tids.append(str(user.telegram_id))
            if not cycle.is_revival:
                async with _redis_client() as r:
                    await r.setex(_LAB_RESULT_KEY.format(uid=str(user.id)), 86400, str(cycle.id))
    return notify_tids
