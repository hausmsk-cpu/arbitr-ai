"""Pydantic-схемы для API."""

from app.schemas.user import UserCreate, UserRead, Token, LoginRequest
from app.schemas.case import (
    CaseCreate,
    CaseRead,
    CaseUpdate,
    DebtorCreate,
    DebtorRead,
    CreditorCreate,
    CreditorRead,
    PropertyCreate,
    PropertyRead,
    DocumentRead,
)
from app.schemas.request import RequestCreate, RequestRead, RequestUpdate

__all__ = [
    "UserCreate",
    "UserRead",
    "Token",
    "LoginRequest",
    "CaseCreate",
    "CaseRead",
    "CaseUpdate",
    "DebtorCreate",
    "DebtorRead",
    "CreditorCreate",
    "CreditorRead",
    "PropertyCreate",
    "PropertyRead",
    "DocumentRead",
    "RequestCreate",
    "RequestRead",
    "RequestUpdate",
]