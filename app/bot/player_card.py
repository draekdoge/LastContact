"""Разметка карточек игрока (HTML) — без пунктирных разделителей (не переносятся на узких экранах)."""

from __future__ import annotations

import hashlib
import html

from aiogram.types import User as TgUser

from app.db.models import User
from app.i18n.messages import Msg
from app.services.user_service import format_timer_block


def zombie_transformation_html(user: User, m: Msg, fu: TgUser | None = None) -> str:
    """Карточка в духе SCREEN 06 после перехода в зомби (пуш sweep / полная карточка)."""
    banner = f"<b>{html.escape(m.zombie_screen06_banner)}</b>"
    head = f"<b>{html.escape(m.zombie_card_header)}</b>"
    if fu is not None:
        name = display_name(fu)
        if name:
            head = f"{head}\n{name}"
    zbody = m.zombie_card_body
    if "{chain_total}" in zbody:
        body = zbody.format(chain_total=user.subtree_infections_count)
    else:
        body = zbody
    rank_dash = html.escape("—")
    stats_block = (
        f"<b>{user.direct_infections_count}</b> {m.mock_stat_ab_direct}\n"
        f"<b>{user.subtree_infections_count}</b> {m.mock_stat_ab_net}\n"
        f"{html.escape(m.mock_stat_ab_sector)}: <b>{rank_dash}</b>"
    )
    return "\n\n".join(
        [
            banner,
            head,
            body,
            m.zombie_card_hint,
            m.zombie_timer_strip,
            m.zombie_badges_line,
            stats_block,
        ]
    )


def display_name(fu: TgUser) -> str:
    fn = (fu.first_name or "").strip()
    return html.escape(fn) if fn else ""


def newcomer_html_mention(fu: TgUser) -> str:
    """Краткое обращение к новому игроку для пуша рефереру (HTML)."""
    un = (fu.username or "").strip().lstrip("@")
    if un:
        safe = html.escape(un, quote=True)
        vis = html.escape(un)
        return f'<a href="https://t.me/{safe}">@{vis}</a>'
    fn = (fu.first_name or "").strip()
    if fn:
        return f"<b>{html.escape(fn)}</b>"
    return f"<code>{fu.id}</code>"


def _hours_phrase(locale: str, hours: float) -> str:
    """«12 часов» / «12 hours» и т.д. для строки как в SCREEN 01."""
    n = int(round(hours))
    primary = (locale or "ru").split("-")[0].lower()

    if primary == "ru":
        if n % 10 == 1 and n % 100 != 11:
            return f"{n} час"
        if 2 <= n % 10 <= 4 and not (12 <= n % 100 <= 14):
            return f"{n} часа"
        return f"{n} часов"
    if primary == "uk":
        if n % 10 == 1 and n % 100 != 11:
            return f"{n} година"
        if 2 <= n % 10 <= 4 and not (12 <= n % 100 <= 14):
            return f"{n} години"
        return f"{n} годин"
    if primary == "en":
        return f"{n} hour" if n == 1 else f"{n} hours"
    if primary == "de":
        return f"{n} Stunde" if n == 1 else f"{n} Stunden"
    if primary in ("es", "pt"):
        return f"{n} hora" if n == 1 else f"{n} horas"
    if primary == "ko":
        return f"{n}시간"
    if primary == "ja":
        return f"{n}時間"
    if primary == "zh":
        return f"{n}小时"
    return f"{n} h"


def new_player_welcome_html(
    m: Msg,
    fu: TgUser,
    *,
    locale: str,
    organic: bool,
    initial_timer_hours: float,
    timer_block: str,
    link_block: str,
) -> str:
    name = display_name(fu)
    head = f"<b>{html.escape(m.mock_header_new)}</b>"
    if name:
        head = f"{head}\n{name}"
    if organic:
        phrase = html.escape(_hours_phrase(locale, initial_timer_hours))
        body = m.mock_body_new_organic.format(timer_hours_phrase=phrase)
    else:
        body = m.mock_body_new_referral
    return f"{head}\n\n{body}\n\n{timer_block}\n\n{m.mock_badges_new}\n\n{link_block}"


def infected_dashboard_html(user: User, m: Msg, fu: TgUser, *, status_header: str) -> str:
    if user.state == "zombie":
        return zombie_transformation_html(user, m, fu)
    name = display_name(fu)
    if user.state == "immune":
        head = f"<b>{html.escape(m.mock_header_immune)}</b>"
        body = m.mock_body_immune
    else:
        head = f"<b>{html.escape(status_header)}</b>"
        body = m.mock_body_return.format(network=user.subtree_infections_count)
    if name:
        head = f"{head}\n{name}"
    timer_part = format_timer_block(user, m)
    rank_dash = html.escape("—")
    stats_block = (
        f"<b>{user.direct_infections_count}</b> {m.mock_stat_ab_direct}\n"
        f"<b>{user.subtree_infections_count}</b> {m.mock_stat_ab_net}\n"
        f"{html.escape(m.mock_stat_ab_sector)}: <b>{rank_dash}</b>"
    )
    return f"{head}\n\n{body}\n\n{timer_part}\n\n{stats_block}"


def returning_player_html(user: User, m: Msg, fu: TgUser) -> str:
    return infected_dashboard_html(user, m, fu, status_header=m.mock_header_return)


def own_invite_message_html(m: Msg, invite_url: str, *, bonus_hours: float) -> str:
    """Экран отправителя: ссылка в <code> — тап копирует; только t.me deep link."""
    safe_url = html.escape(invite_url, quote=False)
    label = html.escape(m.invite_link_box_label)
    share = m.share_title.format(bonus_hours=float(bonus_hours))
    return (
        f"<b>{html.escape(m.mock_header_invite)}</b>\n\n"
        f"{share}\n\n"
        f"<b>{label}</b>\n"
        f"<code>{safe_url}</code>"
    )


_INVITE_TEXT_VARIANTS_RU = (
    "Вход в цепочку открыт.\nПроверь, не ты ли следующий носитель.",
    "У тебя есть доступ к заражённой цепи.\nОткрой и займи место в сети.",
    "Меня уже вписали в цепочку. Открой — узнаешь, не ты ли следующий.",
)


def invite_recipient_lead_html(locale: str, *, sender_name: str) -> str:
    """Лид для карточки у контакта (HTML)."""
    primary = (locale or "en").split("-")[0].lower()
    sender_esc = html.escape(sender_name.strip()) if sender_name.strip() else ""
    if primary == "ru":
        seed = (sender_name or "ru").encode("utf-8")
        idx = int(hashlib.sha256(seed).hexdigest(), 16) % len(_INVITE_TEXT_VARIANTS_RU)
        variant = html.escape(_INVITE_TEXT_VARIANTS_RU[idx])
        if sender_esc:
            return f"{sender_esc} передаёт тебе штамм.\n\n{variant}"
        return variant
    if sender_esc:
        return (
            f"{sender_esc} invited you to the strain chain.\n\n"
            "Open the bot via the button below and join."
        )
    return "You are invited to the strain chain. Open the bot via the button below and join."


def contact_invite_recipient_caption_html(
    m: Msg,
    *,
    locale: str,
    invite_url: str,
    bonus_hours: float,
    sender_display: str,
) -> str:
    """Карточка контакту: лид + бонус отправителю + реферальная ссылка отправителя в <code> (копирование тапом)."""
    lead = invite_recipient_lead_html(locale, sender_name=sender_display)
    bonus_line = m.invite_share_bonus_for_inviter_line.format(bonus_hours=float(bonus_hours))
    sep = "━━━ · ━━━"
    safe_url = html.escape(invite_url, quote=False)
    label = html.escape(m.invite_link_box_label)
    return (
        f"{lead}\n\n"
        f"{sep}\n\n"
        f"{bonus_line}\n\n"
        f"{sep}\n\n"
        f"<b>{label}</b>\n"
        f"<code>{safe_url}</code>"
    )
