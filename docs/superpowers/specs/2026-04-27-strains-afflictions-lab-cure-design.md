# Дизайн: Штаммы (organic roots) + дебаффы штамма + лечение через Лабу + уведомления

Дата: 2026-04-27  
Статус: Draft → (ожидает подтверждения)  
Связанные документы: `openspec/decisions/002-timer-lab-fountain-nodes-bot-miniapp.md`, `openspec/proposals/lab-fountain-zombie-v1.md`

## 0) Цель

Добавить долгую мету и кооперацию внутри ветки заражения:

- **Каждый organic игрок** (пришёл без реф-ссылки) запускает **свой штамм**.
- Штамм получает **рандомные дебаффы**, которые реально ухудшают выживание (вариант B), но не убивают “без шанса”.
- Дебафф **лечится через Лабу**: результаты Лабы дают **прогресс исследования лекарства**.
- Бот рассылает **уведомления**: дебафф появился/вылечен и “что делать дальше” (CTA: открыть Лабу).

## 1) Определения

- **Штамм (strain)**: метка компоненты леса заражений. У каждого пользователя ровно один `strain_id`.
- **Корень штамма**: игрок, у которого `infected_by_user_id is NULL` (organic). Он же `root_user_id` в штамме.
- **Дебафф штамма (affliction)**: негативный эффект, действующий на всех участников штамма в течение окна, пока не вылечен.
- **Лечение**: накопление `cure_progress` до `cure_required` (за счёт `lab_claim`).

## 2) Модель графа

Вместо одного дерева — **лес**:

- Organic: новый узел-источник (корень) создаёт новый `strain_id`.
- Referral: наследует `strain_id` от заражающего.

В Mini App “Моё дерево” по умолчанию показывает **дерево своего штамма** (иначе глобальный лес слишком большой).

## 3) Ограничения MVP

- В каждый момент у штамма максимум **1 активный дебафф**.
- Дебафф лечится **только** через “результат Лабы” (claim).
- Никакой LLM-генерации текста в рантайме: описания — из пула шаблонов.

## 4) Частота появления дебаффов

Цель: “ощущается”, но не спамит.

- **Проверка** раз в `AFFLICTION_CHECK_MINUTES` (по умолчанию 60 минут).
- **Кулдаун** после окончания/лечения: `AFFLICTION_COOLDOWN_HOURS` (по умолчанию 36 часов).
- Вероятность появления на проверку — функция размера штамма (с капом).

Рекомендованные параметры (env):

- `AFFLICTION_CHECK_MINUTES=60`
- `AFFLICTION_COOLDOWN_HOURS=36`
- `AFFLICTION_BASE_CHANCE=0.03` (3%/ч)
- `AFFLICTION_CHANCE_CAP=0.08` (8%/ч)
- `AFFLICTION_MIN_STRAIN_SIZE=4` (штаммы 1–3 игроков защищены от дебаффов)

Формула (MVP):

- `size = active_strain_members`
- `chance = min(cap, base + 0.01 * log2(size))`
- если `size < min_size` → 0

## 5) Дебаффы: типы и эффект (вариант B, но с капами)

Дебаффы должны быть жёсткими “по ощущению”, но без мгновенного убийства:

- Эффекты **не уменьшают** `timer_ends_at` напрямую каждую секунду.
- Вместо этого они **ухудшают спасательные механики** (Лаба/Фонтан), чтобы игрок ощущал давление, но мог контрить.

MVP-эффекты (примерный набор, 3–5 типов):

- `necrosis_bloom`: бонус Лабы к таймеру уменьшается на `severity × 15%` (кап 45%).
- `signal_spoof`: вклад реагентов в Фонтан (pour weight) уменьшается на `severity × 20%` (кап 60%).
- `enzyme_leak`: лимит “реагентов в фонтан в сутки” уменьшается на `severity × 2` (нижний предел 4).
- `latency_fog`: время анализа в Лабе увеличивается на `severity × 10 минут` (кап +30 мин).

**Почему так**: игрок не “умирает от дебаффа”, но ощущает просадку прогресса — и понимает, что лечение важно.

## 6) Лечение дебаффа через Лабу

При `lab_claim`:

- игрок получает личную награду (как сейчас),
- дополнительно, если у штамма есть активный дебафф — увеличиваем `cure_progress` на `research_points`.

`research_points` (MVP):

- базово 1
- +1 если пользователь `infected` (а не zombie) и цикл начат сегодня (опционально)
- кап на вклад игрока: `AFFLICTION_RESEARCH_DAILY_CAP=2`

Когда `cure_progress >= cure_required`:

- помечаем debuff как `cured_at=now`, `status=cured`
- эффект перестаёт применяться
- бот шлёт уведомление “лекарство готово” всем участникам штамма (или активным за 7 дней).

## 7) Уведомления ботом

События:

- `affliction_spawned`: “Появился дебафф штамма” + описание + CTA: открыть Лабу.
- `affliction_cured`: “Лекарство разработано” + короткое описание “что теперь”.

Тексты:

- Для каждого `type` есть 8–12 шаблонов RU (и по возможности EN позже), выбираем случайно.
- Шаблон содержит:
  - код штамма (например `X-77`)
  - severity (словом: I/II/III)
  - подсказка “Лаба → собрать образец → ждать → забрать результат”

## 8) API / Mini App: данные

`GET /api/mini/state` дополняется:

- `strain`: `{ code, size, root_label }`
- `affliction`: `{ type, severity, ends_at, cure_progress, cure_required, effect_hint } | null`

`/api/mini/lab/*` — без изменений протокола, только побочный эффект “исследование” при claim.

## 9) Схема БД (предложение)

### 9.1 Таблица `strains`

- `id UUID PK`
- `code VARCHAR(16) UNIQUE NOT NULL` (например `X-77`)
- `root_user_id UUID UNIQUE NOT NULL REFERENCES users(id)`
- `created_at TIMESTAMPTZ NOT NULL DEFAULT now()`

### 9.2 Поле `users.strain_id`

- `strain_id UUID NOT NULL REFERENCES strains(id)`
- Индекс по `strain_id`.

### 9.3 Таблица `strain_afflictions`

- `id UUID PK`
- `strain_id UUID NOT NULL REFERENCES strains(id)`
- `type VARCHAR(32) NOT NULL`
- `severity SMALLINT NOT NULL`
- `started_at TIMESTAMPTZ NOT NULL`
- `ends_at TIMESTAMPTZ NOT NULL`
- `cure_progress INTEGER NOT NULL DEFAULT 0`
- `cure_required INTEGER NOT NULL`
- `cured_at TIMESTAMPTZ NULL`

Ограничение (логическое, не обязательно SQL-constraint в MVP): не больше 1 активной записи на штамм (где `cured_at IS NULL AND ends_at > now()`).

## 10) План внедрения (в коде)

1. Миграции БД: `strains`, `users.strain_id`, `strain_afflictions`.
2. Присвоение `strain_id` при регистрации:
   - organic: create strain + assign
   - referral: inherit
3. Сервис “afflictions”:
   - выбор штаммов, cooldown, шанс
   - create affliction
4. Celery beat task: `strain_afflictions_tick` (раз в час).
5. Лаба: в `claim` добавляем research progress и проверяем cured.
6. Бот: отправка уведомлений участникам штамма (batch).
7. Mini App: отдаём `strain` и `affliction` в state + UI блок.

## 11) Open questions (не в MVP)

- Персональные дебаффы (не штаммовые).
- Влияние дебаффов на “зомби-выход” и/или иммунитет.
- Синергии с “узлами” из ADR 002 (региональные дебаффы vs штаммовые).

