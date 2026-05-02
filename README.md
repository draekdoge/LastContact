# Вирус (Telegram)

MVP: `/start`, реферал `?start=r<telegram_id>`, запрет повторного заражения по чужой ссылке, счётчики цепочки, Docker Compose.

Спецификация: `virus_game_v2.pdf`, OpenSpec: `openspec/project.md`.

## Быстрый старт

1. Скопируй `.env.example` в `.env`, укажи `BOT_TOKEN`. По умолчанию **`TELEGRAM_DELIVERY=polling`** — HTTPS не обязателен; в этом режиме бот сам опрашивает Telegram.

2. Запуск инфраструктуры, **API** и **бота** (разные процессы):

```bash
docker compose up --build api bot postgres redis rabbitmq
```

- **API** (`app.main`): `http://localhost:8000` — `GET /health`.
- **Бот** (`app.bot_main`): `http://localhost:8080` — `GET /health`; в режиме webhook — `POST {WEBHOOK_PATH}` (по умолчанию `/webhook`).

Миграции выполняет одноразовый сервис **`migrate`** перед `api` / `bot` / `worker` / `beat`. Если видишь `relation "users" does not exist`, подними стек с `migrate` (см. `docker-compose.yml`) или вручную: `docker compose run --rm migrate`.

3. **Вебхук (прод)** — выставь `TELEGRAM_DELIVERY=webhook` и **`WEBHOOK_BASE_URL`** (HTTPS без слэша в конце). При старте сервис **`bot`** вызывает `setWebhook` на `{WEBHOOK_BASE_URL}{WEBHOOK_PATH}`. За reverse proxy направь POST вебхука на контейнер **bot:8080**, а не на API.

Альтернатива без перезапуска бота: `python scripts/set_webhook.py` (те же переменные окружения).

Для **продакшена** используй свой домен и HTTPS (Zeabur, VPS и т.д.) — см. [docs/ZEABUR.md](docs/ZEABUR.md). Ngrok имеет смысл только для **локальной** отладки вебхука без домена (прокси на порт **8080**).

4. Воркеры (опционально, нужен тот же `BOT_TOKEN` в `.env` — рассылка предупреждений и зомби):

```bash
docker compose up --build worker beat
```

В Docker воркер запускается с **`--pool=solo`**: задачи с `asyncio.run()` и async SQLAlchemy не совместимы с дефолтным **prefork** (наследуется мёртвый пул соединений → `TCPTransport closed`).

Раз в минуту: истечение таймера → зомби, режим «спящего» (нет рефералов 4+ ч), **отдельные** напоминания за 2 ч / 1 ч / 30 / 10 мин.

**Mini App** (живой таймер): страница `GET /` на сервисе API (`:8000`), данные `GET /api/mini/state` с заголовком `Authorization: tma <initData>`. В `.env` задай **`MINI_APP_PUBLIC_URL`** (HTTPS origin без `/mini`, тот же хост что у API), в @BotFather укажи домен для Web Apps. Старые пути `GET /mini` и `/mini/` тоже отдают ту же страницу. В чате появится вторая кнопка «Таймер». Команда **`/status`** — снимок в сообщении.

## Локальная разработка без Docker

Если поднят только Redis из Compose, на хосте он слушает **16379** (не 6379), чтобы не пересекаться с локальным Redis.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql+asyncpg://virus:virus@localhost:5432/virus
export DATABASE_URL_SYNC=postgresql://virus:virus@localhost:5432/virus
export REDIS_URL=redis://localhost:16379/0
alembic upgrade head
uvicorn app.main:app --reload --port 8000   # API
uvicorn app.bot_main:app --reload --port 8080   # бот (в другом терминале)
```

## Полезное

- Здоровье API: `GET http://localhost:8000/health` — `{"status":"ok","service":"api"}`.
- Здоровье бота: `GET http://localhost:8080/health` — `service: bot`, поле `telegram`: `polling` или `webhook`.
- Вебхук: только у процесса бота при `TELEGRAM_DELIVERY=webhook` — `POST {WEBHOOK_PATH}` (тело JSON Update).
- У бота в @BotFather должен быть **username**, иначе реферальные ссылки не собрать.
- В проде Mini App открывается с твоего домена на сервис **API** (`MINI_APP_PUBLIC_URL`). Локально для теста без домена — отдельный туннель на порт **8000**, не путать с вебхуком бота на **8080**.

## Деплой на Zeabur

Краткая инструкция: [docs/ZEABUR.md](docs/ZEABUR.md) (GitHub → несколько сервисов, Postgres, Redis, RabbitMQ, `start-api.sh` / `start-bot.sh`).
