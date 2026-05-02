import asyncio
import logging
import random
from datetime import UTC, datetime

from worker.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="worker.tasks.timer_tick")
def timer_tick() -> str:
    """Проверка таймеров: зомби, «спящий», предупреждения."""
    from app.db.session import engine
    from app.services.timer_sweep import run_timer_sweep

    async def _once() -> None:
        try:
            await run_timer_sweep()
        finally:
            # Каждый asyncio.run() закрывает свой loop; пул asyncpg остаётся привязанным к
            # старому loop — без dispose второй тик даёт TCPTransport closed.
            await engine.dispose()

    try:
        asyncio.run(_once())
    except Exception:
        logger.exception("timer_sweep failed")
        raise
    return "ok"


@celery_app.task(name="worker.tasks.lab_sweep")
def lab_sweep() -> str:
    """Переводит готовые lab_cycles analyzing→ready и шлёт пуши."""
    from app.db.models import User
    from app.db.session import async_session_maker, engine
    from app.i18n import get_msg
    from app.services.lab_service import sweep_ready_labs

    from aiogram import Bot
    from aiogram.client.default import DefaultBotProperties
    from aiogram.enums import ParseMode
    from aiogram.types import LinkPreviewOptions
    from sqlalchemy import select

    async def _once() -> None:
        from app.config import get_settings
        settings = get_settings()
        if not settings.bot_token:
            return
        async with async_session_maker() as session:
            telegram_ids = await sweep_ready_labs(session)
            await session.commit()

        if not telegram_ids:
            return

        bot = Bot(
            token=settings.bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
        lp_off = LinkPreviewOptions(is_disabled=True)
        try:
            async with async_session_maker() as session:
                for tid_str in telegram_ids:
                    try:
                        tid = int(tid_str)
                        user = await session.scalar(
                            select(User).where(User.telegram_id == tid)
                        )
                        if user is None:
                            continue
                        msg = get_msg(user.locale)
                        await bot.send_message(
                            tid,
                            msg.lab_ready_push,
                            link_preview_options=lp_off,
                        )
                    except Exception:
                        logger.exception("lab_sweep push failed for %s", tid_str)
        finally:
            await bot.session.close()

    async def _run() -> None:
        try:
            await _once()
        finally:
            await engine.dispose()

    try:
        asyncio.run(_run())
    except Exception:
        logger.exception("lab_sweep failed")
        raise
    return "ok"


@celery_app.task(name="worker.tasks.strain_afflictions_tick")
def strain_afflictions_tick() -> str:
    """По расписанию Beat (`Settings.affliction_check_minutes`): шанс дебаффа штамма + пуши."""
    from app.config import get_settings
    from app.db.models import Strain, StrainAffliction, User
    from app.db.session import async_session_maker, engine
    from app.i18n import get_msg
    from app.services.affliction_service import tick_afflictions

    from aiogram import Bot
    from aiogram.client.default import DefaultBotProperties
    from aiogram.enums import ParseMode
    from aiogram.types import LinkPreviewOptions
    from sqlalchemy import select

    logger = logging.getLogger(__name__)

    async def _once() -> None:
        settings = get_settings()
        if not settings.bot_token:
            return

        async with async_session_maker() as session:
            spawned = await tick_afflictions(session)
            await session.commit()

        bot = Bot(
            token=settings.bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
        lp_off = LinkPreviewOptions(is_disabled=True)
        try:
            async with async_session_maker() as session:
                # 1) Пуши о появившихся дебаффах (spawned)
                for a in spawned:
                    strain = await session.get(Strain, a.strain_id)
                    if strain is None:
                        continue
                    users = await session.scalars(select(User).where(User.strain_id == strain.id))
                    for u in users:
                        try:
                            msg = get_msg(u.locale)
                            text = _affliction_spawn_message(
                                msg=msg,
                                strain_title=strain.title,
                                a_type=a.type,
                                severity=int(a.severity),
                            )
                            await bot.send_message(u.telegram_id, text, link_preview_options=lp_off)
                        except Exception:
                            logger.exception("affliction push failed tid=%s", u.telegram_id)

                # 2) Пуши о вылеченных дебаффах (разово)
                now = datetime.now(UTC)
                cured = await session.scalars(
                    select(StrainAffliction).where(
                        StrainAffliction.cured_at.is_not(None),
                        StrainAffliction.cured_notified_at.is_(None),
                    )
                )
                for a in list(cured):
                    strain = await session.get(Strain, a.strain_id)
                    if strain is None:
                        continue
                    users = await session.scalars(select(User).where(User.strain_id == strain.id))
                    for u in users:
                        try:
                            msg = get_msg(u.locale)
                            text = _affliction_cured_message(
                                msg=msg,
                                strain_title=strain.title,
                                a_type=a.type,
                            )
                            await bot.send_message(u.telegram_id, text, link_preview_options=lp_off)
                        except Exception:
                            logger.exception("affliction cured push failed tid=%s", u.telegram_id)
                    a.cured_notified_at = now
                await session.commit()
        finally:
            await bot.session.close()

    async def _run() -> None:
        try:
            await _once()
        finally:
            await engine.dispose()

    try:
        asyncio.run(_run())
    except Exception:
        logging.getLogger(__name__).exception("strain_afflictions_tick failed")
        raise
    return "ok"


def _affliction_spawn_message(*, msg, strain_title: str, a_type: str, severity: int) -> str:
    sev = "I" if severity == 1 else ("II" if severity == 2 else "III")
    type_map = {
        "necrosis_bloom": msg.affliction_type_necrosis_bloom,
        "signal_spoof": msg.affliction_type_signal_spoof,
        "enzyme_leak": msg.affliction_type_enzyme_leak,
        "latency_fog": msg.affliction_type_latency_fog,
    }
    label = type_map.get(a_type, a_type)
    pool = msg.affliction_spawn_push_pool
    tpl = random.choice(pool) if pool else "{strain}: {type} ({sev})"
    return tpl.format(strain=strain_title, type=label, sev=sev)


def _affliction_cured_message(*, msg, strain_title: str, a_type: str) -> str:
    type_map = {
        "necrosis_bloom": msg.affliction_type_necrosis_bloom,
        "signal_spoof": msg.affliction_type_signal_spoof,
        "enzyme_leak": msg.affliction_type_enzyme_leak,
        "latency_fog": msg.affliction_type_latency_fog,
    }
    label = type_map.get(a_type, a_type)
    pool = msg.affliction_cured_push_pool
    tpl = random.choice(pool) if pool else "{strain}: cured {type}"
    return tpl.format(strain=strain_title, type=label)
