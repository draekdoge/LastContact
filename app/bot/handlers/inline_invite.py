import hashlib
import html
from datetime import UTC, datetime

from aiogram import Router
from aiogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InlineQueryResultPhoto,
    InputTextMessageContent,
    LinkPreviewOptions,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards import invite_chain_only_markup
from app.bot.player_card import contact_invite_recipient_caption_html
from app.config import get_settings
from app.db.models import InviteBoost
from app.i18n import get_msg, pick_locale
from app.services.economy_service import boost_payload, is_boost_payload
from app.services.user_service import (
    build_telegram_start_url,
    ensure_referral_token,
    get_user_by_telegram,
)

router = Router(name="inline_invite")


async def _active_boost_for_owner(session: AsyncSession, owner_user_id) -> InviteBoost | None:
    now = datetime.now(UTC)
    return await session.scalar(
        select(InviteBoost)
        .where(
            InviteBoost.owner_user_id == owner_user_id,
            InviteBoost.expires_at > now,
            InviteBoost.uses < InviteBoost.max_uses,
        )
        .order_by(InviteBoost.expires_at.desc())
        .limit(1)
    )


def _boost_invite_caption_html(m, *, sender_disp: str, invite_url: str) -> str:
    """Подпись boost: ссылка только в <code> (копирование тапом)."""
    body = m.boost_share_invite_body_html.format(sender=sender_disp)
    sep = "━━━ · ━━━"
    safe_url = html.escape(invite_url, quote=False)
    return (
        f"{sep}\n\n"
        f"{body}\n\n"
        f"{sep}\n\n"
        f"<b>{m.boost_card_url_hint}</b>\n"
        f"<code>{safe_url}</code>"
    )


async def _boost_by_payload(session: AsyncSession, payload: str) -> InviteBoost | None:
    if not is_boost_payload(payload):
        return None
    token = payload[2:] if payload.startswith("b_") else payload
    now = datetime.now(UTC)
    return await session.scalar(
        select(InviteBoost).where(
            InviteBoost.token == token,
            InviteBoost.expires_at > now,
            InviteBoost.uses < InviteBoost.max_uses,
        )
    )


@router.inline_query()
async def inline_invite(query: InlineQuery, session: AsyncSession) -> None:
    """Inline: обычная рефералка (query invite) или boost (пусто / boost / b_…)."""
    user = await get_user_by_telegram(session, query.from_user.id)
    locale = user.locale if user else pick_locale(query.from_user.language_code)
    m = get_msg(locale)

    me = await query.bot.get_me()
    if user is None or me.username is None:
        await query.answer(results=[], cache_time=1, is_personal=True)
        return

    settings = get_settings()
    qraw = (query.query or "").strip()

    use_boost = False
    boost_row: InviteBoost | None = None
    if not qraw or qraw.casefold() == "boost":
        boost_row = await _active_boost_for_owner(session, user.id)
        use_boost = boost_row is not None
    elif is_boost_payload(qraw):
        cand = await _boost_by_payload(session, qraw)
        if cand is not None and cand.owner_user_id == user.id:
            boost_row = cand
            use_boost = True

    if use_boost and boost_row is not None:
        payload_s = boost_payload(boost_row)
        invite_url = build_telegram_start_url(bot_username=me.username, start_payload=payload_s)
        sender_raw = (query.from_user.first_name or "").strip()
        if not sender_raw and query.from_user.username:
            sender_raw = "@" + query.from_user.username.strip().lstrip("@")
        if not sender_raw:
            sender_raw = {"ru": "Игрок", "uk": "Гравець"}.get(locale, "Player")
        sender_disp = html.escape(sender_raw)
        caption = _boost_invite_caption_html(m, sender_disp=sender_disp, invite_url=invite_url)
        result_id = hashlib.sha256(f"boost:{user.telegram_id}:{payload_s}".encode()).hexdigest()[:32]
        img_b = settings.mini_app_public_url.strip().rstrip("/")
        img = f"{img_b}/assets/referral-card.jpg" if img_b else None
        markup = invite_chain_only_markup(m, invite_url=invite_url)
        if not img:
            result = InlineQueryResultArticle(
                id=result_id,
                title=m.boost_inline_title,
                description=m.boost_inline_description,
                input_message_content=InputTextMessageContent(
                    message_text=caption[:4096],
                    parse_mode="HTML",
                    link_preview_options=LinkPreviewOptions(is_disabled=True),
                ),
                reply_markup=markup,
            )
            await query.answer(results=[result], cache_time=0, is_personal=True)
            return
        result = InlineQueryResultPhoto(
            id=result_id,
            photo_url=img,
            thumbnail_url=img,
            photo_width=640,
            photo_height=640,
            title=m.boost_inline_title,
            description=m.boost_inline_description,
            caption=caption[:1024],
            parse_mode="HTML",
            show_caption_above_media=False,
            reply_markup=markup,
        )
        await query.answer(results=[result], cache_time=0, is_personal=True)
        return

    qnorm = qraw.casefold()
    if qnorm and qnorm not in ("invite", "i"):
        await query.answer(results=[], cache_time=1, is_personal=True)
        return

    token = await ensure_referral_token(session, user)
    invite_url = build_telegram_start_url(bot_username=me.username, start_payload=token)
    result_id = hashlib.sha256(f"{user.telegram_id}:{token}".encode()).hexdigest()[:32]
    sender_disp = (query.from_user.first_name or "").strip()
    if not sender_disp and query.from_user.username:
        sender_disp = "@" + query.from_user.username.strip().lstrip("@")
    bonus_h = float(settings.bonus_hours_per_referral)
    caption = contact_invite_recipient_caption_html(
        m,
        locale=locale,
        invite_url=invite_url,
        bonus_hours=bonus_h,
        sender_display=sender_disp,
    )
    if len(caption) > 1024:
        caption = caption[:1021] + "…"
    markup = invite_chain_only_markup(m, invite_url=invite_url)
    img_b = settings.mini_app_public_url.strip().rstrip("/")
    img = f"{img_b}/assets/referral-card.jpg" if img_b else None
    if not img:
        result = InlineQueryResultArticle(
            id=result_id,
            title=m.mock_header_invite[:64],
            description=m.share_native_prefill[:255],
            input_message_content=InputTextMessageContent(
                message_text=caption[:4096],
                parse_mode="HTML",
                link_preview_options=LinkPreviewOptions(is_disabled=True),
            ),
            reply_markup=markup,
        )
        await query.answer(results=[result], cache_time=0, is_personal=True)
        return
    result = InlineQueryResultPhoto(
        id=result_id,
        photo_url=img,
        thumbnail_url=img,
        photo_width=640,
        photo_height=640,
        title=m.mock_header_invite[:64],
        description=m.share_native_prefill[:255],
        caption=caption,
        parse_mode="HTML",
        show_caption_above_media=False,
        reply_markup=markup,
    )
    await query.answer(results=[result], cache_time=0, is_personal=True)

