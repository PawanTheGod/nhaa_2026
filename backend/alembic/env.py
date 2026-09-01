"""Alembic environment for NHAA Case API.

Uses async SQLAlchemy to support both Supabase PostgreSQL and SQLite dev.
"""
import asyncio
import sys
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from logging.config import fileConfig

from alembic import context

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from app.models import (  # noqa: E402
    Cases, Victims, RiskAssessments, Officers,
    Notifications, AuditLogs, SlaDeadlines,
)
from app.database import Base  # noqa: E402

target_metadata = Base.metadata

db_url = os.environ.get("DATABASE_URL", "sqlite+aiosqlite:///./dev.db")
db_url = db_url.replace("asyncpg", "psycopg2").replace("aiosqlite", "sqlite")
db_url = db_url.replace("%", "%%")
config.set_main_option("sqlalchemy.url", db_url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_types=True,
    )
    with context.connect() as conn:
        context.run_migrations(connection=conn)


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_types=True,
    )
    context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode using the async engine."""
    async_url = os.environ.get("DATABASE_URL", "sqlite+aiosqlite:///./dev.db")
    connectable = create_async_engine(
        async_url,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
