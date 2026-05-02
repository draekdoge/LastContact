from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import LinkPreviewOptions
from sqlalchemy import select

from app.bot.keyboards import main_reply_keyboard
from app.bot.player_card import zombie_transformation_html
from app.config import get_settings
from app.db.models import User
from app.db.session import async_session_maker
from app.i18n import get_msg

logger = logging.getLogger(__name__)

_LINK_PREVIEW_OFF = LinkPreviewOptions(is_disabled=True)


def _sleeping_reference_time(user: User) -> datetime:
    """База для «нет заражений N ч»: последний успешный реферал или момент регистрации."""
    if user.last_spread_at is not None:
        return user.last_spread_at
    return user.created_at


async def run_timer_sweep() -> None:
    settings = get_settings()
    now = datetime.now(UTC)
    bot: Bot | None = None
    if settings.bot_token:
        bot = Bot(
            token=settings.bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
    else:
        logger.warning("timer_sweep: BOT_TOKEN пуст — состояния обновятся без уведомлений в Telegram")

    try:
        async with async_session_maker() as session:
            result = await session.scalars(
                select(User).where(User.is_npc.is_(False), User.side == "virus")
            )
            users = list(result)

            for user in users:
                if user.state == "immune" and user.immune_ends_at is not None:
                    if user.immune_ends_at <= now:
                        hours = (
                            settings.launch_timer_hours
                            if settings.launch_mode
                            else settings.default_timer_hours
                        )
                        user.state = "infected"
                        user.immune_ends_at = None
                        user.timer_ends_at = now + timedelta(hours=hours)
                        user.timer_alert_level = 0
                        loc = get_msg(user.locale)
                        if bot is not None:
                            try:
                                await bot.send_message(
                                    chat_id=user.telegram_id,
                                    text=loc.sweep_immune_ended,
                                )
                            except Exception as exc:
                                logger.warning(
                                    "immune ended notify failed tg=%s: %s",
                                    user.telegram_id,
                                    exc,
                                )
                    continue

                if user.state != "infected" or user.timer_ends_at is None:
                    continue

                if user.timer_ends_at <= now:
                    user.state = "zombie"
                    user.timer_alert_level = 0
                    msg = get_msg(user.locale)
                    if bot is not None:
                        try:
                            await bot.send_message(
                                chat_id=user.telegram_id,
                                text=zombie_transformation_html(user, msg),
                                reply_markup=main_reply_keyboard(msg, telegram_id=user.telegram_id),
                                link_preview_options=_LINK_PREVIEW_OFF,
                            )
                        except Exception as exc:
                            logger.warning("zombie notify failed tg=%s: %s", user.telegram_id, exc)
                    continue

                left_sec = (user.timer_ends_at - now).total_seconds()
                if left_sec <= 0:
                    continue

                h2 = settings.warn_before_hours * 3600
                h1 = settings.warn_before_hours_1 * 3600
                m30 = settings.warn_before_minutes_30 * 60
                m10 = settings.warn_before_minutes_10 * 60

                loc = get_msg(user.locale)
                try:
                    if left_sec <= m10 and user.timer_alert_level < 4:
                        user.timer_alert_level = 4
                        if bot is not None:
                            await bot.send_message(
                                chat_id=user.telegram_id,
                                text=loc.sweep_warn_10m,
                            )
                    elif left_sec <= m30 and user.timer_alert_level < 3:
                        user.timer_alert_level = 3
                        if bot is not None:
                            await bot.send_message(
                                chat_id=user.telegram_id,
                                text=loc.sweep_warn_30m,
                            )
                    elif left_sec <= h1 and user.timer_alert_level < 2:
                        user.timer_alert_level = 2
                        if bot is not None:
                            await bot.send_message(
                                chat_id=user.telegram_id,
                                text=loc.sweep_warn_1h,
                            )
                    elif left_sec <= h2 and user.timer_alert_level < 1:
                        user.timer_alert_level = 1
                        if bot is not None:
                            await bot.send_message(
                                chat_id=user.telegram_id,
                                text=loc.sweep_warn_2h,
                            )
                except Exception as exc:
                    logger.warning("warn notify failed tg=%s: %s", user.telegram_id, exc)

            await session.commit()
    finally:
        if bot is not None:
            await bot.session.close()
