### RULE 1

Перед любыми действиями с git в этом репозитории: проверь текущую ветку (git branch --show-current). Если это main или master — не коммить и не пушить изменения в неё; сообщи пользователю и предложи создать/переключиться на ветку вида feat/<кратко-о-задаче> или ui/<…> / logic/<…> (как договорено в команде), отпочковавшись от актуального origin/main.

При подготовке к пушу: явно указать удалённую ветку, соответствующую локальной фичеветке, например git push -u origin <имя-фичеветки>. Запрещено: git push origin main, force-push в main и любые команды, явно отправляющие коммиты в main.

Если пользователь просит «запушить», «мержить», «выкатывать» без уточнения ветки — не предполагаешь main: уточняешь или используешь уже созданную фичеветку; финальный merge в main описываешь как шаг пользователя через PR/GitHub.

Если в контексте видно несколько авторов («мы с коллегой» и т.п.) — напоминать этого правила при любой операции записи в git.

### RULE 2
## OpenSpec Initialization Protocol
1.  Check for OpenSpec: При запуске в новом проекте первым делом проверь наличие директории openspec/.
2.  Auto-Init: Если директория openspec/ отсутствует, ТЫ ДОЛЖЕН:
    - Предложить пользователю инициализировать OpenSpec.
    - Выполнить команду npx openspec init (или аналогичную для твоего окружения).
    - Если внешняя утилита недоступна, создай структуру вручную:
        - openspec/project.md (с описанием стека, архитектуры и правил именования).
        - openspec/proposals/ (папка для новых фич).
        - openspec/decisions/ (для принятых архитектурных решений/ADR).
3.  Context Loading: После инициализации считай содержимое openspec/project.md в контекст, прежде чем предлагать любые изменения в коде.

### RULE 3
- Перед существенными изменениями читай AGENTS.md (корень репо) и релевантные **openspec/specs/*/spec.md**.
- Новая фича / крупный рефакторинг: /opsx:propose → /opsx:apply → /opsx:archive (подробности в openspec/README.md).
- После правок в openspec/specs/: npm run openspec:validate.
- No auto-apply: После /opsx:propose всегда жди моей команды "Approved" или "Погнали".
- Human Commits: Пиши осмысленные commit messages на русском (Conventional Commits). Используй прошедшее время (например, "добавил", "исправил"). Объясняй "зачем", а не только "что".
- Clear Specs: В spec.md всегда выделяй секцию "Риски и побочные эффекты" для крупных правок.
- Tone: Общайся лаконично, как коллега-разработчик. Минимум вежливости, максимум контекста.

## Cursor Cloud specific instructions

### Сервисы и порты

| Сервис | Порт | Команда запуска |
|--------|------|-----------------|
| API (Mini App + REST) | 8000 | `uvicorn app.main:app --reload --port 8000` |
| Bot (Telegram) | 8080 | `uvicorn app.bot_main:app --reload --port 8080` |
| Worker (Celery) | — | `celery -A worker.celery_app worker --loglevel=info --pool=solo` |
| Beat (Celery scheduler) | — | `celery -A worker.celery_app beat --loglevel=info` |

Инфраструктура (PostgreSQL 16, Redis 7, RabbitMQ 3): `docker compose up -d postgres redis rabbitmq`.

### Env-переменные для локального запуска (без Docker)

```
DATABASE_URL=postgresql+asyncpg://virus:virus@localhost:5432/virus
DATABASE_URL_SYNC=postgresql://virus:virus@localhost:5432/virus
REDIS_URL=redis://localhost:16379/0
CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//
CELERY_RESULT_BACKEND=redis://localhost:16379/1
PYTHONPATH=/workspace
```

Также нужен `.env` с `BOT_TOKEN` (читается через `pydantic-settings`).

### Gotchas

- **Redis на 16379**: Docker Compose пробрасывает Redis на порт 16379 (не 6379), чтобы не конфликтовать с локальным Redis.
- **BOT_TOKEN обязателен** для `bot` сервиса. API стартует без него.
- **Миграции первыми**: `alembic upgrade head` до старта любых сервисов. Нужен `DATABASE_URL_SYNC` (синхронный драйвер `postgresql://`).
- **Celery `--pool=solo`**: задачи используют `asyncio.run()` + async SQLAlchemy — prefork pool вызывает `TCPTransport closed`.
- **Нет тестов**: в проекте нет `pytest` / `tests/`. Базовая проверка синтаксиса: `python -m py_compile <файл>`.
- **Нет линтера**: нет `ruff`/`flake8`/`mypy` в `requirements.txt`.
