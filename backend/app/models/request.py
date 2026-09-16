"""Модуль запросов в госорганы и отслеживание статусов."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class RequestStatus(str, enum.Enum):
    DRAFT = "draft"                 # черновик
    PENDING = "pending"             # ожидает отправки
    SENT = "sent"                   # отправлено
    DELIVERED = "delivered"         # доставлено
    WAITING_RESPONSE = "waiting"    # ждём ответ
    PARTIAL_RESPONSE = "partial"    # частичный ответ
    RESPONSE_RECEIVED = "response"  # ответ получен
    REJECTED = "rejected"           # отказ
    ERROR = "error"                 # ошибка


class SendingMethod(str, enum.Enum):
    API = "api"             # прямое API (СМЭВ и т.п.)
    E_LETTER = "e_letter"   # электронное заказное письмо (Почта России)
    RPA = "rpa"             # автоматизация портала (Playwright)
    MANUAL = "manual"       # ручная отправка


class Request(Base):
    """Запрос в государственный орган, банк или иной контрагент."""

    __tablename__ = "requests"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("cases.id"))

    request_type: Mapped[str] = mapped_column(String(64))  # fns, rosreestr, fssp, bank, post
    title: Mapped[str] = mapped_column(String(255))
    target_org: Mapped[str] = mapped_column(String(255))    # ФНС №, банк, орган

    status: Mapped[RequestStatus] = mapped_column(Enum(RequestStatus), default=RequestStatus.DRAFT)
    sending_method: Mapped[SendingMethod] = mapped_column(Enum(SendingMethod), default=SendingMethod.API)

    content: Mapped[str | None] = mapped_column(Text)       # текст запроса
    document_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("documents.id"))
    external_tracking: Mapped[str | None] = mapped_column(String(128))  # ШПИ / номер в СМЭВ
    response_data: Mapped[str | None] = mapped_column(Text)             # JSON ответа органа

    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    response_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    case = relationship("Case", back_populates="requests")
    document = relationship("Document")