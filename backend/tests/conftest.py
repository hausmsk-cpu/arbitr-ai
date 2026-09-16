"""Тестовая инфраструктура: SQLite вместо PostgreSQL для юнит-тестов."""

import os
import sys
from pathlib import Path

# Указываем SQLite БД до импорта приложения
os.environ.setdefault(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./test_arbitr_ai.db",
)
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-unit-tests")

# Добавляем backend в путь импорта
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.core.database import Base, engine
from app.main import app


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    """Создаёт схему БД перед тестами и удаляет после."""
    # Проверяем, что это SQLite (юнит-тесты не должны трогать прод БД!)
    assert "sqlite" in str(engine.url), (
        "Unit tests must run against SQLite, got: %s" % engine.url
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # удаляем тестовую БД
    await engine.dispose()
    db_path = Path("test_arbitr_ai.db")
    if db_path.exists():
        db_path.unlink()


@pytest_asyncio.fixture
async def client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac