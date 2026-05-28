"""
ConstructMind AI - Database Configuration
Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744

Async SQLAlchemy engine and session setup using aiosqlite for SQLite.
Provides session dependency for FastAPI route injection.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# ── Async Engine ─────────────────────────────────────────────────
# For SQLite we need check_same_thread=False because FastAPI uses
# multiple threads via async; echo=True in dev for SQL logging.
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    pool_pre_ping=True,
)

# ── Session Factory ──────────────────────────────────────────────
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ── Declarative Base ─────────────────────────────────────────────
class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass


# ── Dependency ───────────────────────────────────────────────────
async def get_db() -> AsyncSession:  # type: ignore[misc]
    """
    FastAPI dependency that yields an async database session.
    Automatically commits on success, rolls back on exception.
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables() -> None:
    """Create all database tables from ORM models."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables() -> None:
    """Drop all database tables (use only in testing)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
