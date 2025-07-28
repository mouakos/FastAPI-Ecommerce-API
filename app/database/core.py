from collections.abc import AsyncGenerator
import random
from sqlmodel import SQLModel, select
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from passlib.hash import bcrypt
from faker import Faker

from app.users.schemas import UserRole
from app.models import *  # noqa: F403
from app.core.config import settings
from app.models.user import Gender, User

fake = Faker()

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
        # await create_admin()
        # await seed_users(50)


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


fake = Faker()

async def seed_users(count: int = 50):
    async with AsyncSession(async_engine) as session:
        # Check if users already exist
        result = await session.exec(select(User))
        if result.first():
            print("Users already exist. Skipping seeding.")
            return

        await create_admin()
        users = []
        for _ in range(count):
            gender = random.choice(list(Gender))
            role = random.choice(list(UserRole))
            dob = fake.date_of_birth(minimum_age=18, maximum_age=60)

            user = User(
                email=fake.unique.email(),
                password_hash=bcrypt.hash("12345678"),
                full_name=fake.name_male()
                if gender == Gender.male
                else fake.name_female(),
                gender=gender,
                date_of_birth=dob,
                phone_number=fake.phone_number(),
                role=role,
            )
            users.append(user)

        session.add_all(users)
        try:
            await session.commit()
            print(f"Seeded {count} users successfully.")
        except IntegrityError as e:
            await session.rollback()
            print("Seeding failed due to integrity error:", e)
