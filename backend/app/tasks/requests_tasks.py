"""Фоновые задачи по запросам в госорганы."""

import logging

from app.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.send_request")
def send_request_task(request_id: str) -> dict:
    """Отправка запроса в госорган (API / почта)."""
    logger.info("Sending request %s", request_id)
    # TODO: подставить реальную отправку через адаптер интеграции
    return {"status": "sent", "request_id": request_id}


@celery_app.task(name="app.tasks.track_request")
def track_request_task(tracking_number: str) -> dict:
    """Отслеживание статуса отправленного запроса (ШПИ)."""
    logger.info("Tracking request %s", tracking_number)
    # TODO: опрос API Почты России / СМЭВ
    return {"status": "tracked", "tracking": tracking_number}