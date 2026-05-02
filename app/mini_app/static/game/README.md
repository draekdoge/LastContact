# Mini App · игровые ассеты (`/game/`)

Всё здесь раздаётся **публично** без `Authorization` (Telegram может кешировать CDN). Не клади секретов.

## Как добавить Lottie или картинку

1. Положи файл, например:
   - `assets/lottie/status-hero.json` или `status-hero.lottie`
   - `assets/img/world-map.png`
2. Открой `manifest.json`, заполни путь **относительно папки `game/`**:
   ```json
   "lottie": {
     "statusHero": "assets/lottie/status-hero.json",
     "clickerCore": "assets/lottie/virus-tap.json",
     "labDnaFoot": "assets/lottie/dna.json",
     "fountainBackdrop": "assets/lottie/fountain.json"
   }
   ```
3. Обнови `version` в `manifest.json`, чтобы пробить кеш клиента при необходимости.

Слоты `lottie.*` связаны с `data-game-lottie-slot` в `index.html` (те же ключи camelCase).

## Спонсоры и платные дорожки (заготовка)

- `progression.sponsorSlots[]` — вставки в заранее размеченные места (`data-sponsor-slot="..."`). Пока `enabled: false`, блоки скрыты.
- `progression.paidTracks[]` — резерв под будущие пакеты прокачки; бэкенд потом может мерджить сюда конфиг через `remoteConfigUrl`.
- `progression.remoteConfigUrl` — опционально URL JSON (тот же форма фрагментов темы/`lottie`/`sponsorSlots`) для оперативных кампаний без деплоя.

## Файлы

| Файл | Назначение |
|------|------------|
| `manifest.json` | Тема, пути ассетов, слоты спонсоров |
| `bootstrap.js` | Загрузка манифеста, применение темы, монтирование Lottie/HTML баннеров |
| `assets/lottie/` | `.json` (Lottie) или `.lottie` (DotLottie, если плеер поддержит) |
| `assets/img/` | PNG/WebP |

Для продакшена можно вынести тяжёлые файлы на CDN и в `manifest.json` указать абсолютные `https://...` (тогда поправь `bootstrap.js`: сейчас пути склеиваются с `/game/` только для относительных значений — для абсолютных нужна доработка).
