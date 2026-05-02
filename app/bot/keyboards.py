from urllib.parse import quote

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from app.config import get_settings, parse_admin_telegram_ids
from app.i18n.messages import Msg


def mini_app_webapp_url(*, startapp: str) -> str | None:
    """HTTPS URL Mini App с tgWebAppStartParam (короткий латинский ярлык). Страница — `/`, не `/mini`."""
    raw = get_settings().mini_app_public_url.strip()
    if not raw:
        return None
    base = raw.rstrip("/")
    if base.lower().endswith("/mini"):
        base = base[: -len("/mini")].rstrip("/")
    if not base:
        return None
    sep = "&" if "?" in base else "?"
    return f"{base}{sep}startapp={quote(startapp, safe='')}"


def invite_chain_only_markup(m: Msg, *, invite_url: str) -> InlineKeyboardMarkup:
    """У получателя карточки: одна кнопка — deep link в бота."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=m.spread_join_chain_button, url=invite_url)],
        ]
    )


# Inline и reply в одном сообщении нельзя; под фото — inline-кнопка с switch_inline_query.
INVITE_CONTACTS_CALLBACK_DATA = "invite_ct"
"""Старые сообщения: inline ведёт на колбэк."""


def main_reply_keyboard(m: Msg, *, telegram_id: int | None = None) -> ReplyKeyboardMarkup:
    """Главное меню бота: «Передать штамм» + «Статус» (+ «Админка» для BOT_ADMIN_TELEGRAM_IDS)."""
    rows: list[list[KeyboardButton]] = [
        [KeyboardButton(text=m.btn_spread)],
        [KeyboardButton(text=m.btn_status)],
    ]
    if telegram_id is not None:
        admins = parse_admin_telegram_ids(get_settings().bot_admin_telegram_ids)
        if telegram_id in admins:
            rows.append([KeyboardButton(text=m.btn_admin)])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True, is_persistent=True)


def admin_reply_keyboard(m: Msg) -> ReplyKeyboardMarkup:
    """Админка: одна reply-кнопка на строку."""
    rows: list[list[KeyboardButton]] = [
        [KeyboardButton(text=m.admin_btn_me_energy)],
        [KeyboardButton(text=m.admin_btn_me_reagents)],
        [KeyboardButton(text=m.admin_btn_me_timer)],
        [KeyboardButton(text=m.admin_btn_main_menu)],
    ]
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True, is_persistent=True)


def invite_contacts_inline_markup(m: Msg) -> InlineKeyboardMarkup:
    """Старые сообщения с inline-кнопкой; колбэк см. invite_contacts_callback."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=m.btn_spread,
                    callback_data=INVITE_CONTACTS_CALLBACK_DATA,
                )
            ]
        ]
    )


def invite_share_inline_markup(
    m: Msg,
    invite_url: str | None,
    *,
    button_text: str | None = None,
    prefill_text: str | None = None,
    share_url: str | None = None,
) -> InlineKeyboardMarkup | None:
    """Кнопка под сообщением: inline → выбор чата → InlineQueryResultPhoto с карточкой."""
    del button_text, prefill_text, share_url
    if not invite_url:
        return None
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=m.btn_spread, switch_inline_query="invite")],
        ]
    )
