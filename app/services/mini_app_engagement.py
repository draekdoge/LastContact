"""Первый заход в Mini App: только метка времени (счётчики «онлайн» — в mini_app_presence)."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User


async def ensure_mini_app_engagement(session: AsyncSession, user: User, now: datetime) -> bool:
    """
    Возвращает True, если выставлен впервые mini_app_first_seen_at.

    Реген сети считается только по окну онлайна (last_seen), не по этому флагу.
    """
    if user.mini_app_first_seen_at is not None:
        return False
    user.mini_app_first_seen_at = now
    return True
