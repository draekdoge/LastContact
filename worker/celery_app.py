import os
from datetime import timedelta

from celery import Celery
from celery.schedules import crontab
from celery.schedules import schedule as interval_schedule

from app.config import get_settings

broker = os.environ.get("CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672//")
backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

celery_app = Celery("virus", broker=broker, backend=backend, include=["worker.tasks"])

_af_min = max(1, int(get_settings().affliction_check_minutes))

celery_app.conf.beat_schedule = {
    "timer-tick-every-minute": {
        "task": "worker.tasks.timer_tick",
        "schedule": crontab(minute="*"),
    },
    "lab-sweep-every-minute": {
        "task": "worker.tasks.lab_sweep",
        "schedule": crontab(minute="*"),
    },
    f"strain-afflictions-every-{_af_min}min": {
        "task": "worker.tasks.strain_afflictions_tick",
        # relative=True — привязка к «часам» для периода ≥ 1 ч (см. Celery Periodic Tasks).
        "schedule": interval_schedule(
            run_every=timedelta(minutes=_af_min),
            relative=_af_min >= 60,
        ),
    },
}
celery_app.conf.timezone = "UTC"
celery_app.conf.broker_connection_retry_on_startup = True
