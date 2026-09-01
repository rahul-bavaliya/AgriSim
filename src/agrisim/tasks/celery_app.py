import os
from celery import Celery

redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery_app: Celery = Celery(
    "agrisim",
    broker=redis_url,
    backend=redis_url,
    include=["agrisim.tasks.weather_tasks"],  # Ensures task discovery
)

celery_app.conf.update(  # type: ignore[attr-defined]
    result_expires=3600,
    timezone="UTC",
    enable_utc=True,
)
