# Дэшборд админа (shadcn) с логином/паролем на сабдомене — дизайн

## Цель

Сделать приватный админ‑дэшборд для просмотра общей статистики по игре. Доступ — **по логину и паролю (не Telegram)**. Дэшборд открывается на сабдомене **`admlastcts`** через **Caddy**.

## Контекст проекта

- Backend: Python 3.12+, FastAPI.
- База: PostgreSQL 16 (SQLAlchemy async).
- Прод: `docker-compose.prod.yml`, API проброшен на `127.0.0.1:8000` (удобно для reverse proxy через Caddy).
- Mini App уже использует cookie `mini_session` (Telegram‑сессия). Админка должна быть полностью отдельной.

## Нефункциональные требования

- **Безопасность**:
  - пароль не хранить в открытом виде: только bcrypt‑хэш
  - админ‑сессия в `httpOnly` cookie
  - защита от перебора: rate limit по IP на `POST /admin/login`
  - ответы админки не кэшировать: `Cache-Control: no-store`
- **Изоляция**:
  - cookie админки не пересекается с Mini App (`admin_session` vs `mini_session`)
  - path cookie ограничен `/admin`
- **Минимальная инфраструктура**:
  - без отдельного сервиса на старте (встроить в существующий FastAPI), Caddy проксирует сабдомен на локальный порт API.

## Архитектура (рекомендованный вариант)

### Backend (FastAPI)

Добавляем админ‑роутер, который:

- отдаёт SPA‑статику дэшборда (React/Vite build)
- предоставляет API метрик (JSON) под `/api/admin/*`
- проверяет админ‑сессию для всех `/admin/*` и `/api/admin/*`, кроме страницы логина

Роуты:

- `GET /admin/login` — html‑страница/SPA‑роут входа
- `POST /admin/login` — логин по username/password → выставляет cookie `admin_session`
- `POST /admin/logout` — удаляет cookie `admin_session`
- `GET /api/admin/overview` — агрегированные KPI
- (по мере необходимости) `GET /api/admin/top` и т.п.

### Frontend (shadcn/ui)

Отдельный фронтенд‑пакет в репозитории, сборка Vite → статические файлы:

- `admin-ui/`:
  - React + TypeScript
  - TailwindCSS
  - shadcn/ui компоненты
  - сборка в `admin-ui/dist/`

FastAPI будет монтировать:

- `/admin/assets/*` → `admin-ui/dist/assets/*`
- `/admin/*` → `admin-ui/dist/index.html` (SPA fallback)

### Конфигурация (env)

Добавляем настройки:

- `ADMIN_USERNAME`
- `ADMIN_PASSWORD_HASH` — bcrypt hash
- `ADMIN_SESSION_SECRET` — секрет для подписи cookie
- `ADMIN_SESSION_TTL_SECONDS` (по умолчанию 7 дней)
- `ADMIN_RATE_LIMIT_PER_MINUTE` (по умолчанию 10)

## Аутентификация и сессии

### Формат cookie

- cookie: `admin_session`
- `httpOnly=true`, `secure=true`, `samesite=lax`, `path=/admin`
- значение: подписанный токен (HMAC‑SHA256) с payload:
  - `sub` (username)
  - `exp` (unix seconds)

### Проверка пароля

- сравнение `ADMIN_USERNAME` и `bcrypt.verify(password, ADMIN_PASSWORD_HASH)`

### Rate limit

MVP‑вариант: Redis‑счётчик по ключу `rl:admin_login:<ip>:<minute_bucket>`.

## Метрики MVP (общая статистика)

`GET /api/admin/overview` возвращает:

- `total_users`
- `new_last_24h`
- `new_today_utc`
- `state_counts`: infected / immune / zombie

Опционально (если быстро/надёжно извлекается из текущей схемы):

- `top_referrers`: топ по прямым заражениям (и/или по поддереву, если есть готовые поля)
- `fountain`: базовые счётчики участия
- `lab`: базовые счётчики запусков/клеймов

## Caddy (reverse proxy)

На сервере:

- сабдомен `admlastcts.<domain>` проксируется на `127.0.0.1:8000`
- рекомендуется добавить security headers на уровне Caddy (опционально)

## Ошибки и UX

- не раскрывать причины отказа логина (единое сообщение “Неверный логин или пароль”)
- 429 при rate limit (понятный текст)
- авто‑редирект на `/admin/login`, если сессия истекла

## Тестирование

Backend:

- unit‑тесты для:
  - подписи/проверки `admin_session`
  - логин success/fail
  - защита `GET /api/admin/overview` без сессии

Frontend:

- smoke: сборка Vite проходит, страница логина рендерится, запросы к API работают при наличии cookie.

