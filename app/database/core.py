from collections.abc import AsyncGenerator
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from app.models import *  # noqa: F403
from app.config import settings


async_engine = create_async_engine(settings.DATABASE_URL, echo=True)

local_session = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db():
    """Initialize the database by creating all tables."""
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a session for database operations."""

    async_session = local_session()
    async with async_session as session:
        yield session
