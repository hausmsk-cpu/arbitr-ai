"""Миграции базы данных (Alembic)."""

from sqlalchemy import MetaData

from alembic import context

from app.core.config import get_settings
from app.core.database import Base
from app import models  # noqa: F401  — регистрация моделей

config = context.config
settings = get_settings()
target_metadata: MetaData = Base.metadata


def run_migrations_offline() -> None:
    """Миграции в офлайн-режиме."""
    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Миграции в онлайн-режиме (async)."""

    import asyncio

    from sqlalchemy.ext.asyncio import async_engine_from_config

    def do_run_migrations(connection) -> None:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

    async def run_async_migrations() -> None:
        connectable = async_engine_from_config(
            {"sqlalchemy.url": settings.DATABASE_URL},
            prefix="sqlalchemy.",
        )
        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)
        await connectable.dispose()

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()