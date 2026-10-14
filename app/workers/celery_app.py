from celery import Celery
from celery.schedules import schedule

from app.core.config import get_settings


def create_celery_app() -> Celery:
    settings = get_settings()
    celery_app = Celery(
        "deribit_prices",
        broker=settings.redis_url,
        backend=settings.redis_url,
        include=["app.workers.tasks"],
    )
    celery_app.conf.update(
        timezone="UTC",
        enable_utc=True,
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        beat_schedule={
            "fetch-prices-every-minute": {
                "task": "app.workers.tasks.fetch_and_store_prices",
                "schedule": schedule(run_every=settings.fetch_interval_seconds),
            },
        },
    )
    return celery_app


celery_app = create_celery_app()
