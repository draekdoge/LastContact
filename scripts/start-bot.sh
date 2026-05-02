#!/usr/bin/env sh
set -e
# Повторный upgrade head безопасен, если api уже поднял схему.
alembic upgrade head
exec uvicorn app.bot_main:app --host 0.0.0.0 --port "${PORT:-8080}"
