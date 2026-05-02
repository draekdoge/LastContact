"""Отдельное приложение Telegram-бота (webhook или long polling)."""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager, suppress

from aiogram.types import MenuButtonWebApp, Update, WebAppInfo
from fastapi import FastAPI, Header, HTTPException, Request, Response

from app.bot.factory import create_bot, create_dispatcher
from app.bot.keyboards import mini_app_webapp_url
from app.config import get_settings
from app.mini_app.router import router as mini_router

logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not settings.bot_token:
        raise RuntimeError("BOT_TOKEN обязателен для сервиса бота (app.bot_main)")

    bot = create_bot()
    dp = create_dispatcher()
    app.state.bot = bot
    app.state.dp = dp

    if settings.telegram_delivery == "polling":
        try:
            await bot.delete_webhook(drop_pending_updates=False)
        except Exception as exc:
            logger.warning("Не удалось удалить webhook при старте polling: %s", exc)
    elif settings.telegram_delivery == "webhook":
        if settings.webhook_base_url:
            url = f"{settings.webhook_base_url.rstrip('/')}{settings.webhook_path}"
            secret = settings.webhook_secret or None
            try:
                await bot.set_webhook(url=url, secret_token=secret)
                logger.info("Webhook установлен: %s", url)
            except Exception as exc:
                logger.warning("Не удалось установить webhook %s: %s", url, exc)
        else:
            logger.warning(
                "TELEGRAM_DELIVERY=webhook, но WEBHOOK_BASE_URL пуст — "
                "вызовите setWebhook вручную на URL с путём %s",
                settings.webhook_path,
            )

    # Единый URL с reply-кнопкой «Терминал»: иначе в @BotFather часто остаётся старый WebApp — initData пустой.
    mini_url = mini_app_webapp_url(startapp="timer")
    if mini_url:
        try:
            await bot.set_chat_menu_button(
                menu_button=MenuButtonWebApp(
                    text="🔬 Терминал",
                    web_app=WebAppInfo(url=mini_url),
                ),
            )
            logger.info("Меню чата: WebApp «Терминал» → %s", mini_url)
        except Exception as exc:
            logger.warning("set_chat_menu_button (WebApp) не применился: %s", exc)

    poll_task: asyncio.Task[None] | None = None
    if settings.telegram_delivery == "polling":
        poll_task = asyncio.create_task(
            dp.start_polling(bot, handle_signals=False),
            name="telegram-polling",
        )
    try:
        yield
    finally:
        if poll_task is not None:
            await dp.stop_polling()
            with suppress(asyncio.CancelledError):
                await poll_task
        await bot.session.close()


app = FastAPI(title="Вирус — бот", lifespan=lifespan)
app.include_router(mini_router)


@app.middleware("http")
async def mini_api_private_cache(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/api/mini"):
        response.headers["Cache-Control"] = "private, no-store"
    return response


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "bot", "telegram": settings.telegram_delivery}


if settings.telegram_delivery == "webhook":

    @app.post(settings.webhook_path)
    async def telegram_webhook(
        request: Request,
        x_telegram_bot_api_secret_token: str | None = Header(default=None),
    ) -> Response:
        if settings.webhook_secret and x_telegram_bot_api_secret_token != settings.webhook_secret:
            raise HTTPException(status_code=401, detail="invalid secret")

        bot = request.app.state.bot
        dp = request.app.state.dp
        body = await request.json()
        update = Update.model_validate(body)
        await dp.feed_update(bot, update)
        return Response(status_code=200)
