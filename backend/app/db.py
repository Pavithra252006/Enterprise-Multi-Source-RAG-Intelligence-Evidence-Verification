"""
db.py - Async SQLAlchemy engine + session factory.
Call `init_db()` on startup to create all tables.
"""
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

settings = get_settings()

# asyncpg does not accept ssl=... as a URL query param;
# strip it and pass ssl=False via connect_args instead.
_db_url = settings.DATABASE_URL.split("?")[0]

engine = create_async_engine(
    _db_url,
    echo=(settings.APP_ENV == "development"),
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    connect_args={"ssl": False},
)

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
