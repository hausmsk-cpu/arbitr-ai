"""Фоновые задачи (Celery)."""

from app.tasks.requests_tasks import send_request_task, track_request_task

__all__ = ["send_request_task", "track_request_task"]