"""Схемы пользователей и аутентификации."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """Регистрация пользователя."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=2, max_length=255)


class UserRead(BaseModel):
    """Публичное представление пользователя."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    full_name: str
    role: str
    created_at: datetime


class LoginRequest(BaseModel):
    """Запрос на вход."""

    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT-токен."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int