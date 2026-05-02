# Proposal: Invite x Clicker Economy Loop (v1)

## Статус

Draft v1.0 · новая экономика поверх текущего Mini App clicker и реферального таймера. Не применять без отдельного `Approved` / `Погнали`.

## 0. Контекст

Сейчас кликер производит реагенты (`DNA/RNA/CAT`), а приглашения напрямую дают время через `bonus_hours_per_referral` в `register_new_infected`. Эти механики почти не замкнуты друг на друга: игрок может кликать отдельно и делиться отдельно.

Целевой контур:

```text
кликер производит ресурс -> ресурс усиливает приглашения -> приглашения усиливают производство
```

Роль подсистем:

- **Кликер**: производство ресурсов и ощущение ручной прокачки штамма.
- **Приглашения**: основной источник времени и роста сети.
- **Апгрейды**: мост между ресурсами кликера и силой приглашений.
- **Новые infected**: обратная связь, усиливающая энергию/реген/производство кликера.

## 1. Принципы

1. Кликер не выдаёт время напрямую.
2. Время остаётся редким ресурсом и приходит в основном из подтверждённых заражений.
3. Ресурсы кликера усиливают именно будущие invite-события.
4. Invite-события усиливают дальнейшее производство в кликере.
5. Визуальная обратная связь должна объяснять, откуда пришёл бонус: апгрейд, мутация, усиленный штамм, цепная глубина.

## 2. Валюты и ресурсы

### Уже есть

| Ресурс | Назначение v1 |
|---|---|
| `DNA` | базовая валюта апгрейдов и усиления ссылки |
| `RNA` | более дорогая валюта апгрейдов второго уровня |
| `CAT` | редкий реагент, не использовать в MVP invite loop |

### Можно добавить позже

| Ресурс | Назначение |
|---|---|
| `viral_mass` | мягкая валюта роста штамма, если DNA/RNA начнут конфликтовать с Фонтаном |

MVP не требует `viral_mass`: начинаем с DNA/RNA, потому что поля уже есть и кликер уже их производит.

## 3. Апгрейды приглашений

Хранение MVP: `users.mutation_tree` JSONB, ключ `economy_v1`.

```json
{
  "economy_v1": {
    "viral_amplifier": 2,
    "mutation_chance": 1,
    "chain_boost": 0,
    "clicker_regen": 1,
    "clicker_capacity": 3
  }
}
```

### 3.1 Вирусный усилитель

Усиливает базовое время за прямой invite.

Формула MVP:

```text
invite_bonus_seconds = base_bonus_seconds * (1 + 0.10 * viral_amplifier_level)
```

Ограничение:

- max level: 10
- максимум `+100%` к базовому invite time

### 3.2 Шанс мутации

Даёт шанс, что конкретное invite-событие умножит время.

Формула MVP:

```text
x2 chance = 3% + 2% * mutation_chance_level
x3 chance = 0.5% + 0.5% * floor(mutation_chance_level / 2)
```

Ограничение:

- roll выполняется только на подтверждённом новом игроке;
- x3 проверяется первым;
- max level: 10.

### 3.3 Chain Boost

Не должен превращать indirect сеть в бесконечный источник времени. MVP:

- direct inviter получает время;
- ancestors получают только производственный бонус к кликеру (`network_charge` / progress), без прямого времени;
- UI показывает, что сеть подпитывает штамм.

Позже можно добавить малый indirect time bonus с жёстким дневным cap.

## 4. Инвестиция перед шарингом

Паттерн: игрок перед отправкой может усилить конкретную ссылку.

### Boosted invite token

Добавить таблицу `invite_boosts`:

| Поле | Тип | Назначение |
|---|---|---|
| `id` | UUID | PK |
| `owner_user_id` | UUID | кто создал усиление |
| `token` | String(64), unique | payload для Telegram start |
| `dna_spent` | Integer | сколько DNA вложено |
| `rna_spent` | Integer | сколько RNA вложено |
| `bonus_multiplier` | Float | например `1.5` |
| `mutation_bonus_chance` | Float | дополнительный шанс x2/x3 |
| `max_uses` | Integer | MVP: `1` |
| `uses` | Integer | сколько раз сработало |
| `expires_at` | DateTime | TTL, например 24 часа |
| `created_at` | DateTime | аудит |

Payload:

```text
b_<token>
```

`resolve_inviter_from_start` расширяется:

- обычный `referral_token` работает как сейчас;
- `b_<token>` ищет активный `invite_boost`;
- возвращает inviter + boost context.

### MVP варианты усиления

| Действие | Цена | Эффект |
|---|---:|---|
| Усилить штамм | 100 DNA | `+50%` времени за следующего нового infected |
| Мутагенная капсула | 80 DNA + 10 RNA | `+10%` к x2 roll для следующего infected |

## 5. Приглашения усиливают кликер

Каждый новый infected должен давать видимый производственный прирост.

MVP direct invite rewards для inviter:

```text
+5 max_energy
+0.2% effective regen
+network_charge progress
```

Хранение:

- `clicker_max_energy_bonus` можно добавить отдельным Integer-полем;
- `clicker_regen_bonus_bps` можно добавить Integer bps-полем;
- либо MVP хранить в `mutation_tree.economy_v1`, но для частых расчётов лучше отдельные поля.

Рекомендуемая схема MVP:

| Поле | Тип | Default |
|---|---|---:|
| `clicker_max_energy_bonus` | Integer | `0` |
| `clicker_regen_bonus_bps` | Integer | `0` |
| `clicker_power_bps` | Integer | `0` |

Эффективные параметры:

```text
max_energy = 1200 + clicker_max_energy_bonus
regen_seconds = max(2, base_regen_seconds / (1 + clicker_regen_bonus_bps / 10000))
tap_value = 1 + clicker_power_bps / 10000
```

В MVP `tap_value` можно не включать, чтобы не усложнять дробный progress.

## 6. Визуальная обратная связь

При новом invite показывать не просто `+N секунд`, а разложение:

```text
🧬 Усиленный штамм сработал
+270 секунд

База: +180 секунд
Вирусный усилитель: +36 секунд
Мутация x2: +54 секунд
Кликер: +5 энергии к максимуму
```

В Mini App:

- экран апгрейдов рядом с кликером;
- блок "Сила следующего штамма";
- CTA: "Усилить ссылку и отправить".

## 7. API MVP

### `GET /api/mini/economy/state`

Возвращает:

- текущие DNA/RNA/CAT;
- уровни upgrades;
- цену следующего уровня;
- текущий прогноз invite bonus;
- clicker production bonuses.

### `POST /api/mini/economy/upgrade`

Тело:

```json
{ "upgrade": "viral_amplifier" }
```

Сервер:

1. Проверяет `initData`.
2. Проверяет цену.
3. Списывает DNA/RNA.
4. Повышает уровень.
5. Возвращает новое economy state.

### `POST /api/mini/economy/invite-boost`

Тело:

```json
{ "kind": "strain_boost" }
```

Сервер:

1. Списывает ресурс.
2. Создаёт `invite_boost`.
3. Возвращает boosted deep link и landing URL.

## 8. Изменения в существующем коде

### `app/services/user_service.py`

Разделить `register_new_infected`:

- оставить создание пользователя/ветки;
- вынести экономику invite bonus в `app/services/economy_service.py`;
- `register_new_infected` вызывает `apply_invite_economy(...)`.

### `app/bot/handlers/start.py`

- `_notify_inviter_new_carrier` должен получать breakdown, а не только `bonus_hours`.
- текст пуша показывает причину бонусов.

### `app/mini_app/router.py`

Добавить endpoints:

- `GET /api/mini/economy/state`
- `POST /api/mini/economy/upgrade`
- `POST /api/mini/economy/invite-boost`

### `app/mini_app/static/index.html`

Вкладка "Лаба" / кликер:

- блок апгрейдов;
- кнопка "Усилить штамм";
- прогноз следующего invite.

## 9. Баланс MVP

Стартовые параметры:

| Параметр | Значение |
|---|---:|
| base invite bonus | `settings.bonus_hours_per_referral` |
| Вирусный усилитель per level | `+10%` |
| Вирусный усилитель max | `10` |
| Шанс мутации per level | `+2% x2` |
| Boosted invite cost | `100 DNA` |
| Boosted invite multiplier | `1.5x` |
| Direct invite max energy bonus | `+5` |
| Direct invite regen bonus | `+20 bps` |

Главное ограничение:

- кликер не даёт время напрямую;
- boosted invite сгорает только при новом пользователе;
- повторные/существующие игроки не расходуют boost.

## 10. Acceptance Criteria

- **AC-ECO-01** Кликер производит DNA/RNA, но не увеличивает `timer_ends_at` напрямую.
- **AC-ECO-02** Игрок может купить `Вирусный усилитель` за DNA/RNA.
- **AC-ECO-03** `Вирусный усилитель` увеличивает время за следующего нового direct invite.
- **AC-ECO-04** `Шанс мутации` даёт шанс x2/x3 invite bonus.
- **AC-ECO-05** Игрок может создать boosted invite link за DNA.
- **AC-ECO-06** Boosted invite link действует на одного нового игрока и имеет TTL.
- **AC-ECO-07** Новый direct infected увеличивает производственные параметры кликера inviter.
- **AC-ECO-08** Пуш inviter показывает breakdown: база, апгрейды, мутация, boost.
- **AC-ECO-09** Повторное заражение / уже существующий игрок не начисляет бонусы и не тратит boost.
- **AC-ECO-10** Все экономические эффекты считаются на сервере.
- **AC-ECO-11** Mini App показывает прогноз "сила следующего штамма".
- **AC-ECO-12** Existing referral links продолжают работать.

## 11. Риски и побочные эффекты

- **Инфляция времени:** stacking `Вирусный усилитель + boosted invite + mutation` может слишком сильно продлевать таймер. Смягчение: max levels, дневной cap на boosted invites, telemetry по среднему bonus seconds.
- **Обесценивание рефералок:** если кликер производит слишком много DNA, игроки будут фармить boosts без шеринга. Смягчение: boost срабатывает только на нового infected, а время всё равно приходит через invite.
- **Сложность UX:** игрок может не понять разницу между upgrade и boosted link. Смягчение: один CTA "Усилить штамм перед отправкой" и breakdown после успеха.
- **Злоупотребление одноразовыми ссылками:** boosted token нельзя расходовать на существующих игроков; нужен TTL и `uses < max_uses` под транзакцией.
- **Гонки при регистрации:** два старта по одному boosted token должны атомарно обновлять `uses`. Нужен row lock / транзакционная проверка.
- **Нагрузка на Mini App:** экран экономики добавляет API calls. Смягчение: один `economy/state` и optimistic UI только после серверного ответа.
- **Миграции продакшена:** новые поля/таблица требуют Alembic и аккуратного deploy через Docker Compose.

## 12. План внедрения после Approval

1. Миграция БД: `invite_boosts`, clicker production bonus fields.
2. `economy_service.py`: цены, уровни, расчёт invite breakdown.
3. Расширение referral resolver под `b_<token>`.
4. Подключение экономики в `register_new_infected`.
5. Bot copy для breakdown-уведомлений.
6. Mini App endpoints и UI upgrades/boosted invite.
7. Проверки: unit/service tests для расчётов и manual deploy на сервер с restart `api`/`bot`.
