"""Reply-меню админа: только telegram id из BOT_ADMIN_TELEGRAM_IDS."""

from __future__ import annotations

from datetime import UTC, datetime

from aiogram import F, Router
from aiogram.types import LinkPreviewOptions, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards import admin_reply_keyboard, main_reply_keyboard
from app.config import get_settings, parse_admin_telegram_ids
from app.i18n import (
    ADMIN_BUTTON_TEXTS,
    ADMIN_MAIN_MENU_TEXTS,
    ADMIN_ME_ENERGY_TEXTS,
    ADMIN_ME_REAGENTS_TEXTS,
    ADMIN_ME_TIMER_TEXTS,
    get_msg,
    pick_locale,
)
from app.services.admin_self_grant import (
    grant_self_full_clicker_energy,
    grant_self_reagents,
    grant_self_timer_hours,
)
from app.services.user_service import get_user_by_telegram

router = Router(name="admin")

_LINK_PREVIEW_OFF = LinkPreviewOptions(is_disabled=True)


def _is_bot_admin(tid: int) -> bool:
    return tid in parse_admin_telegram_ids(get_settings().bot_admin_telegram_ids)


@router.message(F.text.in_(ADMIN_BUTTON_TEXTS))
async def open_admin_panel(message: Message, session: AsyncSession) -> None:
    if message.from_user is None:
        return
    tid = message.from_user.id
    if not _is_bot_admin(tid):
        m = get_msg(pick_locale(message.from_user.language_code))
        await message.answer(m.admin_forbidden, link_preview_options=_LINK_PREVIEW_OFF)
        return
    u = await get_user_by_telegram(session, tid)
    m = get_msg(u.locale if u else pick_locale(message.from_user.language_code))
    await message.answer(
        m.admin_panel_intro,
        reply_markup=admin_reply_keyboard(m),
        link_preview_options=_LINK_PREVIEW_OFF,
    )


@router.message(F.text.in_(ADMIN_ME_ENERGY_TEXTS))
async def admin_me_energy(message: Message, session: AsyncSession) -> None:
    if message.from_user is None:
        return
    tid = message.from_user.id
    if not _is_bot_admin(tid):
        m = get_msg(pick_locale(message.from_user.language_code))
        await message.answer(m.admin_forbidden, link_preview_options=_LINK_PREVIEW_OFF)
        return
    u = await get_user_by_telegram(session, tid)
    m = get_msg(u.locale if u else pick_locale(message.from_user.language_code))
    if u is None:
        await message.answer(m.admin_me_need_register, reply_markup=admin_reply_keyboard(m), link_preview_options=_LINK_PREVIEW_OFF)
        return
    now = datetime.now(UTC)
    e, mx = grant_self_full_clicker_energy(u, now)
    await message.answer(
        m.admin_me_energy_ok.format(e=e, m=mx),
        reply_markup=admin_reply_keyboard(m),
        link_preview_options=_LINK_PREVIEW_OFF,
    )


@router.message(F.text.in_(ADMIN_ME_REAGENTS_TEXTS))
async def admin_me_reagents(message: Message, session: AsyncSession) -> None:
    if message.from_user is None:
        return
    tid = message.from_user.id
    if not _is_bot_admin(tid):
        m = get_msg(pick_locale(message.from_user.language_code))
        await message.answer(m.admin_forbidden, link_preview_options=_LINK_PREVIEW_OFF)
        return
    u = await get_user_by_telegram(session, tid)
    m = get_msg(u.locale if u else pick_locale(message.from_user.language_code))
    if u is None:
        await message.answer(m.admin_me_need_register, reply_markup=admin_reply_keyboard(m), link_preview_options=_LINK_PREVIEW_OFF)
        return
    d, r, c = grant_self_reagents(u)
    await message.answer(
        m.admin_me_reagents_ok.format(d=d, r=r, c=c),
        reply_markup=admin_reply_keyboard(m),
        link_preview_options=_LINK_PREVIEW_OFF,
    )


@router.message(F.text.in_(ADMIN_ME_TIMER_TEXTS))
async def admin_me_timer(message: Message, session: AsyncSession) -> None:
    if message.from_user is None:
        return
    tid = message.from_user.id
    if not _is_bot_admin(tid):
        m = get_msg(pick_locale(message.from_user.language_code))
        await message.answer(m.admin_forbidden, link_preview_options=_LINK_PREVIEW_OFF)
        return
    u = await get_user_by_telegram(session, tid)
    m = get_msg(u.locale if u else pick_locale(message.from_user.language_code))
    if u is None:
        await message.answer(m.admin_me_need_register, reply_markup=admin_reply_keyboard(m), link_preview_options=_LINK_PREVIEW_OFF)
        return
    now = datetime.now(UTC)
    ok, h = grant_self_timer_hours(u, now)
    body = m.admin_me_timer_ok.format(h=h) if ok else m.admin_me_timer_skip
    await message.answer(body, reply_markup=admin_reply_keyboard(m), link_preview_options=_LINK_PREVIEW_OFF)


@router.message(F.text.in_(ADMIN_MAIN_MENU_TEXTS))
async def admin_back_to_player_menu(message: Message, session: AsyncSession) -> None:
    if message.from_user is None:
        return
    tid = message.from_user.id
    if not _is_bot_admin(tid):
        m = get_msg(pick_locale(message.from_user.language_code))
        await message.answer(m.admin_forbidden, link_preview_options=_LINK_PREVIEW_OFF)
        return
    u = await get_user_by_telegram(session, tid)
    m = get_msg(u.locale if u else pick_locale(message.from_user.language_code))
    await message.answer(
        m.back_to_main_ack,
        reply_markup=main_reply_keyboard(m, telegram_id=tid),
        link_preview_options=_LINK_PREVIEW_OFF,
    )
