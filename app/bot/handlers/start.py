import html
import logging
from pathlib import Path

from aiogram import Bot, F, Router
from aiogram.filters import CommandObject, CommandStart
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    LinkPreviewOptions,
    Message,
    ReplyKeyboardMarkup,
    FSInputFile,
    User as TgUser,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards import (
    INVITE_CONTACTS_CALLBACK_DATA,
    invite_share_inline_markup,
    main_reply_keyboard,
)
from app.bot.timer_extend_followup import send_timer_extend_sources_message
from app.bot.player_card import (
    newcomer_html_mention,
    new_player_welcome_html,
    own_invite_message_html,
    returning_player_html,
)
from app.config import get_settings
from app.services.economy_service import resolve_invite_context
from app.i18n import (
    BACK_BUTTON_TEXTS,
    MENU_BUTTON_TEXTS,
    REFRESH_TIME_BUTTON_TEXTS,
    SPREAD_BUTTON_TEXTS,
    get_msg,
    pick_locale,
)
from app.db.models import User
from app.services.profile_service import apply_telegram_metadata, refresh_avatar_if_needed
from app.services.user_service import (
    build_telegram_start_url,
    ensure_referral_token,
    format_referral_bonus_hms,
    format_invite_bonus_breakdown,
    format_timer_block,
    get_user_by_telegram,
    register_new_infected,
)

router = Router(name="start")

logger = logging.getLogger(__name__)

_LINK_PREVIEW_OFF = LinkPreviewOptions(is_disabled=True)

_BIDI_TRIM = dict.fromkeys(map(ord, "\u200e\u200f\u200b\u202a\u202b\u202c\u202d\u202e"), None)
_REFERRAL_CARD_PATH = Path(__file__).resolve().parents[2] / "mini_app" / "static" / "referral-card.jpg"
_SPREAD_TEXT_ALIASES_CF = frozenset(
    {
        "передать штамм",
        "передать штамп",
        "отправить заражение",
    }
)


def _normalize_button_text(text: str) -> str:
    """Нормализация текста кнопки: trim/bidi + единые пробелы + без variation selector."""
    compact = " ".join(text.strip().translate(_BIDI_TRIM).split())
    return compact.replace("\ufe0f", "")


def _spread_tail_casefold(text: str) -> str:
    t = _normalize_button_text(text)
    if t.startswith("☣"):
        t = t[1:].strip()
    return t.casefold()


_SPREAD_BUTTON_TEXTS_NORMALIZED = frozenset(_normalize_button_text(lbl) for lbl in SPREAD_BUTTON_TEXTS)
_SPREAD_BUTTON_TAILS_CF = frozenset(_spread_tail_casefold(lbl) for lbl in SPREAD_BUTTON_TEXTS)


def _is_spread_reply_text(text: str | None) -> bool:
    """Текст reply-кнопки «Передать штамм»: точное совпадение + trim bidi + тот же текст в другом регистре (EN)."""
    if not text:
        return False
    t = _normalize_button_text(text)
    if t in _SPREAD_BUTTON_TEXTS_NORMALIZED:
        return True
    tail_cf = _spread_tail_casefold(t)
    return tail_cf in _SPREAD_BUTTON_TAILS_CF or tail_cf in _SPREAD_TEXT_ALIASES_CF


async def _answer_card(
    message: Message,
    text: str,
    *,
    reply_markup: ReplyKeyboardMarkup | InlineKeyboardMarkup,
    photo_file_id: str | None,
) -> Message:
    common = {
        "reply_markup": reply_markup,
        "link_preview_options": _LINK_PREVIEW_OFF,
    }
    if photo_file_id:
        return await message.answer_photo(
            photo_file_id,
            caption=text,
            **common,
        )
    return await message.answer(text, **common)


async def _answer_start_dashboard(
    message: Message,
    body: str,
    m,
    photo_file_id: str | None,
    user: User,
) -> None:
    """Карточка + нижнее меню; id сообщения сохраняем — при «Передать штамм» удалим и отправим код."""
    sent = await _answer_card(
        message,
        body,
        reply_markup=main_reply_keyboard(m, telegram_id=user.telegram_id),
        photo_file_id=photo_file_id,
    )
    user.last_card_message_id = sent.message_id


async def _send_spread_invite(
    bot: Bot,
    chat_id: int,
    session: AsyncSession,
    *,
    telegram_id: int,
    language_code: str | None,
    business_connection_id: str | None = None,
) -> bool:
    """Отправить экран «код распространения». Карточка дашборда в чате не удаляется — «Назад» убирает только это сообщение."""
    u = await get_user_by_telegram(session, telegram_id)
    m = get_msg(u.locale if u else pick_locale(language_code))

    me = await bot.get_me()
    if me.username is None:
        await bot.send_message(
            chat_id,
            m.share_no_username,
            business_connection_id=business_connection_id,
            link_preview_options=_LINK_PREVIEW_OFF,
        )
        return False
    if u is None:
        await bot.send_message(
            chat_id,
            m.share_no_username,
            business_connection_id=business_connection_id,
            link_preview_options=_LINK_PREVIEW_OFF,
        )
        return False
    tok = await ensure_referral_token(session, u)
    url = build_telegram_start_url(bot_username=me.username, start_payload=tok)
    share_markup = invite_share_inline_markup(m, url)
    _invite_extra_msg: dict = {
        "business_connection_id": business_connection_id,
        "link_preview_options": _LINK_PREVIEW_OFF,
        "parse_mode": "HTML",
    }
    _invite_extra_photo: dict = {
        "business_connection_id": business_connection_id,
        "parse_mode": "HTML",
    }
    if share_markup is not None:
        _invite_extra_msg["reply_markup"] = share_markup
        _invite_extra_photo["reply_markup"] = share_markup
    text = own_invite_message_html(m, url, bonus_hours=get_settings().bonus_hours_per_referral)
    if len(text) > 1024:
        text = text[:1021] + "…"
    if _REFERRAL_CARD_PATH.is_file():
        await bot.send_photo(
            chat_id,
            photo=FSInputFile(str(_REFERRAL_CARD_PATH)),
            caption=text,
            **_invite_extra_photo,
        )
    else:
        await bot.send_message(chat_id, text, **_invite_extra_msg)
    return True


async def _notify_inviter_new_carrier(
    bot: Bot,
    *,
    inviter: User,
    newcomer: TgUser,
    bonus_hours: float,
    breakdown: dict | None = None,
) -> None:
    """Пуш пригласившему: новый носитель по ссылке (+ч к таймеру, если ещё infected)."""
    if inviter.telegram_id == newcomer.id:
        return
    m = get_msg(inviter.locale)
    nh = newcomer_html_mention(newcomer)
    got_bonus = inviter.state == "infected" and inviter.timer_ends_at is not None
    if breakdown is None:
        bonus_block = (
            m.referral_timer_bonus.format(bonus_hms=format_referral_bonus_hms(bonus_hours))
            if got_bonus
            else ""
        )
    else:
        bonus_block = format_invite_bonus_breakdown(breakdown, locale=inviter.locale) if got_bonus else ""
    text = m.referral_new_carrier.format(
        newcomer=nh,
        bonus_block=bonus_block,
        branch_total=int(inviter.subtree_infections_count),
    )
    try:
        await bot.send_message(
            inviter.telegram_id,
            text,
            link_preview_options=_LINK_PREVIEW_OFF,
        )
    except Exception as exc:
        logger.warning(
            "referral notify failed inviter_tg=%s: %s",
            inviter.telegram_id,
            exc,
        )


def _invite_html(bot_username: str, token: str, m) -> str:
    url = build_telegram_start_url(bot_username=bot_username, start_payload=token)
    safe_url = html.escape(url, quote=False)
    label = html.escape(m.invite_link_box_label)
    return f"<b>{label}</b>\n<code>{safe_url}</code>"


@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject, session: AsyncSession) -> None:
    if message.from_user is None:
        return

    fu = message.from_user
    uid = fu.id
    invite_context = await resolve_invite_context(session, command.args)
    inviter = invite_context.inviter
    if inviter is not None and inviter.telegram_id == uid:
        invite_context.inviter = None
        invite_context.boost = None
        inviter = None

    existing = await get_user_by_telegram(session, uid)
    if existing:
        apply_telegram_metadata(
            existing,
            language_code=fu.language_code,
            username=fu.username,
            first_name=fu.first_name,
        )
        await refresh_avatar_if_needed(message.bot, existing)
        await ensure_referral_token(session, existing)
        m = get_msg(existing.locale)

        if inviter is not None and inviter.telegram_id != uid:
            await message.answer(
                m.already_in_game_reinfect,
                reply_markup=main_reply_keyboard(m, telegram_id=existing.telegram_id),
                link_preview_options=_LINK_PREVIEW_OFF,
            )
            return

        start_arg = (command.args or "").strip()
        if start_arg and existing.referral_token == start_arg:
            me = await message.bot.get_me()
            if me.username is None:
                await message.answer(m.share_no_username, link_preview_options=_LINK_PREVIEW_OFF)
                return
            url = build_telegram_start_url(bot_username=me.username, start_payload=existing.referral_token)
            _sm = invite_share_inline_markup(m, url)
            _start_inv_extra: dict = {
                "link_preview_options": _LINK_PREVIEW_OFF,
                "parse_mode": "HTML",
            }
            if _sm is not None:
                _start_inv_extra["reply_markup"] = _sm
            _body = own_invite_message_html(m, url, bonus_hours=get_settings().bonus_hours_per_referral)
            if len(_body) > 4096:
                _body = _body[:4093] + "…"
            await message.answer(
                _body,
                **_start_inv_extra,
            )
            return

        settings = get_settings()
        body = returning_player_html(existing, m, fu)
        dashboard_photo = (
            None if existing.state == "zombie" else existing.avatar_small_file_id
        )
        await _answer_start_dashboard(
            message,
            body,
            m,
            dashboard_photo,
            existing,
        )
        await send_timer_extend_sources_message(
            message,
            existing,
            m,
            bonus_hours=float(settings.bonus_hours_per_referral),
        )
        return

    user, _, invite_result = await register_new_infected(
        session,
        telegram_id=uid,
        invite_context=invite_context,
        language_code=fu.language_code,
        username=fu.username,
        first_name=fu.first_name,
    )
    await refresh_avatar_if_needed(message.bot, user)
    m = get_msg(user.locale)
    settings = get_settings()
    init_hours = settings.launch_timer_hours if settings.launch_mode else settings.default_timer_hours

    me = await message.bot.get_me()
    if me.username is None:
        link_block = m.welcome_no_bot_username
    else:
        tok = await ensure_referral_token(session, user)
        link_block = _invite_html(me.username, tok, m)

    organic = user.infected_by_user_id is None
    timer_part = format_timer_block(user, m)
    text = new_player_welcome_html(
        m,
        fu,
        locale=user.locale,
        organic=organic,
        initial_timer_hours=init_hours,
        timer_block=timer_part,
        link_block=link_block,
    )
    await _answer_start_dashboard(
        message,
        text,
        m,
        user.avatar_small_file_id,
        user,
    )
    await send_timer_extend_sources_message(
        message,
        user,
        m,
        bonus_hours=float(settings.bonus_hours_per_referral),
    )

    if inviter is not None:
        await _notify_inviter_new_carrier(
            message.bot,
            inviter=inviter,
            newcomer=fu,
            bonus_hours=invite_result.bonus_hours if invite_result else settings.bonus_hours_per_referral,
            breakdown=invite_result.breakdown if invite_result else None,
        )


@router.message(F.text.in_(BACK_BUTTON_TEXTS))
async def back_to_main_menu(message: Message, session: AsyncSession) -> None:
    """С дочерней клавиатуры (передача штамма) — вернуть полное меню."""
    if message.from_user is None:
        return
    u = await get_user_by_telegram(session, message.from_user.id)
    m = get_msg(u.locale if u else pick_locale(message.from_user.language_code))
    if u is None:
        await message.answer(m.status_use_start, link_preview_options=_LINK_PREVIEW_OFF)
        return
    await message.answer(
        m.back_to_main_ack,
        reply_markup=main_reply_keyboard(m, telegram_id=message.from_user.id),
        link_preview_options=_LINK_PREVIEW_OFF,
    )


@router.message(F.text.in_(MENU_BUTTON_TEXTS))
async def menu_placeholders(message: Message, session: AsyncSession) -> None:
    if message.from_user is None:
        return
    u = await get_user_by_telegram(session, message.from_user.id)
    m = get_msg(u.locale if u else pick_locale(message.from_user.language_code))
    if get_settings().mini_app_public_url.strip():
        body = m.menu_open_mini_hint
    else:
        body = m.stub_feature_soon
    await message.answer(
        body,
        reply_markup=main_reply_keyboard(m, telegram_id=message.from_user.id) if u else None,
        link_preview_options=_LINK_PREVIEW_OFF,
    )


@router.message(lambda m: _is_spread_reply_text(m.text))
async def share_invite(message: Message, session: AsyncSession) -> None:
    if message.from_user is None:
        return
    fu = message.from_user
    if message.chat is None:
        return
    biz = getattr(message, "business_connection_id", None)
    u = await get_user_by_telegram(session, fu.id)
    try:
        ok = await _send_spread_invite(
            message.bot,
            message.chat.id,
            session,
            telegram_id=fu.id,
            language_code=fu.language_code,
            business_connection_id=biz,
        )
    except Exception:
        logger.exception("share_invite: не удалось отправить приглашение")
        m = get_msg(u.locale if u else pick_locale(fu.language_code))
        await message.bot.send_message(
            message.chat.id,
            m.spread_open_failed,
            business_connection_id=biz,
            link_preview_options=_LINK_PREVIEW_OFF,
        )


@router.callback_query(F.data == INVITE_CONTACTS_CALLBACK_DATA)
async def invite_contacts_callback(query: CallbackQuery, session: AsyncSession) -> None:
    """Старые сообщения с callback: выдать inline-кнопку «Передать штамм» (switch_inline_query)."""
    await query.answer()
    if query.from_user is None or query.message is None:
        return
    try:
        u = await get_user_by_telegram(session, query.from_user.id)
        m = get_msg(u.locale if u else pick_locale(query.from_user.language_code))
        me = await query.bot.get_me()
        invite_url: str | None = None
        if me.username and u is not None:
            tok = await ensure_referral_token(session, u)
            invite_url = build_telegram_start_url(bot_username=me.username, start_payload=tok)
        biz = getattr(query, "business_connection_id", None)
        _ct_extra: dict = {
            "business_connection_id": biz,
            "link_preview_options": _LINK_PREVIEW_OFF,
            "parse_mode": "HTML",
        }
        _sm = invite_share_inline_markup(m, invite_url)
        if _sm is not None:
            _ct_extra["reply_markup"] = _sm
        await query.message.answer(m.invite_bottom_keyboard_prompt, **_ct_extra)
    except Exception:
        logger.exception("invite_contacts_callback: не удалось отправить клавиатуру")


@router.message(F.text.in_(REFRESH_TIME_BUTTON_TEXTS))
async def refresh_remain(message: Message, session: AsyncSession) -> None:
    if message.from_user is None:
        return
    u = await get_user_by_telegram(session, message.from_user.id)
    m = get_msg(u.locale if u else pick_locale(message.from_user.language_code))
    if u is None:
        await message.answer(m.status_use_start, link_preview_options=_LINK_PREVIEW_OFF)
        return
    settings = get_settings()
    tb = format_timer_block(u, m)
    await message.answer(
        tb,
        reply_markup=main_reply_keyboard(m, telegram_id=message.from_user.id),
        link_preview_options=_LINK_PREVIEW_OFF,
    )
    await send_timer_extend_sources_message(
        message,
        u,
        m,
        bonus_hours=float(settings.bonus_hours_per_referral),
    )
