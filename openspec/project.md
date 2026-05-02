# Вирус — Telegram-игра (OpenSpec)

## Назначение

Социальная PvP-симуляция «эпидемии» в Telegram: реферальное распространение, таймеры, сторона Virus/Immune, глобальные волны, Mini App. Продуктовая спецификация: [virus_game_v2.pdf](../virus_game_v2.pdf). Детальный план: `.cursor/plans/вирус_telegram-игра_9b340740.plan.md`.

**Ядро позиционирования:** социальный эксперимент, не MLM; нативные механики Telegram (deep link, inline, `shareToStory`, `shareMessage` / prepared inline).

## Стек

| Компонент | Технология |
|-----------|------------|
| API | Python 3.12+, FastAPI, Uvicorn |
| Бот | aiogram 3.x; по умолчанию **long polling**, вебхук опционально (`TELEGRAM_DELIVERY`) |
| Брокер | RabbitMQ |
| Воркеры | Celery |
| Кэш / таймеры (расширение) | Redis |
| БД | PostgreSQL 16 |
| Миграции | Alembic |
| Контейнеры | Docker Compose |

## Репозиторий

- `app/` — приложение: FastAPI, aiogram, домен, БД
  - Mini App клиент: `app/mini_app/static/index.html` + **игровой слой** `app/mini_app/static/game/` (`manifest.json`, `bootstrap.js`, `assets/*`) — раздаётся по `GET /game/...` без авторизации; ассеты и remote config — `game/README.md`. Визуальный стиль миниаппа: **тёмный терминал / неоновый ember** (мокап HUD, герой статуса с Lottie-слотом, SVG-карта «Мир»); Lottie — по путям в `manifest.json`.
- `worker/` — Celery
- `openspec/` — этот файл, `proposals/`, `decisions/`

## Решения (ADR)

- [001 — очереди, воркеры, таймеры](decisions/001-redis-rabbitmq-timers.md)
- [002 — таймер 48–72 ч, лаборатория / фонтан / узлы, бот vs Mini App](decisions/002-timer-lab-fountain-nodes-bot-miniapp.md)

## Предложения (proposals)

- [Лаборатория, Фонтан, Зомби-режим (v1)](proposals/lab-fountain-zombie-v1.md) — расширение ADR 002, глоссарий «спек → код», AC-блоки.
- [Кликер ↔ приглашения: единая экономика роста (v1)](proposals/invite-clicker-economy-loop-v1.md) — контур `кликер → усиление приглашений → рост сети → усиление кликера`.

## Соглашения

- **Реферал:** `?start=r{telegram_id}` — `telegram_id` пригласившего (цифры), лимит длины payload Telegram ≤ 64 символов.
- **Повторное заражение:** если пользователь уже в игре — отдельное сообщение, ребро не создаём, рефереру бонус не начисляем.
- **Органик:** `infected_by_user_id = NULL`, корень своей ветки.
- **Коммиты:** Conventional Commits, описание на русском.

## Окружения

- `dev` — локально, Docker Compose
- `staging` / `prod` — вне этого репозитория (деплой по необходимости)

## Целевая ветка Telegram

Минимум клиентских фич: ориентир **Bot API 8.0+** для `shareMessage` + prepared inline; **7.8+** для `shareToStory` в Mini App (фронт отдельно).
