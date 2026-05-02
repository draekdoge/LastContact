"""Маршруты Mini App и JSON для фронта.

Безопасность:
  - Публично: GET /, /mini, /mini/ — только статический index.html (без секретов).
  - Все /api/mini/* — обязательный заголовок Authorization: tma <initData> и проверка
    подписи Telegram (require_mini_app_user_id).
"""

from __future__ import annotations

import json
import html
import logging
import re
import random
import uuid
from datetime import UTC, datetime, timedelta
import base64
import hashlib
import hmac
from pathlib import Path
from typing import Annotated, Any

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, Response
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from pydantic import BaseModel
from sqlalchemy import func, select, text

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LinkPreviewOptions,
    SwitchInlineQueryChosenChat,
)

from app.config import get_settings
from app.db.models import FountainContribution, GlobalEvent, InviteBoost, Strain, StrainAffliction, User
from app.db.session import async_session_maker
from app.i18n import get_msg
from app.mini_app.region_scopes import country_codes_for_top_scope, normalize_top_scope
from app.mini_app.telegram_validate import WebAppAuthError, parse_and_validate_init_data, telegram_user_id_from_validated
from app.services.lab_service import LabError, claim_lab_result, get_lab_state, start_lab_cycle
from app.services.affliction_service import active_affliction_effect, get_active_affliction
from app.services.economy_service import (
    BOOST_KIND_STRAIN_BOOST,
    EconomyError,
    build_economy_state,
    boost_payload,
    create_invite_boost,
    purchase_upgrade,
    upgrade_level,
)
from app.services.reagent_service import contribution_weight, pour_units_remaining, reset_fountain_pour_daily_if_needed
from app.services.user_service import (
    apply_immunity_recovery,
    build_telegram_start_url,
    ensure_referral_token,
)
from app.services.clicker_energy import (
    clicker_max_energy as _clicker_max_energy,
    clicker_next_energy_at as _clicker_next_energy_at,
    clicker_regen_energy as _clicker_regen_energy,
    clicker_regen_seconds as _clicker_regen_seconds,
)
from app.services.clicker_network_regen import (
    MAX_TOTAL_REGEN_BPS,
    effective_regen_bonus_bps,
    invite_temp_regen_bonus_bps,
    network_regen_bonus_bps,
)
from app.services.mini_app_presence import sync_mini_app_engagement_and_presence

router = APIRouter(tags=["mini-app"])
_log = logging.getLogger(__name__)

_STATIC_DIR = Path(__file__).resolve().parent / "static"
_GAME_STATIC_ROOT = (_STATIC_DIR / "game").resolve()

_WORLD_CACHE_KEY = "world:stats:v1"
_WORLD_CACHE_TTL_SECONDS = 30
_TREE_NODE_LIMIT = 501
_REFERRAL_PAYLOAD_RE = r"^[A-Za-z0-9_-]{1,64}$"


def _build_boost_owner_dm_html(m, *, boost: InviteBoost, landing_url: str) -> str:
    """Карточка в ЛС владельцу после покупки boost: сводка по бусту + ссылка."""
    mult = float(boost.bonus_multiplier or 1.0)
    bonus_pct = max(0, round((mult - 1.0) * 100))
    expires_line = boost.expires_at.strftime("%d.%m.%Y %H:%M UTC")
    uses = int(boost.max_uses or 0)
    return (
        f"{m.boost_card_header}\n\n"
        f"{m.boost_card_bonus.format(bonus_pct=bonus_pct)}\n"
        f"{m.boost_card_uses.format(uses=uses)}\n"
        f"{m.boost_card_expires.format(expires=expires_line)}\n\n"
        f"{m.boost_card_url_hint}\n"
        f"<code>{html.escape(landing_url, quote=False)}</code>"
    )


def _build_boost_card_markup(m) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=(m.boost_btn_owner_share or m.boost_btn_spread or "Share")[:200],
                    switch_inline_query_chosen_chat=SwitchInlineQueryChosenChat(
                        query="boost",
                        allow_user_chats=True,
                        allow_group_chats=True,
                        allow_channel_chats=True,
                    ),
                )
            ],
        ]
    )


_CLICKER_MAX_TAPS_PER_REQUEST = 30
_CLICKER_MAX_ACCEPTED_TAPS_PER_SECOND = 30
_CLICKER_DROP_P_DNA = 0.05
_CLICKER_DROP_P_RNA = 0.02
_CLICKER_DROP_P_CAT = 0.005


def _clicker_drop_probs(user: User) -> tuple[float, float, float]:
    """Вероятности выпадения реагента за один тап; растут с прокачкой штамма в экономике."""
    mut = upgrade_level(user, "mutation_chance")
    amp = upgrade_level(user, "viral_amplifier")
    p_dna = _CLICKER_DROP_P_DNA + 0.002 * mut + 0.001 * amp
    p_rna = _CLICKER_DROP_P_RNA + 0.001 * mut + 0.0005 * amp
    p_cat = _CLICKER_DROP_P_CAT + 0.00025 * mut + 0.00012 * amp
    return (
        min(0.22, max(0.0, p_dna)),
        min(0.10, max(0.0, p_rna)),
        min(0.025, max(0.0, p_cat)),
    )


def _redis_client() -> aioredis.Redis:
    return aioredis.from_url(get_settings().redis_url, decode_responses=True)


def _clicker_reset_daily_if_needed(user: User, today) -> None:
    if user.clicker_daily_reset_date != today:
        user.clicker_daily_reset_date = today
        user.clicker_daily_rolls = 0


def _clicker_rewards_for_accepted_taps(user: User, n: int) -> dict[str, int]:
    """За каждый принятый тап — независимые шансы выпадения реагентов (зависят от прокачки)."""
    p_dna, p_rna, p_cat = _clicker_drop_probs(user)
    out = {"dna": 0, "rna": 0, "cat": 0}
    for _ in range(max(0, n)):
        if random.random() < p_dna:
            out["dna"] += 1
        if random.random() < p_rna:
            out["rna"] += 1
        if random.random() < p_cat:
            out["cat"] += 1
    return out


def _clicker_state_payload(user: User, now: datetime) -> dict[str, Any]:
    nxt = _clicker_next_energy_at(user, now)
    pd, pr, pc = _clicker_drop_probs(user)
    return {
        "energy": int(user.clicker_energy or 0),
        "max_energy": _clicker_max_energy(user),
        "next_energy_at": nxt.isoformat() if nxt else None,
        "max_taps_per_request": _CLICKER_MAX_TAPS_PER_REQUEST,
        "max_accepted_taps_per_second": _CLICKER_MAX_ACCEPTED_TAPS_PER_SECOND,
        "regen_seconds": _clicker_regen_seconds(user, now=now),
        "regen_bonus_bps_cap": int(MAX_TOTAL_REGEN_BPS),
        "regen_bonus_bps": effective_regen_bonus_bps(user, now),
        "network_regen_bonus_bps": network_regen_bonus_bps(user),
        "invite_temp_regen_bonus_bps": invite_temp_regen_bonus_bps(user, now),
        "invite_regen_boost_ends_at": (
            user.invite_regen_boost_ends_at.isoformat() if user.invite_regen_boost_ends_at else None
        ),
        "mini_regen_online_direct": int(user.mini_regen_online_direct or 0),
        "mini_regen_online_subtree": int(user.mini_regen_online_subtree or 0),
        "reagents": {
            "dna": int(user.reagent_dna or 0),
            "rna": int(user.reagent_rna or 0),
            "cat": int(user.reagent_cat or 0),
        },
        "proc_chance": {
            "dna": round(pd * 100, 2),
            "rna": round(pr * 100, 2),
            "cat": round(pc * 100, 2),
        },
    }


class MiniStateOut(BaseModel):
    telegram_id: int
    state: str
    locale: str
    timer_ends_at: datetime | None
    timer_left_seconds: int | None
    timer_span_seconds: int | None = None
    immune_ends_at: datetime | None = None
    immune_left_seconds: int | None = None
    immune_span_seconds: int | None = None
    can_activate_immunity: bool = False
    direct_infections: int
    subtree_infections: int
    country_code: str | None
    timer_extend_sources_html: str | None = None
    """HTML с бэка (локаль пользователя); только для активной фазы infected с таймером."""
    strain_code: str | None = None
    strain_title: str | None = None
    affliction_type: str | None = None
    affliction_severity: int | None = None
    affliction_ends_at: datetime | None = None
    affliction_progress: int | None = None
    affliction_required: int | None = None
    is_strain_root: bool = False
    infected_by_other: bool = False
    invite_share_url: str | None = None
    """Та же deep-link ссылка, что и у «Передать штамм»: https://t.me/<bot>?start=<referral_token>."""


class MiniWorldCountry(BaseModel):
    code: str
    infected: int
    zombie: int
    immune: int
    active: int


class MiniWorldOut(BaseModel):
    total_users: int
    infected: int
    zombie: int
    immune: int
    new_last_24h: int
    new_utc_today: int
    my_subtree_infections: int | None = None
    my_direct_infections: int | None = None
    my_world_rank: int | None = None
    countries: list[MiniWorldCountry] = []


class MiniTreeNode(BaseModel):
    id: str
    parent_id: str | None
    telegram_id: int
    label: str
    state: str
    depth: int
    direct_infections: int = 0
    subtree_infections: int = 0
    reagents: dict[str, int] | None = None
    upgrades: dict[str, int] | None = None
    clicker: dict[str, int] | None = None
    active_invite_boosts: int = 0


class MiniTreeOut(BaseModel):
    nodes: list[MiniTreeNode]
    truncated: bool


class MiniTopRow(BaseModel):
    rank: int
    telegram_id: int
    label: str
    subtree_infections: int
    direct_infections: int
    state: str


class MiniTopOut(BaseModel):
    rows: list[MiniTopRow]
    total: int
    page: int
    page_size: int
    scope: str


class FountainPourIn(BaseModel):
    dna: int = 0
    rna: int = 0
    cat: int = 0


class ClickerTapIn(BaseModel):
    taps: int = 1


class EconomyUpgradeIn(BaseModel):
    upgrade: str


class EconomyInviteBoostIn(BaseModel):
    kind: str = BOOST_KIND_STRAIN_BOOST


def require_mini_app_user_id(
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> int:
    """Подпись Telegram WebApp initData. Обязательна для всех маршрутов /api/mini/*."""
    settings = get_settings()
    if not settings.bot_token:
        raise HTTPException(status_code=503, detail="BOT_TOKEN not configured")
    if not authorization or not authorization.startswith("tma "):
        raise HTTPException(status_code=401, detail="need Authorization: tma <initData>")
    raw = authorization[4:].strip()
    try:
        data = parse_and_validate_init_data(raw, settings.bot_token)
        return telegram_user_id_from_validated(data)
    except WebAppAuthError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


def _mini_index_file() -> FileResponse:
    index = _STATIC_DIR / "index.html"
    if not index.is_file():
        raise HTTPException(status_code=404, detail="mini app static missing")
    # Telegram WebView и прокси часто кэшируют HTML миниаппа — без этого пользователь
    # видит старый index.html после деплоя.
    return FileResponse(
        index,
        media_type="text/html; charset=utf-8",
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
        },
    )


@router.get("/")
@router.get("/mini")
@router.get("/mini/")
async def mini_index() -> FileResponse:
    """Mini App: основной вход — корень `/`; `/mini` оставлен для старых ссылок (фрагмент #tgWebAppData…)."""
    return _mini_index_file()


def _game_safe_file(relative: str) -> Path:
    """Публичные ассеты Mini App: `static/game/<path>`. Без path traversal."""
    if not relative or relative.startswith(("/", "\\")):
        raise HTTPException(status_code=404, detail="not found")
    rel = Path(relative)
    if rel.is_absolute():
        raise HTTPException(status_code=404, detail="not found")
    parts = rel.parts
    if ".." in parts or any(p.startswith("..") for p in parts):
        raise HTTPException(status_code=404, detail="not found")
    resolved = (_GAME_STATIC_ROOT.joinpath(*parts)).resolve()
    try:
        resolved.relative_to(_GAME_STATIC_ROOT)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="not found") from exc
    if not resolved.is_file():
        raise HTTPException(status_code=404, detail="not found")
    return resolved


@router.get("/game/{filepath:path}")
async def mini_game_public_asset(filepath: str) -> FileResponse:
    """Манифест, bootstrap, Lottie, img — без авторизации (для WebView)."""
    path = _game_safe_file(filepath)
    return FileResponse(path)


@router.get("/r/{start_payload}")
async def referral_landing(start_payload: str, request: Request, bot: str | None = Query(default=None)) -> HTMLResponse:
    """Публичный referral landing для OG preview; пользователь уходит в Telegram deep link."""
    if not re.match(_REFERRAL_PAYLOAD_RE, start_payload):
        raise HTTPException(status_code=404, detail="referral not found")

    settings = get_settings()
    base = settings.mini_app_public_url.strip().rstrip("/")
    if not base:
        base = str(request.base_url).rstrip("/")

    bot_username = (bot or "").strip().lstrip("@")
    telegram_url = f"https://t.me/{bot_username}?start={start_payload}" if bot_username else "https://t.me/"
    page_url = f"{base}/r/{start_payload}"
    if bot_username:
        page_url = f"{page_url}?bot={bot_username}"
    image_url = f"{base}/assets/referral-card.jpg"

    title = "LastContact · Цепочка заражений"
    description = "Тебе передали штамм. Открой карточку и проверь, куда тебя втянет сеть."
    safe_title = html.escape(title, quote=True)
    safe_description = html.escape(description, quote=True)
    safe_page_url = html.escape(page_url, quote=True)
    safe_image_url = html.escape(image_url, quote=True)
    safe_telegram_url = html.escape(telegram_url, quote=True)

    content = f"""<!doctype html>
<html lang="ru">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <title>{safe_title}</title>
    <meta property="og:type" content="website" />
    <meta property="og:title" content="{safe_title}" />
    <meta property="og:description" content="{safe_description}" />
    <meta property="og:image" content="{safe_image_url}" />
    <meta property="og:url" content="{safe_page_url}" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{safe_title}" />
    <meta name="twitter:description" content="{safe_description}" />
    <meta name="twitter:image" content="{safe_image_url}" />
    <meta http-equiv="refresh" content="1;url={safe_telegram_url}" />
  </head>
  <body>
    <p>Открываем Telegram…</p>
    <p><a href="{safe_telegram_url}">Перейти в цепочку заражений</a></p>
  </body>
</html>"""
    return HTMLResponse(content, status_code=200)


@router.get("/assets/referral-card.jpg")
async def referral_card_asset() -> FileResponse:
    """Публичная картинка для inline referral-карточки (thumbnail/photo_url)."""
    card = _STATIC_DIR / "referral-card.jpg"
    if not card.is_file():
        raise HTTPException(status_code=404, detail="referral card missing")
    return FileResponse(card, media_type="image/jpeg")


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _b64url_decode(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)


def _mini_session_sign(*, uid: int, exp: int, secret: str) -> str:
    payload = f"{uid}.{exp}".encode("utf-8")
    sig = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).digest()
    return f"{_b64url(payload)}.{_b64url(sig)}"


def _mini_session_verify(cookie: str, *, now: int, secret: str) -> int | None:
    try:
        payload_b64, sig_b64 = cookie.split(".", 1)
        payload = _b64url_decode(payload_b64)
        sig = _b64url_decode(sig_b64)
        exp_sig = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).digest()
        if not hmac.compare_digest(sig, exp_sig):
            return None
        uid_s, exp_s = payload.decode("utf-8").split(".", 1)
        uid = int(uid_s)
        exp = int(exp_s)
        if exp < now:
            return None
        return uid
    except Exception:
        return None


@router.get("/login")
async def mini_login_page(request: Request) -> Response:
    """
    Вход для Mini App: из обычного браузера покажет инструкцию.
    Внутри Telegram WebView — попробует взять initData и обменять на cookie mini_session.
    """
    # Если уже есть сессия — сразу в Mini App.
    settings = get_settings()
    now = int(datetime.now(UTC).timestamp())
    cookie = request.cookies.get("mini_session")
    if cookie and _mini_session_verify(cookie, now=now, secret=settings.bot_token):
        return RedirectResponse(url="/", status_code=302)

    html = """<!doctype html>
<html lang="ru">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <title>LastContact · Вход</title>
    <style>
      body{font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Ubuntu;max-width:720px;margin:48px auto;padding:0 18px;line-height:1.45}
      .card{border:1px solid rgba(255,255,255,.12);border-radius:14px;padding:18px;background:rgba(255,255,255,.04)}
      code{background:rgba(0,0,0,.06);padding:2px 6px;border-radius:6px}
      .muted{opacity:.75}
      .btn{display:inline-block;margin-top:10px;padding:10px 14px;border-radius:12px;border:1px solid rgba(255,255,255,.16);text-decoration:none}
    </style>
  </head>
  <body>
    <div class="card">
      <h2>Это вход в игру</h2>
      <p class="muted">Игра открывается <b>только внутри Telegram</b> — чтобы мы точно знали, кто вы.</p>
      <p>Зайдите в чат с ботом и нажмите кнопку <b>«Терминал»</b>.</p>
      <a class="btn" href="https://t.me/">Открыть Telegram</a>
      <p id="status" class="muted">Секунду…</p>
    </div>
    <script>
      (async function(){
        const status = document.getElementById('status');
        const tg = window.Telegram && window.Telegram.WebApp;
        function initDataFromUrl() {
          try {
            const h = (window.location.hash || '').replace(/^#/, '');
            const m = h.match(/(?:^|&)tgWebAppData=([^&]+)/);
            if (m && m[1]) {
              try { return decodeURIComponent(m[1].replace(/[+]/g, ' ')); }
              catch (e) { return m[1]; }
            }
            if (h.indexOf('user=') !== -1 && h.indexOf('hash=') !== -1) return h;
            const q = new URLSearchParams(window.location.search || '').get('tgWebAppData');
            return q || '';
          } catch (e) {
            return '';
          }
        }
        async function waitInitData() {
          for (let i = 0; i < 90; i++) {
            const d = (tg && (tg.initData || '').trim()) || initDataFromUrl();
            if (d) return d;
            await new Promise((resolve) => setTimeout(resolve, 130));
          }
          return (tg && (tg.initData || '').trim()) || initDataFromUrl();
        }
        const initData = await waitInitData();
        if (!initData) { status.textContent = 'Похоже, Telegram не передал подпись сессии. Закройте мини-приложение и откройте снова через кнопку «Терминал».'; return; }
        status.textContent = 'Входим…';
        try {
          const r = await fetch('/api/mini/login', { method:'POST', headers: { Authorization: 'tma ' + initData }});
          if (!r.ok) { status.textContent = 'Не получилось войти. Закройте мини‑приложение и откройте снова через «Терминал». (Код: ' + r.status + ')'; return; }
          location.replace('/');
        } catch (e) {
          status.textContent = 'Кажется, сеть шалит. Попробуйте ещё раз чуть позже.';
        }
      })();
    </script>
  </body>
</html>"""
    return HTMLResponse(html, status_code=200)


@router.post("/api/mini/login")
async def mini_login(
    tid: Annotated[int, Depends(require_mini_app_user_id)],
) -> Response:
    """Обмен initData (TMA) на httpOnly cookie для доступа к статику Mini App."""
    settings = get_settings()
    now_dt = datetime.now(UTC)
    async with async_session_maker() as session:
        u = await session.scalar(select(User).where(User.telegram_id == tid))
        if u is not None:
            await sync_mini_app_engagement_and_presence(session, u, now_dt)
            await session.commit()
    now = int(now_dt.timestamp())
    exp = now + 86400
    token = _mini_session_sign(uid=tid, exp=exp, secret=settings.bot_token)
    resp = Response(status_code=204)
    resp.set_cookie(
        "mini_session",
        token,
        max_age=86400,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/",
    )
    return resp


@router.get("/api/mini/state", response_model=MiniStateOut)
async def mini_state(
    tid: Annotated[int, Depends(require_mini_app_user_id)],
) -> MiniStateOut:
    settings = get_settings()
    async with async_session_maker() as session:
        user = await session.scalar(select(User).where(User.telegram_id == tid))
        if user is None:
            raise HTTPException(status_code=404, detail="user not registered; use /start in bot")

        now = datetime.now(UTC)
        await sync_mini_app_engagement_and_presence(session, user, now)
        left: int | None = None
        span: int | None = None
        extend_html: str | None = None
        if user.timer_ends_at and user.state == "infected":
            left = max(0, int((user.timer_ends_at - now).total_seconds()))
            span = max(60, int((user.timer_ends_at - user.created_at).total_seconds()))
            loc_msg = get_msg(user.locale)
            extend_html = loc_msg.timer_extend_sources.format(
                bonus_hours=float(settings.bonus_hours_per_referral)
            )

        imm_left: int | None = None
        imm_span: int | None = None
        if user.state == "immune" and user.immune_ends_at and now < user.immune_ends_at:
            imm_left = max(0, int((user.immune_ends_at - now).total_seconds()))
            imm_span = max(60, int(settings.immune_duration_hours * 3600))

        # Счётчики с фактической цепочкой users.* (денормализованные поля могли отставать).
        direct_infections = int(
            await session.scalar(select(func.count()).where(User.infected_by_user_id == user.id)) or 0
        )
        subtree_res = await session.execute(
            text(
                """
                WITH RECURSIVE down AS (
                    SELECT id FROM users WHERE infected_by_user_id = :uid
                    UNION ALL
                    SELECT u.id FROM users u
                    INNER JOIN down d ON u.infected_by_user_id = d.id
                )
                SELECT count(*)::int FROM down
                """
            ),
            {"uid": user.id},
        )
        subtree_infections = int(subtree_res.scalar_one())

        strain = await session.get(Strain, user.strain_id)
        aff = await get_active_affliction(session, strain_id=user.strain_id, now=now)

        invite_share_url: str | None = None
        if settings.bot_token:
            bot_username = ""
            bot = Bot(token=settings.bot_token)
            try:
                try:
                    me = await bot.get_me()
                    bot_username = (me.username or "").strip()
                except Exception:
                    _log.warning("mini_state: get_me failed for invite_share_url", exc_info=True)
            finally:
                await bot.session.close()
            if bot_username:
                await ensure_referral_token(session, user)
                ref_tok = user.referral_token
                invite_share_url = build_telegram_start_url(
                    bot_username=bot_username,
                    start_payload=ref_tok,
                )

        await session.commit()

        return MiniStateOut(
            telegram_id=user.telegram_id,
            state=user.state,
            locale=user.locale,
            timer_ends_at=user.timer_ends_at,
            timer_left_seconds=left,
            timer_span_seconds=span,
            immune_ends_at=user.immune_ends_at,
            immune_left_seconds=imm_left,
            immune_span_seconds=imm_span,
            can_activate_immunity=user.state == "zombie",
            direct_infections=direct_infections,
            subtree_infections=subtree_infections,
            country_code=user.country_code,
            timer_extend_sources_html=extend_html,
            strain_code=strain.code if strain else None,
            strain_title=strain.title if strain else None,
            affliction_type=aff.type if aff else None,
            affliction_severity=int(aff.severity) if aff else None,
            affliction_ends_at=aff.ends_at if aff else None,
            affliction_progress=int(aff.cure_progress) if aff else None,
            affliction_required=int(aff.cure_required) if aff else None,
            is_strain_root=bool(strain and strain.root_user_id == user.id),
            infected_by_other=bool(user.infected_by_user_id is not None),
            invite_share_url=invite_share_url,
        )


@router.get("/api/mini/world", response_model=MiniWorldOut)
async def mini_world(
    tid: Annotated[int, Depends(require_mini_app_user_id)],
) -> MiniWorldOut:
    cached: dict[str, Any] | None = None
    try:
        raw_cache = await _redis_client().get(_WORLD_CACHE_KEY)
        if raw_cache:
            cached = json.loads(raw_cache)
    except Exception:
        cached = None

    if cached is not None:
        total_users = int(cached.get("total") or 0)
        infected = int(cached.get("infected") or 0)
        zombie = int(cached.get("zombie") or 0)
        immune = int(cached.get("immune") or 0)
        new_last_24h = int(cached.get("new_24h") or 0)
        new_utc_today = int(cached.get("new_utc") or 0)
        countries_raw = cached.get("countries") or []
    else:
        now = datetime.now(UTC)
        since_24h = now - timedelta(hours=24)
        since_utc_day = datetime(now.year, now.month, now.day, tzinfo=UTC)

        async with async_session_maker() as session:
            total_users = int(await session.scalar(select(func.count()).select_from(User)) or 0)
            infected = int(
                await session.scalar(select(func.count()).select_from(User).where(User.state == "infected")) or 0
            )
            zombie = int(
                await session.scalar(select(func.count()).select_from(User).where(User.state == "zombie")) or 0
            )
            immune = int(
                await session.scalar(select(func.count()).select_from(User).where(User.state == "immune")) or 0
            )
            new_last_24h = int(
                await session.scalar(select(func.count()).select_from(User).where(User.created_at >= since_24h)) or 0
            )
            new_utc_today = int(
                await session.scalar(select(func.count()).select_from(User).where(User.created_at >= since_utc_day))
                or 0
            )

            country_rows = (
                await session.execute(
                    select(User.country_code, User.state, func.count())
                    .where(User.country_code.is_not(None))
                    .group_by(User.country_code, User.state)
                )
            ).all()

        agg: dict[str, dict[str, int]] = {}
        for code, state, cnt in country_rows:
            if not code:
                continue
            key = code.strip().upper()
            if not key:
                continue
            slot = agg.setdefault(key, {"infected": 0, "zombie": 0, "immune": 0})
            if state in slot:
                slot[state] += int(cnt or 0)
        countries_raw = []
        for code, slot in agg.items():
            inf = int(slot.get("infected") or 0)
            zom = int(slot.get("zombie") or 0)
            imm = int(slot.get("immune") or 0)
            active = inf + zom
            if active <= 0 and imm <= 0:
                continue
            countries_raw.append(
                {"code": code, "infected": inf, "zombie": zom, "immune": imm, "active": active}
            )
        countries_raw.sort(key=lambda r: (-r["active"], -r["immune"], r["code"]))

        try:
            await _redis_client().set(
                _WORLD_CACHE_KEY,
                json.dumps(
                    {
                        "total": total_users,
                        "infected": infected,
                        "zombie": zombie,
                        "immune": immune,
                        "new_24h": new_last_24h,
                        "new_utc": new_utc_today,
                        "countries": countries_raw,
                    },
                    ensure_ascii=False,
                ),
                ex=_WORLD_CACHE_TTL_SECONDS,
            )
        except Exception:
            pass

    my_sub: int | None = None
    my_dir: int | None = None
    my_rank: int | None = None
    async with async_session_maker() as session:
        user = await session.scalar(select(User).where(User.telegram_id == tid))
        if user is not None:
            my_sub = int(user.subtree_infections_count)
            my_dir = int(user.direct_infections_count)
            above = await session.scalar(
                select(func.count()).select_from(User).where(
                    User.is_npc.is_(False),
                    User.subtree_infections_count > user.subtree_infections_count,
                )
            )
            my_rank = int(above or 0) + 1

    countries_out = [
        MiniWorldCountry(
            code=str(row.get("code") or "").upper(),
            infected=int(row.get("infected") or 0),
            zombie=int(row.get("zombie") or 0),
            immune=int(row.get("immune") or 0),
            active=int(row.get("active") or 0),
        )
        for row in (countries_raw or [])
        if row.get("code")
    ]

    return MiniWorldOut(
        total_users=total_users,
        infected=infected,
        zombie=zombie,
        immune=immune,
        new_last_24h=new_last_24h,
        new_utc_today=new_utc_today,
        my_subtree_infections=my_sub,
        my_direct_infections=my_dir,
        my_world_rank=my_rank,
        countries=countries_out,
    )


def _tree_label(*, display_first_name: str | None, tg_username: str | None, telegram_id: int) -> str:
    if display_first_name and display_first_name.strip():
        return display_first_name.strip()[:48]
    if tg_username and tg_username.strip():
        return ("@" + tg_username.strip().lstrip("@"))[:48]
    return f"#{str(telegram_id)[-6:]}"


@router.get("/api/mini/tree", response_model=MiniTreeOut)
async def mini_tree(
    tid: Annotated[int, Depends(require_mini_app_user_id)],
    view: str = Query("down", description="down | full"),
) -> MiniTreeOut:
    async with async_session_maker() as session:
        user = await session.scalar(select(User).where(User.telegram_id == tid))
        if user is None:
            raise HTTPException(status_code=404, detail="user not registered")

        view_eff = (view or "down").strip().lower()
        if view_eff not in ("down", "full"):
            raise HTTPException(status_code=400, detail="invalid view")

        if view_eff == "down":
            rows = (
                await session.execute(
                    text(
                        """
                        WITH RECURSIVE sub AS (
                            SELECT id, infected_by_user_id, telegram_id, display_first_name, tg_username, state, 0 AS depth
                            FROM users WHERE id = :root_id
                            UNION ALL
                            SELECT u.id, u.infected_by_user_id, u.telegram_id, u.display_first_name, u.tg_username, u.state,
                                   s.depth + 1
                            FROM users u
                            INNER JOIN sub s ON u.infected_by_user_id = s.id
                        )
                        SELECT id::text AS id,
                               infected_by_user_id::text AS parent_id,
                               telegram_id,
                               display_first_name,
                               tg_username,
                               state,
                               depth
                        FROM sub
                        ORDER BY depth, telegram_id
                        LIMIT :lim
                        """
                    ),
                    {"root_id": user.id, "lim": _TREE_NODE_LIMIT},
                )
            ).mappings().all()
        else:
            # full = chain up to root + subtree down from current user.
            # We compute allowed node ids (ancestors U descendants), then lay them out from the top ancestor.
            rows = (
                await session.execute(
                    text(
                        """
                        WITH RECURSIVE
                        up AS (
                            SELECT id, infected_by_user_id, 0 AS lvl
                            FROM users
                            WHERE id = :me_id
                            UNION ALL
                            SELECT u.id, u.infected_by_user_id, c.lvl + 1
                            FROM users u
                            INNER JOIN up c ON c.infected_by_user_id = u.id
                        ),
                        down AS (
                            SELECT id
                            FROM users
                            WHERE id = :me_id
                            UNION ALL
                            SELECT u.id
                            FROM users u
                            INNER JOIN down d ON u.infected_by_user_id = d.id
                        ),
                        allowed AS (
                            SELECT id FROM up
                            UNION
                            SELECT id FROM down
                        ),
                        top AS (
                            SELECT id AS top_id
                            FROM up
                            ORDER BY lvl DESC
                            LIMIT 1
                        ),
                        tree AS (
                            SELECT
                                u.id,
                                u.infected_by_user_id,
                                u.telegram_id,
                                u.display_first_name,
                                u.tg_username,
                                u.state,
                                0 AS depth
                            FROM users u
                            WHERE u.id = (SELECT top_id FROM top)
                            UNION ALL
                            SELECT
                                u.id,
                                u.infected_by_user_id,
                                u.telegram_id,
                                u.display_first_name,
                                u.tg_username,
                                u.state,
                                t.depth + 1
                            FROM users u
                            INNER JOIN tree t ON u.infected_by_user_id = t.id
                            WHERE u.id IN (SELECT id FROM allowed)
                        )
                        SELECT id::text AS id,
                               infected_by_user_id::text AS parent_id,
                               telegram_id,
                               display_first_name,
                               tg_username,
                               state,
                               depth
                        FROM tree
                        ORDER BY depth, telegram_id
                        LIMIT :lim
                        """
                    ),
                    {"me_id": user.id, "lim": _TREE_NODE_LIMIT},
                )
            ).mappings().all()

    truncated = len(rows) >= _TREE_NODE_LIMIT
    row_user_ids = [uuid.UUID(str(r["id"])) for r in rows]
    users_by_id: dict[uuid.UUID, User] = {}
    active_boosts_by_user_id: dict[uuid.UUID, int] = {}
    if row_user_ids:
        user_rows = await session.scalars(select(User).where(User.id.in_(row_user_ids)))
        users_by_id = {u.id: u for u in user_rows}
        boost_rows = (
            await session.execute(
                select(InviteBoost.owner_user_id, func.count())
                .where(
                    InviteBoost.owner_user_id.in_(row_user_ids),
                    InviteBoost.uses < InviteBoost.max_uses,
                    InviteBoost.expires_at > datetime.now(UTC),
                )
                .group_by(InviteBoost.owner_user_id)
            )
        ).all()
        active_boosts_by_user_id = {uid: int(cnt) for uid, cnt in boost_rows}
    nodes: list[MiniTreeNode] = []
    for r in rows:
        pid = r.get("parent_id")
        node_user_id = uuid.UUID(str(r["id"]))
        node_user = users_by_id.get(node_user_id)
        nodes.append(
            MiniTreeNode(
                id=str(r["id"]),
                parent_id=str(pid) if pid else None,
                telegram_id=int(r["telegram_id"]),
                label=_tree_label(
                    display_first_name=r.get("display_first_name"),
                    tg_username=r.get("tg_username"),
                    telegram_id=int(r["telegram_id"]),
                ),
                state=str(r["state"]),
                depth=int(r["depth"]),
                direct_infections=int(node_user.direct_infections_count if node_user else 0),
                subtree_infections=int(node_user.subtree_infections_count if node_user else 0),
                reagents={
                    "dna": int(node_user.reagent_dna or 0) if node_user else 0,
                    "rna": int(node_user.reagent_rna or 0) if node_user else 0,
                    "cat": int(node_user.reagent_cat or 0) if node_user else 0,
                },
                upgrades={
                    "viral_amplifier": upgrade_level(node_user, "viral_amplifier") if node_user else 0,
                    "mutation_chance": upgrade_level(node_user, "mutation_chance") if node_user else 0,
                },
                clicker={
                    "energy": int(node_user.clicker_energy or 0) if node_user else 0,
                    "max_energy_bonus": int(node_user.clicker_max_energy_bonus or 0) if node_user else 0,
                    "regen_bonus_bps": int(effective_regen_bonus_bps(node_user)) if node_user else 0,
                },
                active_invite_boosts=active_boosts_by_user_id.get(node_user_id, 0),
            )
        )
    return MiniTreeOut(nodes=nodes, truncated=truncated)


@router.get("/api/mini/top", response_model=MiniTopOut)
async def mini_top(
    tid: Annotated[int, Depends(require_mini_app_user_id)],
    scope: str = Query("world", description="world | country | eu | cis | asia | americas | africa | middle_east | oceania"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=25),
) -> MiniTopOut:
    sc = normalize_top_scope(scope)

    async with async_session_maker() as session:
        me = await session.scalar(select(User).where(User.telegram_id == tid))
        if me is None:
            raise HTTPException(status_code=404, detail="user not registered")
        codes = country_codes_for_top_scope(sc, user_country=me.country_code)
        filters: list[Any] = [User.is_npc.is_(False)]
        if codes is not None:
            if len(codes) == 0:
                return MiniTopOut(rows=[], total=0, page=1, page_size=page_size, scope=sc)
            filters.append(User.country_code.in_(codes))

        total = int(await session.scalar(select(func.count()).select_from(User).where(*filters)) or 0)
        max_page = max(1, (total + page_size - 1) // page_size) if total else 1
        page_eff = min(max(1, page), max_page)
        offset = (page_eff - 1) * page_size
        res = await session.execute(
            select(User)
            .where(*filters)
            .order_by(User.subtree_infections_count.desc())
            .offset(offset)
            .limit(page_size)
        )
        users = res.scalars().all()

    rows: list[MiniTopRow] = []
    for i, u in enumerate(users, start=1):
        rows.append(
            MiniTopRow(
                rank=offset + i,
                telegram_id=int(u.telegram_id),
                label=_tree_label(
                    display_first_name=u.display_first_name,
                    tg_username=u.tg_username,
                    telegram_id=int(u.telegram_id),
                ),
                subtree_infections=int(u.subtree_infections_count),
                direct_infections=int(u.direct_infections_count),
                state=str(u.state),
            )
        )
    return MiniTopOut(rows=rows, total=total, page=page_eff, page_size=page_size, scope=sc)


_LINK_PREVIEW_OFF = LinkPreviewOptions(is_disabled=True)


async def _send_immunity_activated_notice(*, telegram_id: int, locale: str) -> None:
    settings = get_settings()
    if not settings.bot_token:
        return
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    try:
        msg = get_msg(locale)
        await bot.send_message(
            telegram_id,
            msg.immune_activated_notice,
            link_preview_options=_LINK_PREVIEW_OFF,
        )
    finally:
        await bot.session.close()


@router.get("/api/mini/lab/state")
async def mini_lab_state(
    tid: Annotated[int, Depends(require_mini_app_user_id)],
) -> dict[str, Any]:
    async with async_session_maker() as session:
        user = await session.scalar(select(User).where(User.telegram_id == tid))
        if user is None:
            raise HTTPException(status_code=404, detail="user not registered")
        return await get_lab_state(session, user)


@router.post("/api/mini/lab/start")
async def mini_lab_start(
    tid: Annotated[int, Depends(require_mini_app_user_id)],
) -> dict[str, Any]:
    async with async_session_maker() as session:
        user = await session.scalar(select(User).where(User.telegram_id == tid))
        if user is None:
            raise HTTPException(status_code=404, detail="user not registered")
        try:
            result = await start_lab_cycle(session, user)
        except LabError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        await session.commit()
        return result


@router.post("/api/mini/lab/claim")
async def mini_lab_claim(
    tid: Annotated[int, Depends(require_mini_app_user_id)],
) -> dict[str, Any]:
    async with async_session_maker() as session:
        user = await session.scalar(select(User).where(User.telegram_id == tid))
        if user is None:
            raise HTTPException(status_code=404, detail="user not registered")
        try:
            result = await claim_lab_result(session, user)
        except LabError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        await session.commit()
    return result


@router.get("/api/mini/fountain/state")
async def mini_fountain_state(
    tid: Annotated[int, Depends(require_mini_app_user_id)],
) -> dict[str, Any]:
    settings = get_settings()
    async with async_session_maker() as session:
        user = await session.scalar(select(User).where(User.telegram_id == tid))
        if user is None:
            raise HTTPException(status_code=404, detail="user not registered")

        reset_fountain_pour_daily_if_needed(user)
        reagents_block = {
            "dna": int(user.reagent_dna or 0),
            "rna": int(user.reagent_rna or 0),
            "cat": int(user.reagent_cat or 0),
        }
        sample_col = dict(user.lab_sample_collection or {})
        pour_info = {
            "daily_cap": settings.fountain_pour_daily_unit_cap,
            "used_today": int(user.fountain_pour_units_today or 0),
            "remaining_units": pour_units_remaining(user),
        }

        now = datetime.now(UTC)
        # Текущий или ближайший активный ивент
        active_event = await session.scalar(
            select(GlobalEvent)
            .where(
                GlobalEvent.type == "fountain",
                GlobalEvent.starts_at <= now,
                GlobalEvent.ends_at > now,
            )
            .order_by(GlobalEvent.starts_at.desc())
        )
        upcoming_event = None
        if active_event is None:
            upcoming_event = await session.scalar(
                select(GlobalEvent)
                .where(GlobalEvent.type == "fountain", GlobalEvent.starts_at > now)
                .order_by(GlobalEvent.starts_at.asc())
            )

        event_data: dict[str, Any] | None = None
        player_contribution: float = 0.0

        if active_event:
            total_weight = await session.scalar(
                select(func.coalesce(func.sum(FountainContribution.weight), 0))
                .where(FountainContribution.event_id == active_event.id)
            ) or 0.0

            player_weight = await session.scalar(
                select(func.coalesce(func.sum(FountainContribution.weight), 0))
                .where(
                    FountainContribution.event_id == active_event.id,
                    FountainContribution.user_id == user.id,
                )
            ) or 0.0
            player_contribution = float(player_weight)

            event_data = {
                "id": str(active_event.id),
                "status": "active",
                "starts_at": active_event.starts_at.isoformat(),
                "ends_at": active_event.ends_at.isoformat(),
                "seconds_left": max(0, int((active_event.ends_at - now).total_seconds())),
                "total_weight": float(total_weight),
                "player_contribution": player_contribution,
                "player_qualifies": player_contribution >= 2.0,
            }
        elif upcoming_event:
            event_data = {
                "id": str(upcoming_event.id),
                "status": "upcoming",
                "starts_at": upcoming_event.starts_at.isoformat(),
                "ends_at": upcoming_event.ends_at.isoformat(),
                "seconds_until": max(0, int((upcoming_event.starts_at - now).total_seconds())),
                "total_weight": 0.0,
                "player_contribution": 0.0,
                "player_qualifies": False,
            }

        return {
            "fountain_revival_ready": user.fountain_revival_ready,
            "event": event_data,
            "reagents": reagents_block,
            "sample_collection": sample_col,
            "fountain_pour": pour_info,
        }


@router.post("/api/mini/fountain/pour")
async def mini_fountain_pour(
    body: FountainPourIn,
    tid: Annotated[int, Depends(require_mini_app_user_id)],
) -> dict[str, Any]:
    settings = get_settings()
    if body.dna < 0 or body.rna < 0 or body.cat < 0:
        raise HTTPException(status_code=400, detail="invalid_amount")
    units = body.dna + body.rna + body.cat
    if units <= 0:
        raise HTTPException(status_code=400, detail="empty_pour")

    async with async_session_maker() as session:
        user = await session.scalar(select(User).where(User.telegram_id == tid))
        if user is None:
            raise HTTPException(status_code=404, detail="user not registered")

        now = datetime.now(UTC)
        active_event = await session.scalar(
            select(GlobalEvent)
            .where(
                GlobalEvent.type == "fountain",
                GlobalEvent.starts_at <= now,
                GlobalEvent.ends_at > now,
            )
            .order_by(GlobalEvent.starts_at.desc())
        )
        if active_event is None:
            raise HTTPException(status_code=400, detail="fountain_not_active")

        reset_fountain_pour_daily_if_needed(user)
        cap = settings.fountain_pour_daily_unit_cap
        aff = await get_active_affliction(session, strain_id=user.strain_id, now=now)
        eff = active_affliction_effect(aff)
        cap = max(4, int(cap) + int(eff.fountain_pour_cap_delta_units))
        used = int(user.fountain_pour_units_today or 0)
        left = cap - used
        if units > left:
            raise HTTPException(status_code=400, detail="pour_daily_cap")

        if body.dna > int(user.reagent_dna or 0) or body.rna > int(user.reagent_rna or 0) or body.cat > int(user.reagent_cat or 0):
            raise HTTPException(status_code=400, detail="insufficient_reagents")

        weight = contribution_weight(dna=body.dna, rna=body.rna, cat=body.cat)
        weight = round(weight * float(eff.fountain_weight_mult), 4)
        user.reagent_dna = int(user.reagent_dna or 0) - body.dna
        user.reagent_rna = int(user.reagent_rna or 0) - body.rna
        user.reagent_cat = int(user.reagent_cat or 0) - body.cat
        user.fountain_pour_units_today = used + units

        session.add(
            FountainContribution(
                id=uuid.uuid4(),
                user_id=user.id,
                event_id=active_event.id,
                weight=weight,
                action_type="reagent_pour",
            )
        )

        player_weight = await session.scalar(
            select(func.coalesce(func.sum(FountainContribution.weight), 0)).where(
                FountainContribution.event_id == active_event.id,
                FountainContribution.user_id == user.id,
            )
        )
        rd, rr, rc = int(user.reagent_dna), int(user.reagent_rna), int(user.reagent_cat)
        poured_total = int(user.fountain_pour_units_today)
        await session.commit()

    return {
        "ok": True,
        "weight_added": weight,
        "units_poured": units,
        "reagents": {"dna": rd, "rna": rr, "cat": rc},
        "fountain_pour": {
            "daily_cap": cap,
            "used_today": poured_total,
            "remaining_units": max(0, cap - poured_total),
        },
        "player_contribution": float(player_weight or 0.0),
    }


@router.post("/api/mini/immunity/activate")
async def mini_immunity_activate(
    tid: Annotated[int, Depends(require_mini_app_user_id)],
) -> dict[str, bool]:
    async with async_session_maker() as session:
        user = await session.scalar(select(User).where(User.telegram_id == tid))
        if user is None:
            raise HTTPException(status_code=404, detail="user not registered; use /start in bot")
        if not apply_immunity_recovery(user):
            raise HTTPException(
                status_code=400,
                detail="immunity can only be activated from zombie state",
            )
        loc = user.locale
        await session.commit()

    await _send_immunity_activated_notice(telegram_id=tid, locale=loc)
    return {"ok": True}


@router.get("/api/mini/clicker/state")
async def mini_clicker_state(
    tid: Annotated[int, Depends(require_mini_app_user_id)],
) -> dict[str, Any]:
    now = datetime.now(UTC)
    async with async_session_maker() as session:
        user = await session.scalar(select(User).where(User.telegram_id == tid))
        if user is None:
            raise HTTPException(status_code=404, detail="user not registered")
        await sync_mini_app_engagement_and_presence(session, user, now)
        _clicker_reset_daily_if_needed(user, now.date())
        _clicker_regen_energy(user, now)
        payload = _clicker_state_payload(user, now)
        await session.commit()
        return payload


@router.get("/api/mini/economy/state")
async def mini_economy_state(
    tid: Annotated[int, Depends(require_mini_app_user_id)],
) -> dict[str, Any]:
    now = datetime.now(UTC)
    async with async_session_maker() as session:
        user = await session.scalar(select(User).where(User.telegram_id == tid))
        if user is None:
            raise HTTPException(status_code=404, detail="user not registered")
        await sync_mini_app_engagement_and_presence(session, user, now)
        await session.commit()
        return build_economy_state(user, now)


@router.post("/api/mini/economy/upgrade")
async def mini_economy_upgrade(
    body: EconomyUpgradeIn,
    tid: Annotated[int, Depends(require_mini_app_user_id)],
) -> dict[str, Any]:
    async with async_session_maker() as session:
        user = await session.scalar(select(User).where(User.telegram_id == tid))
        if user is None:
            raise HTTPException(status_code=404, detail="user not registered")
        try:
            payload = await purchase_upgrade(session, user, body.upgrade)
        except EconomyError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        await session.commit()
        return payload


@router.post("/api/mini/economy/invite-boost")
async def mini_economy_invite_boost(
    body: EconomyInviteBoostIn,
    request: Request,
    tid: Annotated[int, Depends(require_mini_app_user_id)],
) -> dict[str, Any]:
    async with async_session_maker() as session:
        user = await session.scalar(select(User).where(User.telegram_id == tid))
        if user is None:
            raise HTTPException(status_code=404, detail="user not registered")
        try:
            boost = await create_invite_boost(session, user, kind=body.kind)
        except EconomyError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        settings = get_settings()
        bot_username = ""
        if settings.bot_token:
            bot = Bot(token=settings.bot_token)
            try:
                try:
                    me = await bot.get_me()
                    bot_username = me.username or ""
                except Exception:
                    _log.warning(
                        "invite-boost: get_me недоступен — deep link будет через web_fallback",
                        exc_info=True,
                    )
            finally:
                await bot.session.close()

        payload = boost_payload(boost)
        deep_link = build_telegram_start_url(bot_username=bot_username, start_payload=payload) if bot_username else ""
        base = settings.mini_app_public_url.strip().rstrip("/") or str(request.base_url).rstrip("/")
        web_fallback = f"{base}/r/{payload}"
        if bot_username:
            web_fallback = f"{web_fallback}?bot={bot_username}"
        # В чат и миниапп — только прямая ссылка в бота (без браузера /r/…)
        share_url = deep_link if deep_link else web_fallback
        uname = (bot_username or "").lstrip("@")
        state = build_economy_state(user)
        await session.commit()

        bot_card_sent = False
        if settings.bot_token and tid:
            try:
                loc = user.locale if user else "en"
                m = get_msg(loc)
                card_body = _build_boost_owner_dm_html(m, boost=boost, landing_url=share_url)
                markup = _build_boost_card_markup(m)
                lp_off = LinkPreviewOptions(is_disabled=True)
                bot_send = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
                try:
                    await bot_send.send_message(
                        tid,
                        card_body,
                        reply_markup=markup,
                        link_preview_options=lp_off,
                    )
                    bot_card_sent = True
                except Exception:
                    _log.exception("invite-boost: не удалось отправить карточку в чат с ботом")
                finally:
                    await bot_send.session.close()
            except Exception:
                _log.exception("invite-boost: подготовка или отправка карточки в ЛС")

        return {
            "ok": True,
            "payload": payload,
            "deep_link": deep_link,
            "landing_url": share_url,
            "inline_me_username": uname,
            "boost": {
                "kind": boost.kind,
                "expires_at": boost.expires_at.isoformat(),
                "bonus_multiplier": float(boost.bonus_multiplier),
                "max_uses": int(boost.max_uses),
            },
            "state": state,
            "bot_card_sent": bot_card_sent,
        }


@router.post("/api/mini/clicker/tap")
async def mini_clicker_tap(
    body: ClickerTapIn,
    tid: Annotated[int, Depends(require_mini_app_user_id)],
) -> dict[str, Any]:
    requested_taps = max(0, min(_CLICKER_MAX_TAPS_PER_REQUEST, int(body.taps or 0)))
    now = datetime.now(UTC)
    async with async_session_maker() as session:
        user = await session.scalar(select(User).where(User.telegram_id == tid))
        if user is None:
            raise HTTPException(status_code=404, detail="user not registered")

        await sync_mini_app_engagement_and_presence(session, user, now)
        _clicker_reset_daily_if_needed(user, now.date())
        _clicker_regen_energy(user, now)

        accepted_by_rate = 0
        try:
            r = _redis_client()
            key = f"clicker:{tid}:tap_window"
            accepted_by_rate = int(await r.incrby(key, requested_taps))
            if accepted_by_rate == requested_taps:
                await r.expire(key, 1)
            await r.aclose()
        except Exception:
            accepted_by_rate = requested_taps

        rate_left = max(0, _CLICKER_MAX_ACCEPTED_TAPS_PER_SECOND - max(0, accepted_by_rate - requested_taps))
        accepted_taps = min(
            requested_taps,
            max(0, int(user.clicker_energy or 0)),
            rate_left,
        )
        rejected_taps = max(0, int(body.taps or 0) - accepted_taps)

        rewards: dict[str, int] = {"dna": 0, "rna": 0, "cat": 0}
        if accepted_taps > 0:
            user.clicker_energy = max(0, int(user.clicker_energy or 0) - accepted_taps)
            if int(user.clicker_energy or 0) < _clicker_max_energy(user) and user.clicker_energy_updated_at is None:
                user.clicker_energy_updated_at = now

            rewards = _clicker_rewards_for_accepted_taps(user, accepted_taps)

            if rewards["dna"]:
                user.reagent_dna = int(user.reagent_dna or 0) + rewards["dna"]
            if rewards["rna"]:
                user.reagent_rna = int(user.reagent_rna or 0) + rewards["rna"]
            if rewards["cat"]:
                user.reagent_cat = int(user.reagent_cat or 0) + rewards["cat"]

        payload = _clicker_state_payload(user, now)
        payload.update(
            {
                "accepted_taps": accepted_taps,
                "rejected_taps": rejected_taps,
                "reward": rewards,
            }
        )
        await session.commit()
        return payload
