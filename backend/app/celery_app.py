"""Celery-приложение для асинхронных задач Arbitr AI."""

from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "Arbitr AI",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Europe/Moscow",
    enable_utc=True,
    task_track_started=True,
    worker_max_tasks_per_child=200,
)

celery_app.autodiscover_tasks(["app.tasks"])