from celery import Celery
from celery.schedules import crontab
import os

redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery_app: Celery = Celery(
    "agrisim",
    broker=redis_url,
    backend=redis_url,
    include=["agrisim.tasks.weather_tasks"],
)

celery_app.conf.update(
    result_expires=3600,
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "fetch-weather-every-hour": {
            "task": "tasks.poll_all_fields_weather",
            "schedule": crontab(minute=0),  # Runs at the top of every hour
        },
    },
)