"""
db.py - Async SQLAlchemy engine + session factory.
Call `init_db()` on startup to create all tables.
"""
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

settings = get_settings()

import ssl

def _build_engine():
    raw_url = settings.DATABASE_URL.strip()
    if raw_url.startswith("sqlite"):
        eng = create_async_engine(
            raw_url,
            echo=(settings.APP_ENV == "development"),
        )
        return eng, True

    # Standardize postgres scheme to postgresql+asyncpg://
    if raw_url.startswith("postgres://"):
        raw_url = "postgresql+asyncpg://" + raw_url[len("postgres://"):]
    elif raw_url.startswith("postgresql://") and not raw_url.startswith("postgresql+asyncpg://"):
        raw_url = "postgresql+asyncpg://" + raw_url[len("postgresql://"):]

    # Strip query parameters that asyncpg doesn't support as URL params
    has_ssl_param = any(p in raw_url for p in ["ssl=true", "sslmode=require", "ssl=require"])
    clean_url = raw_url.split("?")[0]

    connect_args = {}
    if has_ssl_param or any(host in clean_url for host in ["render.com", "neon.tech", "supabase.co", "aws.com"]):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        connect_args["ssl"] = ctx
    else:
        connect_args["ssl"] = False

    eng = create_async_engine(
        clean_url,
        echo=(settings.APP_ENV == "development"),
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        connect_args=connect_args,
    )
    return eng, False

engine, is_sqlite = _build_engine()

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Single declarative base shared by all ORM models."""
    pass


async def get_db() -> AsyncSession:
    """FastAPI dependency: yields an async DB session."""
    async with AsyncSessionLocal() as session:
        yield session


async def init_db() -> None:
    """Create all tables. Called from lifespan startup."""
    from app import models  # noqa: F401 – registers all models
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        if not is_sqlite:
            # create_all never alters existing tables; add columns introduced later.
            await conn.exec_driver_sql("ALTER TABLE chunks ADD COLUMN IF NOT EXISTS source TEXT")

