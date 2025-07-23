from collections.abc import AsyncGenerator
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

from src.models import *  # noqa: F403
from src.config import settings

engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL, echo=True, future=True, expire_on_commit=False
)


async def init_db():
    """Initialize the database by creating all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None, None]:
    """Get a session for database operations."""
    async with AsyncSession(engine) as session:
        yield session
