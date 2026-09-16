"""Точка входа FastAPI-приложения Arbitr AI."""

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.core.config import get_settings

settings = get_settings()

logger = structlog.get_logger()

app = FastAPI(
    title="ArbitrAI API",
    version=settings.APP_VERSION,
    description="AI-платформа для финансового управляющего в делах о банкротстве физлиц",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    """Проверка живости сервиса."""
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}


@app.get("/", tags=["system"])
async def root() -> dict[str, str]:
    """Корень API."""
    return {
        "app": settings.APP_NAME,
        "docs": "/docs",
        "health": "/health",
    }