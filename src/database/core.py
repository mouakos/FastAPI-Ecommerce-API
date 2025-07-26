from collections.abc import AsyncGenerator
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from passlib.hash import bcrypt

from src.users.schemas import UserRole
from src.models import *  # noqa: F403
from src.core.config import settings
from src.models.user import Gender, User

async_engine = create_async_engine(settings.DATABASE_URL, echo=True)

async_session = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db():
    """Initialize the database by creating all tables."""
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
        await create_admin()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a session for database operations."""

    async_session = sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with async_session() as session:
        yield session


async def create_admin():
    """Create an admin user if it does not already exist."""
    async with async_session() as session:
        # Check if any admin exists
        existing = await session.exec(select(User).where(User.role == UserRole.admin))
        if existing.first():
            return

        admin = User(
            full_name=settings.ADMIN_FULL_NAME,
            email=settings.ADMIN_EMAIL,
            password_hash=bcrypt.hash(settings.ADMIN_PASSWORD),
            gender=Gender.other,
            role=UserRole.admin,
        )
        session.add(admin)
        await session.commit()
