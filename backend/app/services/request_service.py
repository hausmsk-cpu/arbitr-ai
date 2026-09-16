"""Сервис запросов в госорганы."""

import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.request import Request, RequestStatus, SendingMethod


class RequestService:
    """Бизнес-логика запросов и их жизненного цикла."""

    @staticmethod
    async def send_request(
        db: AsyncSession,
        request: Request,
        method: SendingMethod = SendingMethod.API,
    ) -> Request:
        """Перевод запроса в статус «отправлено»."""
        request.status = RequestStatus.SENT
        request.sending_method = method
        request.sent_at = datetime.now(UTC)
        # TODO: реальная отправка через адаптер (ФНС / Росреестр / Почта)
        await db.flush()
        await db.refresh(request)
        return request

    @staticmethod
    async def register_response(
        db: AsyncSession,
        request: Request,
        response_data: str,
    ) -> Request:
        """Регистрация ответа органа."""
        request.status = RequestStatus.RESPONSE_RECEIVED
        request.response_data = response_data
        request.response_at = datetime.now(UTC)
        await db.flush()
        await db.refresh(request)
        return request

    @staticmethod
    async def mark_error(db: AsyncSession, request: Request, error: str) -> Request:
        """Фиксация ошибки."""
        request.status = RequestStatus.ERROR
        request.response_data = error
        await db.flush()
        await db.refresh(request)
        return request