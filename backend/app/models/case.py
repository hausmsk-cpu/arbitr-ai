"""Дело о банкротстве: должник, кредиторы, имущество, документы."""

import enum
import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class CaseStatus(str, enum.Enum):
    DRAFT = "draft"                     # черновик
    PREPARING = "preparing"             # подготовка к подаче
    SUBMITTED = "submitted"             # заявление подано
    IN_PROCEDURE = "in_procedure"       # процедура идёт
    COMPLETED = "completed"             # завершено
    TERMINATED = "terminated"           # прекращено
    ARCHIVED = "archived"               # архив


class ProcedureType(str, enum.Enum):
    OBSERVATION = "observation"         # наблюдение
    FINANCIAL_RECOVERY = "recovery"     # финансовое оздоровление
    EXTERNAL_MANAGEMENT = "external"    # внешнее управление
    BANKRUPTCY = "bankruptcy"           # конкурсное производство
    DEBT_RESTRUCTURE = "restructure"    # реструктуризация долгов
    SALE_OF_PROPERTY = "sale"           # реализация имущества


class Case(Base):
    """Дело о банкротстве физического лица."""

    __tablename__ = "cases"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    case_number: Mapped[str | None] = mapped_column(String(64), unique=True)  # А41-12345/2024
    manager_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    court_name: Mapped[str] = mapped_column(String(255))
    court_region: Mapped[str] = mapped_column(String(128))

    status: Mapped[CaseStatus] = mapped_column(Enum(CaseStatus), default=CaseStatus.DRAFT)
    procedure_type: Mapped[ProcedureType | None] = mapped_column(Enum(ProcedureType))

    application_date: Mapped[date | None] = mapped_column(Date)
    procedure_start_date: Mapped[date | None] = mapped_column(Date)
    procedure_end_date: Mapped[date | None] = mapped_column(Date)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    manager = relationship("User", back_populates="cases")
    debtors = relationship(
        "Debtor",
        back_populates="case",
        cascade="all, delete-orphan",
    )
    creditors = relationship(
        "Creditor",
        back_populates="case",
        cascade="all, delete-orphan",
    )
    properties = relationship(
        "Property",
        back_populates="case",
        cascade="all, delete-orphan",
    )
    documents = relationship(
        "Document",
        back_populates="case",
        cascade="all, delete-orphan",
    )
    requests = relationship(
        "Request",
        back_populates="case",
        cascade="all, delete-orphan",
    )


class Debtor(Base):
    """Должник (физическое лицо) по делу."""

    __tablename__ = "debtors"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("cases.id"))
    full_name: Mapped[str] = mapped_column(String(255))
    inn: Mapped[str | None] = mapped_column(String(12))
    snils: Mapped[str | None] = mapped_column(String(14))
    birth_date: Mapped[date | None] = mapped_column(Date)
    address: Mapped[str | None] = mapped_column(Text)
    passport_series: Mapped[str | None] = mapped_column(String(4))
    passport_number: Mapped[str | None] = mapped_column(String(6))
    passport_issue_date: Mapped[date | None] = mapped_column(Date)
    passport_issued_by: Mapped[str | None] = mapped_column(String(512))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    case = relationship("Case", back_populates="debtors")
    properties = relationship("Property", back_populates="debtor")


class Creditor(Base):
    """Кредитор в деле о банкротстве."""

    __tablename__ = "creditors"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("cases.id"))
    name: Mapped[str] = mapped_column(String(255))          # ИП или наименование юрлица
    inn: Mapped[str | None] = mapped_column(String(12))
    kpp: Mapped[str | None] = mapped_column(String(9))
    is_legal_entity: Mapped[bool] = mapped_column(default=False)

    claim_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0"))
    claim_currency: Mapped[str] = mapped_column(String(3), default="RUB")
    claim_basis: Mapped[str | None] = mapped_column(Text)   # основание требования
    status_in_registry: Mapped[str | None] = mapped_column(String(64))  # включено / заявлено / отклонено

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    case = relationship("Case", back_populates="creditors")


class Property(Base):
    """Имущество должника."""

    __tablename__ = "properties"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("cases.id"))
    debtor_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("debtors.id"))

    property_type: Mapped[str] = mapped_column(String(64))  # недвижимость, транспорт, счёт, доля в ООО
    description: Mapped[str | None] = mapped_column(Text)
    address: Mapped[str | None] = mapped_column(Text)
    cadastral_number: Mapped[str | None] = mapped_column(String(64))
    estimated_value: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    sale_value: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    is_preserved: Mapped[bool] = mapped_column(default=False)   # арест/запрет

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    case = relationship("Case", back_populates="properties")
    debtor = relationship("Debtor", back_populates="properties")


class Document(Base):
    """Документ по делу (скан, сгенерированный файл)."""

    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("cases.id"))

    title: Mapped[str] = mapped_column(String(255))
    doc_type: Mapped[str] = mapped_column(String(64))       # запрос, отчёт, ходатайство, уведомление
    file_key: Mapped[str] = mapped_column(String(512))      # ключ в MinIO
    mime_type: Mapped[str] = mapped_column(String(64), default="application/pdf")
    size_bytes: Mapped[int] = mapped_column(default=0)
    generated_by_ai: Mapped[bool] = mapped_column(default=False)
    version: Mapped[int] = mapped_column(default=1)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    case = relationship("Case", back_populates="documents")