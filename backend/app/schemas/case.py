"""Схемы дел, должников, кредиторов, имущества."""

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CaseCreate(BaseModel):
    """Создание дела."""

    case_number: str | None = None
    court_name: str = Field(min_length=3, max_length=255)
    court_region: str = Field(min_length=3, max_length=128)
    procedure_type: str | None = None


class CaseUpdate(BaseModel):
    """Обновление дела."""

    case_number: str | None = None
    court_name: str | None = None
    court_region: str | None = None
    status: str | None = None
    procedure_type: str | None = None
    application_date: date | None = None
    procedure_start_date: date | None = None
    procedure_end_date: date | None = None


class CaseRead(BaseModel):
    """Представление дела."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    case_number: str | None
    court_name: str
    court_region: str
    status: str
    procedure_type: str | None
    application_date: date | None
    procedure_start_date: date | None
    procedure_end_date: date | None
    created_at: datetime
    updated_at: datetime


class DebtorCreate(BaseModel):
    """Создание должника."""

    full_name: str = Field(min_length=2, max_length=255)
    inn: str | None = Field(default=None, max_length=12)
    snils: str | None = Field(default=None, max_length=14)
    birth_date: date | None = None
    address: str | None = None


class DebtorRead(BaseModel):
    """Представление должника."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    full_name: str
    inn: str | None
    snils: str | None
    birth_date: date | None
    address: str | None


class CreditorCreate(BaseModel):
    """Создание кредитора."""

    name: str = Field(min_length=2, max_length=255)
    inn: str | None = Field(default=None, max_length=12)
    kpp: str | None = Field(default=None, max_length=9)
    is_legal_entity: bool = False
    claim_amount: Decimal = Decimal("0")
    claim_basis: str | None = None


class CreditorRead(BaseModel):
    """Представление кредитора."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    inn: str | None
    kpp: str | None
    is_legal_entity: bool
    claim_amount: Decimal
    claim_currency: str
    claim_basis: str | None
    status_in_registry: str | None


class PropertyCreate(BaseModel):
    """Создание имущества."""

    property_type: str = Field(min_length=2, max_length=64)
    description: str | None = None
    address: str | None = None
    cadastral_number: str | None = None
    estimated_value: Decimal | None = None


class PropertyRead(BaseModel):
    """Представление имущества."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    property_type: str
    description: str | None
    address: str | None
    cadastral_number: str | None
    estimated_value: Decimal | None
    sale_value: Decimal | None
    is_preserved: bool


class DocumentRead(BaseModel):
    """Представление документа."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    doc_type: str
    mime_type: str
    size_bytes: int
    generated_by_ai: bool
    version: int
    created_at: datetime