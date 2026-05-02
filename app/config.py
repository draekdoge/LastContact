from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    bot_token: str = ""
    """Обязателен для сервиса бота и для Celery-уведомлений; API может стартовать без него."""

    bot_admin_telegram_ids: str = Field(
        default="6805465388,7670490295",
        validation_alias="BOT_ADMIN_TELEGRAM_IDS",
        description="Через запятую: telegram user id с доступом к reply-меню «Админка» в боте.",
    )

    telegram_delivery: Literal["polling", "webhook"] = "polling"
    """polling — long polling (удобно локально); webhook — нужен публичный HTTPS."""

    webhook_secret: str = ""
    """Только для webhook: заголовок X-Telegram-Bot-Api-Secret-Token (пусто = не проверять)."""

    webhook_path: str = "/webhook"
    """Только для webhook: путь POST на вашем сервере."""

    webhook_base_url: str = ""
    """Публичный HTTPS origin без завершающего слэша, например https://bot.example.com — для setWebhook при старте."""

    mini_app_public_url: str = Field(
        default="",
        validation_alias="MINI_APP_PUBLIC_URL",
        description="Публичный HTTPS origin Mini App, например https://host (страница отдаётся с GET /).",
    )

    launch_mode: bool = False
    """Удлинённый стартовый таймер (имитация period=launch)."""

    database_url: str
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "amqp://guest:guest@localhost:5672//"
    celery_result_backend: str = "redis://localhost:6379/1"

    default_timer_hours: float = 72.0
    """Базовое окно до кризиса (ч). 72 ч — ребаланс под глобальную аудиторию (v2)."""

    launch_timer_hours: float = 72.0
    """При LAUNCH_MODE=true — более длинный стартовый горизонт (первые 7 дней)."""

    bonus_hours_per_referral: float = 4.0
    """+часов таймера за подтверждённое заражение. Ребаланс под новый базовый горизонт (v2)."""

    immune_duration_hours: float = 24.0
    """Длительность иммунитета после активации из состояния зомби (часы)."""

    sleeping_no_spread_hours: float = 4.0
    """[DEPRECATED v2] Нет исходящих заражений дольше N ч — режим «спящего». Заменяется Лабораторией."""

    sleeping_tick_bonus_seconds: int = 0
    """[DEPRECATED v2] Продление в режиме сна. 0 = отключено. Заменяется Лабораторией."""

    warn_before_hours: float = 2.0
    warn_before_hours_1: float = 1.0
    """Отдельное push-уведомление «мало времени» — за час до кризиса."""

    warn_before_minutes_30: float = 30.0
    warn_before_minutes_10: float = 10.0

    # ── Лаборатория ──────────────────────────────────────────────────────────
    lab_analysis_minutes: int = 45
    """Задержка анализа (шаг 2 Лабы), минуты."""

    lab_daily_limit_infected: int = 2
    """Максимум циклов Лабы в UTC-сутки для Infected."""

    lab_daily_limit_zombie: int = 1
    """Максимум циклов Лабы воскрешения для Zombie в UTC-сутки."""

    lab_reward_hours_min: int = 4
    """Минимальный бонус часов за цикл Лабы (infected)."""

    lab_reward_hours_max: int = 8
    """Максимальный бонус часов за цикл Лабы (infected)."""

    lab_revival_streak_needed: int = 3
    """Циклов подряд для воскрешения через Лабу."""

    # ── Фонтан жизни ─────────────────────────────────────────────────────────
    fountain_interval_hours: int = 60
    """Интервал между ивентами Фонтана (ч)."""

    fountain_window_hours: int = 24
    """Длительность окна активности Фонтана (ч)."""

    fountain_announce_before_hours: int = 6
    """Оповещение за N ч до открытия."""

    fountain_npc_dau_threshold: int = 500
    """При DAU ниже этого значения NPC докидывают прогресс до 75%."""

    fountain_pour_daily_unit_cap: int = 20
    """Суммарно единиц реагентов (DNA+RNA+CAT) в Фонтан за UTC-сутки на игрока."""

    reagent_weight_dna: float = 1.0
    """Вес вклада одной единицы DNA в Фонтан."""

    reagent_weight_rna: float = 3.0
    """Вес вклада одной единицы RNA в Фонтан."""

    reagent_cat_mult: float = 0.25
    """Множитель за каждую единицу CAT: итог = base * (1 + cat * mult)."""

    invite_regen_boost_hours: float = Field(default=5.0, validation_alias="INVITE_REGEN_BOOST_HOURS")
    """Окно временного ускорения регена кликера после нового инвайта: продлевается от max(текущий конец, сейчас)."""

    invite_regen_boost_bps: int = Field(default=5000, validation_alias="INVITE_REGEN_BOOST_BPS")
    """Величина bps в этом окне (не стакается; только продление времени)."""

    mini_app_online_presence_seconds: int = Field(
        default=180,
        validation_alias="MINI_APP_ONLINE_PRESENCE_SECONDS",
    )
    """Реферал «онлайн» для бонуса регена: mini_app_last_seen_at новее N секунд."""

    # ── Штаммы / дебаффы ─────────────────────────────────────────────────────
    affliction_check_minutes: int = 120
    """Интервал Celery Beat для strain_afflictions_tick (`worker/celery_app.py`). Должен совпадать с прод-настройкой воркера."""
    affliction_cooldown_hours: int = 36
    affliction_duration_hours: int = 36
    affliction_min_strain_size: int = 4
    affliction_base_chance: float = 0.03
    affliction_chance_cap: float = 0.08

    affliction_research_daily_cap: int = 2


@lru_cache
def get_settings() -> Settings:
    return Settings()


def parse_admin_telegram_ids(raw: str) -> frozenset[int]:
    if not (raw or "").strip():
        return frozenset()
    out: list[int] = []
    for part in raw.split(","):
        p = part.strip()
        if not p:
            continue
        try:
            out.append(int(p))
        except ValueError:
            continue
    return frozenset(out)
