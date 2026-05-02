from __future__ import annotations

import html
import re
import secrets
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db.models import Infection, Strain, User
from app.i18n.messages import Msg
from app.services.economy_service import (
    InviteContext,
    InviteEconomyResult,
    apply_invite_economy,
    resolve_invite_context,
)
from app.services.profile_service import apply_telegram_metadata

_LEGACY_REF = re.compile(r"^r(\d+)$")
_TIMER_HISTORY_MAX = 3


def append_timer_history(user: User, delta_h: float, reason: str) -> None:
    """Добавляет событие роста таймера в FIFO-3 список users.timer_history."""
    entry: dict[str, Any] = {
        "delta_h": round(delta_h, 2),
        "reason": reason,
        "ts": datetime.now(UTC).isoformat(),
    }
    history: list[dict[str, Any]] = list(user.timer_history or [])
    history.append(entry)
    user.timer_history = history[-_TIMER_HISTORY_MAX:]


def generate_referral_token_candidate() -> str:
    """32 hex-символа; допустимо в Telegram ?start= (A–Z a–z 0–9 _ -)."""
    return secrets.token_hex(16)


async def allocate_unique_referral_token(session: AsyncSession) -> str:
    for _ in range(24):
        t = generate_referral_token_candidate()
        exists = await session.scalar(select(User.id).where(User.referral_token == t))
        if exists is None:
            return t
    raise RuntimeError("referral_token: не удалось выделить уникальный токен")


async def ensure_referral_token(session: AsyncSession, user: User) -> str:
    if user.referral_token:
        return user.referral_token
    user.referral_token = await allocate_unique_referral_token(session)
    return user.referral_token


async def resolve_inviter_from_start(session: AsyncSession, start_arg: str | None) -> User | None:
    """
    Deep-link: непрозрачный referral_token или легаси r<telegram_id>.
    """
    ctx = await resolve_invite_context(session, start_arg)
    return ctx.inviter if ctx else None


def format_invite_bonus_breakdown(breakdown: dict[str, Any], *, locale: str) -> str:
    total = format_referral_bonus_hms(float(breakdown.get("bonus_hours") or 0))
    base = format_referral_bonus_hms(float(breakdown.get("base_hours") or 0))
    lines = [
        "🧬 Усиленный штамм сработал",
        f"{total} к таймеру",
        f"База: {base}",
    ]
    amp = int(breakdown.get("viral_amplifier_level") or 0)
    if amp:
        lines.append(f"Вирусный усилитель L{amp}: x{1 + 0.10 * amp:.2f}")
    boost_label = breakdown.get("boost_label")
    if boost_label:
        lines.append(f"{html.escape(str(boost_label))}: boosted link")
    mut = int(breakdown.get("mutation_multiplier") or 1)
    if mut > 1:
        lines.append(f"Мутация: x{mut}")
    lines.append(f"Кликер: +{int(breakdown.get('clicker_max_energy_bonus') or 0)} энергии к максимуму")
    regen = int(breakdown.get("clicker_regen_bonus_bps") or 0)
    if regen:
        h = float(get_settings().invite_regen_boost_hours)
        lines.append(f"Реген (временный ~{h:g} ч): +{regen / 100:.2f}%")
    return "\n".join(lines)


async def _chain_depth_for_infector(session: AsyncSession, infector: User) -> int:
    row = await session.scalar(select(Infection).where(Infection.infected_user_id == infector.id))
    if row is None:
        return 1
    return row.chain_depth + 1


async def _increment_ancestor_subtrees(session: AsyncSession, infector: User) -> None:
    current: User | None = infector
    while current is not None:
        current.subtree_infections_count += 1
        if current.infected_by_user_id is None:
            break
        current = await session.get(User, current.infected_by_user_id)


def format_referral_bonus_hms(hours: float) -> str:
    """Бонус реферера в пуше: +H:MM:SS (из дробных часов, например 3.0 → +3:00:00)."""
    total_seconds = max(0, int(round(float(hours) * 3600)))
    h, rem = divmod(total_seconds, 3600)
    min_, s = divmod(rem, 60)
    return f"+{h:d}:{min_:02d}:{s:02d}"


def format_timer_line(user: User, m: Msg) -> str:
    now = datetime.now(UTC)
    if user.state == "zombie":
        return m.timer_zombie
    if user.state == "immune":
        if user.immune_ends_at is None or now >= user.immune_ends_at:
            return m.timer_expired_pending
        left = user.immune_ends_at - now
        h, rem = divmod(int(left.total_seconds()), 3600)
        min_, s = divmod(rem, 60)
        return m.timer_immune_line.format(time_str=f"{h:02d}:{min_:02d}:{s:02d}")
    if user.timer_ends_at is None:
        return m.timer_inactive
    if now >= user.timer_ends_at:
        if user.state == "infected":
            return m.timer_zombie_transition_pending
        return m.timer_expired_pending
    left = user.timer_ends_at - now
    h, rem = divmod(int(left.total_seconds()), 3600)
    min_, s = divmod(rem, 60)
    return f"{m.timer_countdown}: {h:02d}:{min_:02d}:{s:02d}"


def _green_shield_bar(filled: int, bar_width: int) -> str:
    empty = bar_width - filled
    parts: list[str] = []
    for i in range(filled):
        if filled <= 1:
            parts.append("🟩")
        else:
            t = i / (filled - 1)
            parts.append("🟩" if t < 0.5 else "🟨")
    parts.extend("⬜" * max(0, empty))
    return "".join(parts)


def _orange_gradient_bar(filled: int, bar_width: int) -> str:
    """Псевдо-градиент: красный квадрат → оранжевый → жёлтый (Telegram без CSS)."""
    empty = bar_width - filled
    parts: list[str] = []
    for i in range(filled):
        if filled <= 1:
            parts.append("🟧")
        else:
            t = i / (filled - 1)
            parts.append("🟥" if t < 0.35 else "🟧" if t < 0.75 else "🟨")
    parts.extend("⬜" * max(0, empty))
    return "".join(parts)


def format_timer_block(user: User, m: Msg, *, bar_width: int = 10) -> str:
    """Иммунитет: зелёная полоса. Зомби: полоса некроза. Активный infected: оранжевая полоса + таймер."""
    now = datetime.now(UTC)
    settings = get_settings()

    if user.state == "immune" and user.immune_ends_at is not None and now < user.immune_ends_at:
        left = max(0.0, (user.immune_ends_at - now).total_seconds())
        span = max(60.0, settings.immune_duration_hours * 3600)
        ratio = min(1.0, left / span)
        filled = min(bar_width, max(0, int(round(ratio * bar_width))))
        bar = _green_shield_bar(filled, bar_width)
        pct = max(0, min(100, int(round(ratio * 100))))
        h, rem = divmod(int(left), 3600)
        min_, s = divmod(rem, 60)
        time_str = f"{h:02d}:{min_:02d}:{s:02d}"
        reserve = html.escape(m.mock_immune_vita_label)
        decay = html.escape(m.mock_immune_decay_label)
        return (
            f"{bar} <b>{pct}%</b> <b>{reserve}</b>\n"
            f"⏱ <code>{html.escape(time_str)}</code> · {decay}"
        )

    if user.state == "zombie":
        return m.zombie_timer_strip

    if (
        user.state == "infected"
        and user.timer_ends_at is not None
        and now >= user.timer_ends_at
    ):
        return m.timer_zombie_transition_pending

    line_plain = format_timer_line(user, m)

    if (
        user.timer_ends_at is None
        or user.state not in ("infected",)
        or now >= user.timer_ends_at
    ):
        return line_plain

    left = max(0.0, (user.timer_ends_at - now).total_seconds())
    span = max(60.0, (user.timer_ends_at - user.created_at).total_seconds())
    ratio = min(1.0, left / span)
    filled = min(bar_width, max(0, int(round(ratio * bar_width))))
    bar = _orange_gradient_bar(filled, bar_width)
    pct = max(0, min(100, int(round(ratio * 100))))
    h, rem = divmod(int(left), 3600)
    min_, s = divmod(rem, 60)
    time_str = f"{h:02d}:{min_:02d}:{s:02d}"
    reserve = html.escape(m.mock_vita_label)
    decay = html.escape(m.mock_decay_label)
    timer_line = (
        f"{bar} <b>{pct}%</b> <b>{reserve}</b>\n"
        f"⏱ <code>{time_str}</code> · {decay}"
    )
    history_block = _format_history_block(user)
    if history_block:
        return f"{timer_line}\n{history_block}"
    return timer_line


def _format_history_block(user: User) -> str:
    """Последние 3 события роста таймера в виде дерева (ASCII-ветки)."""
    history = user.timer_history
    if not history:
        return ""
    lines: list[str] = []
    for i, entry in enumerate(history):
        try:
            delta_h = float(entry.get("delta_h", 0))
            reason = str(entry.get("reason", ""))
            ts_raw = entry.get("ts", "")
            ts_label = ""
            if ts_raw:
                try:
                    dt = datetime.fromisoformat(ts_raw)
                    ts_label = f" ({dt.strftime('%H:%M')})"
                except ValueError:
                    pass
            sign = "└" if i == len(history) - 1 else "├"
            delta_str = f"+{delta_h:g} ч"
            lines.append(
                f"  {sign} <code>{delta_str}</code>  {html.escape(reason)}{ts_label}"
            )
        except (TypeError, KeyError):
            continue
    return "\n".join(lines)


def build_telegram_start_url(*, bot_username: str, start_payload: str) -> str:
    u = bot_username.lstrip("@")
    return f"https://t.me/{u}?start={start_payload}"


def format_user_handle_or_name(*, username: str | None, first_name: str | None, telegram_id: int) -> str:
    """
    Безопасный ярлык пользователя для текста/логов.
    - Если есть username → "@username"
    - Иначе если есть first_name → "Имя"
    - Иначе → "user#<telegram_id>"
    """
    un = (username or "").strip().lstrip("@")
    if un:
        return f"@{un}"
    fn = (first_name or "").strip()
    if fn:
        return fn
    return f"user#{telegram_id}"


async def register_new_infected(
    session: AsyncSession,
    *,
    telegram_id: int,
    inviter: User | None = None,
    invite_context: InviteContext | None = None,
    language_code: str | None = None,
    username: str | None = None,
    first_name: str | None = None,
) -> tuple[User, bool, InviteEconomyResult | None]:
    """
    Создаёт нового игрока в ветке вируса.

    Returns:
        (user, created) — created всегда True здесь; оставлено для симметрии API.
    """
    settings = get_settings()
    hours = settings.launch_timer_hours if settings.launch_mode else settings.default_timer_hours
    ends = datetime.now(UTC) + timedelta(hours=hours)

    infector: User | None = None
    effective_inviter = invite_context.inviter if invite_context is not None else inviter
    if effective_inviter is not None and effective_inviter.telegram_id != telegram_id:
        infector = effective_inviter

    # Штамм: organic создаёт новый, иначе наследуем от заражающего.
    strain_id: uuid.UUID
    if infector is not None:
        strain_id = infector.strain_id
    else:
        strain_id = uuid.uuid4()

    ref_tok = await allocate_unique_referral_token(session)
    user_id = uuid.uuid4()
    user = User(
        id=user_id,
        telegram_id=telegram_id,
        referral_token=ref_tok,
        side="virus",
        state="infected",
        infected_by_user_id=infector.id if infector else None,
        strain_id=strain_id,
        timer_ends_at=ends,
        lab_sample_collection={},
    )
    apply_telegram_metadata(
        user,
        language_code=language_code,
        username=username,
        first_name=first_name,
    )
    session.add(user)
    await session.flush()

    # Для organic: создаём strain после flush user, чтобы FK root_user_id гарантированно существовал.
    if infector is None:
        code = f"X-{strain_id.hex[:6].upper()}"
        # "покрасивее": лёгкая стилизация, но без зависимости от LLM.
        title = f"Штамм {code} «Нулевой Пациент»"
        session.add(
            Strain(
                id=strain_id,
                code=code,
                title=title,
                root_user_id=user_id,
            )
        )
        await session.flush()

    if infector:
        depth = await _chain_depth_for_infector(session, infector)
        session.add(
            Infection(
                infector_user_id=infector.id,
                infected_user_id=user.id,
                strength=1.0,
                chain_depth=depth,
            )
        )
        infector.direct_infections_count += 1
        await _increment_ancestor_subtrees(session, infector)

        now = datetime.now(UTC)
        infector.last_spread_at = now
        if infector.state == "infected" and infector.timer_ends_at is not None:
            economy = apply_invite_economy(
                infector,
                base_bonus_hours=float(settings.bonus_hours_per_referral),
                invite_context=invite_context,
            )
            infector.timer_ends_at += timedelta(seconds=economy.total_seconds)
            infector.timer_alert_level = 0
            ref_label = format_user_handle_or_name(
                username=username, first_name=first_name, telegram_id=telegram_id
            )
            append_timer_history(infector, economy.total_seconds / 3600, f"реферал {ref_label}")
        else:
            economy = apply_invite_economy(
                infector,
                base_bonus_hours=float(settings.bonus_hours_per_referral),
                invite_context=invite_context,
            )
            economy.got_timer_bonus = False

    return user, True, economy if infector else None


def apply_immunity_recovery(user: User) -> bool:
    """Зомби → иммунитет на immune_duration_hours. False, если не зомби."""
    if user.state != "zombie":
        return False
    settings = get_settings()
    user.state = "immune"
    user.immune_ends_at = datetime.now(UTC) + timedelta(hours=settings.immune_duration_hours)
    user.timer_alert_level = 0
    return True


async def get_user_by_telegram(session: AsyncSession, telegram_id: int) -> User | None:
    return await session.scalar(select(User).where(User.telegram_id == telegram_id))
