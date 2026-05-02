# Admin Dashboard (shadcn) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Добавить приватный админ‑дэшборд на shadcn/ui с отдельной аутентификацией (логин/пароль), доступный на сабдомене `admlastcts` через Caddy, чтобы смотреть общую статистику по игре.

**Architecture:** React/Vite SPA (Tailwind + shadcn/ui) собирается в статику и отдаётся существующим FastAPI. Backend добавляет `/admin/*` (SPA) + `/api/admin/*` (метрики) и cookie‑сессию `admin_session` (HMAC подпись, bcrypt пароль, rate limit на логин через Redis).

**Tech Stack:** FastAPI, SQLAlchemy (async), PostgreSQL, Redis, React + Vite + Tailwind + shadcn/ui.

---

## Структура файлов (что создаём/меняем)

Backend:
- Create: `app/admin/router.py` — админ‑роуты (login/logout, SPA статика, API метрик)
- Create: `app/admin/auth.py` — подпись/проверка cookie‑сессии, bcrypt verify, зависимости FastAPI
- Modify: `app/main.py` — подключить админ‑роутер
- Modify: `app/config.py` — env настройки админки

Frontend:
- Create: `admin-ui/package.json`, `admin-ui/vite.config.ts`, `admin-ui/tsconfig.json`
- Create: `admin-ui/src/main.tsx`, `admin-ui/src/App.tsx`, `admin-ui/src/pages/Login.tsx`, `admin-ui/src/pages/Overview.tsx`
- Create: `admin-ui/src/components/...` (минимальные компоненты UI на shadcn)
- Create: `admin-ui/tailwind.config.ts`, `admin-ui/postcss.config.js`, `admin-ui/src/index.css`

Docs/ops:
- Modify: `.env_orig` (или добавить `.env.example` если есть) — описать env админки
- Provide snippet: Caddyfile для `admlastcts`

Tests:
- Create: `tests/test_admin_auth.py`
- Create: `tests/test_admin_routes.py`

---

### Task 1: Добавить настройки админки в конфиг

**Files:**
- Modify: `app/config.py`

- [ ] **Step 1: Добавить поля Settings**

Добавить в `Settings`:

```python
from pydantic import Field

admin_username: str = Field(default="admin", validation_alias="ADMIN_USERNAME")
admin_password_hash: str = Field(default="", validation_alias="ADMIN_PASSWORD_HASH")
admin_session_secret: str = Field(default="", validation_alias="ADMIN_SESSION_SECRET")
admin_session_ttl_seconds: int = Field(default=60 * 60 * 24 * 7, validation_alias="ADMIN_SESSION_TTL_SECONDS")
admin_rate_limit_per_minute: int = Field(default=10, validation_alias="ADMIN_RATE_LIMIT_PER_MINUTE")
```

- [ ] **Step 2: Проверить, что приложение стартует**

Run: `python -c "from app.config import get_settings; print(get_settings().admin_username)"`
Expected: prints `admin` (или значение из env).

---

### Task 2: Реализовать admin session + проверку пароля

**Files:**
- Create: `app/admin/auth.py`
- Test: `tests/test_admin_auth.py`

- [ ] **Step 1: Написать тесты подписи/верификации cookie**

```python
import time

from app.admin.auth import sign_admin_session, verify_admin_session

def test_admin_session_roundtrip():
    now = int(time.time())
    secret = "secret"
    token = sign_admin_session(username="admin", exp=now + 60, secret=secret)
    assert verify_admin_session(token, now=now, secret=secret) == "admin"

def test_admin_session_expired():
    now = int(time.time())
    secret = "secret"
    token = sign_admin_session(username="admin", exp=now - 1, secret=secret)
    assert verify_admin_session(token, now=now, secret=secret) is None
```

- [ ] **Step 2: Реализовать подпись и проверку**

```python
import base64
import hmac
import json
import hashlib
from dataclasses import dataclass

def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")

def _b64url_decode(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode((s + pad).encode("ascii"))

def sign_admin_session(*, username: str, exp: int, secret: str) -> str:
    payload = {"sub": username, "exp": exp}
    payload_b64 = _b64url_encode(json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))
    sig = hmac.new(secret.encode("utf-8"), payload_b64.encode("ascii"), hashlib.sha256).digest()
    return payload_b64 + "." + _b64url_encode(sig)

def verify_admin_session(cookie: str, *, now: int, secret: str) -> str | None:
    try:
        payload_b64, sig_b64 = cookie.split(".", 1)
        expected = hmac.new(secret.encode("utf-8"), payload_b64.encode("ascii"), hashlib.sha256).digest()
        if not hmac.compare_digest(_b64url_encode(expected), sig_b64):
            return None
        payload = json.loads(_b64url_decode(payload_b64))
        if int(payload.get("exp", 0)) < now:
            return None
        sub = payload.get("sub")
        return sub if isinstance(sub, str) and sub else None
    except Exception:
        return None
```

- [ ] **Step 3: Подключить bcrypt verify**

Добавить зависимость `bcrypt` в `requirements.txt`, и функцию:

```python
import bcrypt

def verify_password(*, password: str, password_hash: str) -> bool:
    if not password_hash:
        return False
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
```

- [ ] **Step 4: Прогнать тесты**

Run: `pytest -q`
Expected: PASS.

---

### Task 3: Admin router (login/logout, защита, метрики overview)

**Files:**
- Create: `app/admin/router.py`
- Modify: `app/main.py`
- Test: `tests/test_admin_routes.py`

- [ ] **Step 1: Тест: /api/admin/overview без cookie**

```python
from fastapi.testclient import TestClient
from app.main import app

def test_admin_overview_requires_auth():
    c = TestClient(app)
    r = c.get("/api/admin/overview")
    assert r.status_code in (401, 403)
```

- [ ] **Step 2: Реализовать router**

Ключевые элементы:
- `POST /admin/login` принимает `username`, `password`
- проверяет rate limit по IP (Redis)
- если ok → ставит cookie `admin_session` (path `/admin`, httpOnly, secure, samesite=lax)
- `GET /api/admin/overview` — агрегирует метрики из БД (users counts)

- [ ] **Step 3: Подключить router в app**

В `app/main.py`:

```python
from app.admin.router import router as admin_router
app.include_router(admin_router)
```

- [ ] **Step 4: Прогнать тесты**

Run: `pytest -q`
Expected: PASS.

---

### Task 4: Подключить shadcn/ui фронтенд (Vite) и сборку

**Files:**
- Create: `admin-ui/*` (см. выше)

- [ ] **Step 1: Инициализировать Vite React TS**

Run (в корне репо):
- `npm create vite@latest admin-ui -- --template react-ts`
- `cd admin-ui && npm i`

- [ ] **Step 2: Tailwind**

Run:
- `cd admin-ui && npm i -D tailwindcss postcss autoprefixer`
- `cd admin-ui && npx tailwindcss init -p`

Добавить `src/index.css` с tailwind директивами.

- [ ] **Step 3: shadcn/ui**

Run:
- `cd admin-ui && npx shadcn@latest init`
- добавить компоненты: `button`, `card`, `input`, `label`, `table`, `toast` (минимум)

- [ ] **Step 4: Реализовать страницы Login/Overview**

Поведение:
- Login отправляет `POST /admin/login`, затем редиректит на `/admin`
- Overview грузит `GET /api/admin/overview` и показывает карточки KPI

- [ ] **Step 5: Сборка**

Run:
- `cd admin-ui && npm run build`
Expected: `admin-ui/dist/index.html` и `admin-ui/dist/assets/*`.

---

### Task 5: Раздача статики admin-ui из FastAPI

**Files:**
- Modify: `app/admin/router.py`

- [ ] **Step 1: Смонтировать StaticFiles**

В router:
- mount `/admin/assets` на `admin-ui/dist/assets`
- fallback: для `/admin` и `/admin/*` отдавать `admin-ui/dist/index.html`

- [ ] **Step 2: Smoke**

Run:
- `uvicorn app.main:app --reload`
Open:
- `http://localhost:8000/admin/login` (должна открыться страница)

---

### Task 6: Caddyfile snippet

**Files:**
- Docs only (в спецификации/README)

- [ ] **Step 1: Дать конфиг**

Пример:

```caddyfile
admlastcts.example.com {
  reverse_proxy 127.0.0.1:8000
  header {
    Cache-Control "no-store"
    X-Content-Type-Options "nosniff"
    X-Frame-Options "DENY"
    Referrer-Policy "no-referrer"
  }
}
```

---

## Self-Review (plan vs spec)

- Спека требует: отдельный логин/пароль, cookie admin_session, rate limit, shadcn UI, сабдомен через Caddy — все покрыто задачами 1–6.
- Placeholder scan: в плане нет TBD/TODO; команды/пути/код для ключевых частей указаны.

