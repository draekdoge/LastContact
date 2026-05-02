# Деплой на Zeabur (GitHub)

Один репозиторий, несколько **сервисов** в одном проекте Zeabur: общий Docker-образ из `Dockerfile`, разные **Start Command** и порты.

**Свой домен (без ngrok):** в Zeabur привяжи DNS (A/CNAME по их инструкции) к сервисам **api** и **bot**. Для продакшена достаточно двух имён, например:

| Назначение | Пример переменной | Пример значения |
|------------|-------------------|-----------------|
| Mini App + JSON API | `MINI_APP_PUBLIC_URL` | `https://app.твой-домен.ru` (тот же хост, что у сервиса **api** по HTTPS) |
| Вебхук Telegram | `WEBHOOK_BASE_URL` | `https://bot.твой-домен.ru` (публичный URL сервиса **bot**, без слэша в конце) |

В @BotFather для **домена Web Apps** укажи **только hostname** от `MINI_APP_PUBLIC_URL` (как требует Telegram). Сертификат HTTPS обычно выдаёт Zeabur; ngrok не нужен.

## Инфраструктура в проекте

1. **PostgreSQL** — из маркетплейса Zeabur. Подставь в переменные сервисов строки подключения (в Zeabur часто дают `POSTGRES_HOST`, порт, пользователя, пароль, БД или одну composite-переменную).
2. **Redis** — аналогично.
3. **RabbitMQ** — шаблон RabbitMQ в Zeabur или внешний брокер (CloudAMQP). Нужны `CELERY_BROKER_URL` и `CELERY_RESULT_BACKEND` (Redis можно оставить для результата, как в `.env.example`).

Собери **async** и **sync** URL для Postgres (как в `.env.example`):

- `DATABASE_URL` — `postgresql+asyncpg://…`
- `DATABASE_URL_SYNC` — `postgresql://…` (для Alembic в скриптах старта)

## Сервисы приложения (4 штуки)

Все из репозитория `contact`, корень репозитория, сборка по `Dockerfile`.

| Сервис | Start Command | Порт (пример) | Назначение |
|--------|----------------|---------------|------------|
| **api** | `/app/scripts/start-api.sh` | `8000` (или `PORT` от Zeabur) | Mini App `GET /`, `/api/mini/*`, health |
| **bot** | `/app/scripts/start-bot.sh` | `8080` | Long polling или webhook Telegram |
| **worker** | `celery -A worker.celery_app worker --loglevel=info --pool=solo` | — | Таймеры, lab sweep |
| **beat** | `celery -A worker.celery_app beat --loglevel=info` | — | Расписание Celery |

Скрипты `start-api.sh` / `start-bot.sh` выполняют `alembic upgrade head` перед uvicorn (идемпотентно).

## Переменные окружения (минимум)

Скопируй из `.env.example` и заполни в Zeabur (общие для всех сервисов или через shared variables):

- `BOT_TOKEN`
- `DATABASE_URL`, `DATABASE_URL_SYNC`
- `REDIS_URL`
- `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`
- `MINI_APP_PUBLIC_URL` — твой **собственный** HTTPS-origin сервиса **api** (без пути в конце), совпадает с доменом в BotFather → Web Apps.
- Прод: `TELEGRAM_DELIVERY=webhook`, `WEBHOOK_BASE_URL` = твой HTTPS-домен сервиса **bot** (отдельное имя или поддомен — как настроишь в DNS), `WEBHOOK_PATH`, при необходимости `WEBHOOK_SECRET`.

Zeabur проксирует внешний 443 на внутренний `PORT` контейнера — в `WEBHOOK_BASE_URL` / `MINI_APP_PUBLIC_URL` указывай **публичные** `https://…` без `:порт`.

## GitHub

Подключи репозиторий в Zeabur → Deploy → выбери ветку `main`, включи автодеплой при push.

## Проверка

- `GET /health` на API — `service: api`
- `GET /health` на боте — `service: bot`
- После деплоя: в @BotFather домен Web App = хост из `MINI_APP_PUBLIC_URL`
