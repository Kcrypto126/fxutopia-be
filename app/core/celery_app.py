from celery import Celery
from ..config import get_settings

settings = get_settings()

celery_app = Celery(
    "fxutopia",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
)