"""Схемы запросов в госорганы."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RequestCreate(BaseModel):
    """Создание запроса."""

    request_type: str = Field(min_length=2, max_length=64)
    title: str = Field(min_length=3, max_length=255)
    target_org: str = Field(min_length=3, max_length=255)
    content: str | None = None
    sending_method: str = "api"


class RequestUpdate(BaseModel):
    """Обновление запроса."""

    status: str | None = None
    content: str | None = None
    external_tracking: str | None = None
    response_data: str | None = None


class RequestRead(BaseModel):
    """Представление запроса."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    request_type: str
    title: str
    target_org: str
    status: str
    sending_method: str
    content: str | None
    external_tracking: str | None
    response_data: str | None
    sent_at: datetime | None
    response_at: datetime | None
    deadline: datetime | None
    created_at: datetime