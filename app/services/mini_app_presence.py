"""Онлайн Mini App: last_seen, пересчёт кэшей сетевого регена для себя и предков."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db.models import User
from app.services.mini_app_engagement import ensure_mini_app_engagement


async def _count_online_descendants_for_owner(
    session: AsyncSession,
    owner_id: uuid.UUID,
    cutoff: datetime,
) -> tuple[int, int]:
    direct = int(
        await session.scalar(
            select(func.count())
            .select_from(User)
            .where(
                User.infected_by_user_id == owner_id,
                User.mini_app_last_seen_at.is_not(None),
                User.mini_app_last_seen_at > cutoff,
            )
        )
        or 0
    )
    sub_raw = await session.scalar(
        text(
            """
            WITH RECURSIVE down AS (
                SELECT id FROM users WHERE infected_by_user_id = :uid
                UNION ALL
                SELECT u.id FROM users u INNER JOIN down d ON u.infected_by_user_id = d.id
            )
            SELECT count(*)::int FROM down d
            INNER JOIN users u ON u.id = d.id
            WHERE u.mini_app_last_seen_at IS NOT NULL AND u.mini_app_last_seen_at > :cutoff
            """
        ),
        {"uid": owner_id, "cutoff": cutoff},
    )
    subtree = int(sub_raw or 0)
    return direct, subtree


async def refresh_mini_regen_online_for_user_and_ancestors(
    session: AsyncSession,
    user: User,
    now: datetime,
) -> None:
    settings = get_settings()
    cutoff = now - timedelta(seconds=int(settings.mini_app_online_presence_seconds))
    user.mini_app_last_seen_at = now

    d, sub = await _count_online_descendants_for_owner(session, user.id, cutoff)
    user.mini_regen_online_direct = d
    user.mini_regen_online_subtree = sub

    pid: uuid.UUID | None = user.infected_by_user_id
    while pid is not None:
        anc = await session.get(User, pid)
        if anc is None:
            break
        d_a, sub_a = await _count_online_descendants_for_owner(session, anc.id, cutoff)
        anc.mini_regen_online_direct = d_a
        anc.mini_regen_online_subtree = sub_a
        pid = anc.infected_by_user_id


async def sync_mini_app_engagement_and_presence(
    session: AsyncSession,
    user: User,
    now: datetime,
) -> bool:
    """Первый визит (first_seen) + актуальные last_seen и кэши «онлайн» по дереву. Возвращает True, если меняли first_seen."""
    first_engagement = await ensure_mini_app_engagement(session, user, now)
    await refresh_mini_regen_online_for_user_and_ancestors(session, user, now)
    return first_engagement
