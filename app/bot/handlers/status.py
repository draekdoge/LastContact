from aiogram import Router
from aiogram.filters import Command
from aiogram.types import LinkPreviewOptions, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards import main_reply_keyboard
from app.bot.player_card import infected_dashboard_html
from app.bot.timer_extend_followup import send_timer_extend_sources_message
from app.config import get_settings
from app.i18n import STATUS_BUTTON_TEXTS, get_msg, pick_locale
from app.services.profile_service import apply_telegram_metadata, refresh_avatar_if_needed
from app.services.user_service import ensure_referral_token, get_user_by_telegram

router = Router(name="status")

_LINK_PREVIEW_OFF = LinkPreviewOptions(is_disabled=True)


async def _send_status(message: Message, session: AsyncSession) -> None:
    if message.from_user is None:
        return
    fu = message.from_user
    loc = pick_locale(fu.language_code)
    m0 = get_msg(loc)

    u = await get_user_by_telegram(session, fu.id)
    if u is None:
        await message.answer(m0.status_use_start, link_preview_options=_LINK_PREVIEW_OFF)
        return

    apply_telegram_metadata(
        u,
        language_code=fu.language_code,
        username=fu.username,
        first_name=fu.first_name,
    )
    await refresh_avatar_if_needed(message.bot, u)
    await ensure_referral_token(session, u)
    m = get_msg(u.locale)
    body = infected_dashboard_html(u, m, fu, status_header=m.mock_header_status)

    common = {
        "reply_markup": main_reply_keyboard(m, telegram_id=fu.id),
        "link_preview_options": _LINK_PREVIEW_OFF,
    }
    if u.avatar_small_file_id and u.state != "zombie":
        sent = await message.answer_photo(u.avatar_small_file_id, caption=body, **common)
    else:
        sent = await message.answer(body, **common)
    u.last_card_message_id = sent.message_id
    settings = get_settings()
    await send_timer_extend_sources_message(
        message,
        u,
        m,
        bonus_hours=float(settings.bonus_hours_per_referral),
    )


@router.message(Command("status"))
async def cmd_status(message: Message, session: AsyncSession) -> None:
    await _send_status(message, session)


@router.message(lambda m: bool(getattr(m, "text", None)) and m.text in STATUS_BUTTON_TEXTS)  # type: ignore[arg-type]
async def status_button(message: Message, session: AsyncSession) -> None:
    await _send_status(message, session)
