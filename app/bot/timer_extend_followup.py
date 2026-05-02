"""Второе сообщение: «от чего растёт время» — не внутри карточки статуса."""

from __future__ import annotations

from aiogram.types import LinkPreviewOptions, Message

from app.bot.keyboards import main_reply_keyboard
from app.db.models import User
from app.i18n.messages import Msg

_LINK_PREVIEW_OFF = LinkPreviewOptions(is_disabled=True)


async def send_timer_extend_sources_message(
    message: Message,
    user: User,
    m: Msg,
    *,
    bonus_hours: float,
) -> None:
    if user.state != "infected" or user.timer_ends_at is None:
        return
    await message.answer(
        m.timer_extend_sources.format(bonus_hours=float(bonus_hours)),
        reply_markup=main_reply_keyboard(m, telegram_id=user.telegram_id),
        link_preview_options=_LINK_PREVIEW_OFF,
    )
