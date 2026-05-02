#!/usr/bin/env python3
"""Установка вебхука: WEBHOOK_BASE_URL + WEBHOOK_PATH, секрет из WEBHOOK_SECRET."""

import asyncio
import os
import sys

import httpx


async def main() -> None:
    token = os.environ.get("BOT_TOKEN", "")
    base = os.environ.get("WEBHOOK_BASE_URL", "").rstrip("/")
    path = os.environ.get("WEBHOOK_PATH", "/webhook")
    secret = os.environ.get("WEBHOOK_SECRET", "")

    if not token or not base:
        print("Нужны BOT_TOKEN и WEBHOOK_BASE_URL (https://... без слэша в конце)", file=sys.stderr)
        sys.exit(1)

    url = f"https://api.telegram.org/bot{token}/setWebhook"
    payload: dict = {"url": f"{base}{path}"}
    if secret:
        payload["secret_token"] = secret

    async with httpx.AsyncClient() as client:
        r = await client.post(url, json=payload, timeout=30.0)
        print(r.status_code, r.text)


if __name__ == "__main__":
    asyncio.run(main())
