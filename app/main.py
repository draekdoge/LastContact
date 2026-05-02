"""HTTP API (Mini App, health) без процесса Telegram-бота."""

from fastapi import FastAPI, Request

from app.config import get_settings
from app.mini_app.router import router as mini_router

settings = get_settings()

app = FastAPI(title="Вирус — API")
app.include_router(mini_router)


@app.middleware("http")
async def mini_api_private_cache(request: Request, call_next):
    """Не кэшировать ответы /api/mini (персональные данные)."""
    response = await call_next(request)
    if request.url.path.startswith("/api/mini"):
        response.headers["Cache-Control"] = "private, no-store"
    return response


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "api"}
