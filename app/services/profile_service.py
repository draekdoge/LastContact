"""Профиль из Telegram: язык, страна (эвристика), аватар."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aiogram import Bot

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.i18n import pick_locale

logger = logging.getLogger(__name__)

# Язык Telegram → предполагаемая страна (ISO 3166-1 alpha-2). None — неоднозначно.
_LANG_PRIMARY_TO_COUNTRY: dict[str, str | None] = {
    "ru": "RU",
    "be": "BY",
    "uk": "UA",
    "kk": "KZ",
    "ky": "KG",
    "en": None,
    "de": "DE",
    "fr": "FR",
    "pl": "PL",
    "es": "ES",
    "it": "IT",
    # pt обрабатывается в infer_country_from_language (pt-BR vs pt-PT)
    "tr": "TR",
    "ar": "SA",
    "zh": "CN",
    "ja": "JP",
    "ko": "KR",
}


def infer_country_from_language(language_code: str | None) -> str | None:
    if not language_code:
        return None
    norm = language_code.lower().replace("_", "-")
    primary = norm.split("-")[0]

    if primary == "zh":
        parts = norm.split("-")
        tail = parts[-1] if len(parts) > 1 else ""
        if tail in ("tw", "hk", "mo", "sg"):
            return tail.upper()
        if "hant" in parts:
            return "TW"
        return "CN"

    if primary == "pt":
        parts = norm.split("-")
        if len(parts) >= 2 and parts[1] == "pt":
            return "PT"
        return "BR"

    if primary in _LANG_PRIMARY_TO_COUNTRY:
        return _LANG_PRIMARY_TO_COUNTRY[primary]
    # ru-RU style
    parts = norm.split("-")
    if len(parts) == 2 and len(parts[1]) == 2:
        return parts[1].upper()
    return None


def apply_telegram_metadata(
    db_user: User,
    *,
    language_code: str | None,
    username: str | None,
    first_name: str | None,
) -> None:
    db_user.locale = pick_locale(language_code)
    inferred = infer_country_from_language(language_code)
    if inferred:
        db_user.country_code = inferred
    if username is not None:
        db_user.tg_username = username[:255] if username else None
    if first_name is not None:
        db_user.display_first_name = first_name[:255] if first_name else None


async def refresh_avatar_if_needed(
    bot: Bot,
    db_user: User,
    *,
    force: bool = False,
) -> None:
    if db_user.avatar_small_file_id and not force:
        return
    try:
        prof = await bot.get_user_profile_photos(db_user.telegram_id, limit=1)
        if prof.photos:
            sizes = prof.photos[0]
            smallest = sizes[-1]
            db_user.avatar_small_file_id = smallest.file_id[:255]
    except Exception as exc:
        logger.debug("avatar skip tg=%s: %s", db_user.telegram_id, exc)
