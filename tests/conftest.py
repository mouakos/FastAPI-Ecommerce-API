from httpx import AsyncClient, ASGITransport
import pytest_asyncio
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.main import app
from app.database.core import get_session

TEST_DATABASE_URL = "sqlite+aiosqlite://"

engine = create_async_engine(TEST_DATABASE_URL, echo=True)
test_session = async_sessionmaker(engine, class_=AsyncSession)


async def override_get_db():
    async_session = test_session()
    async with async_session as session:
        yield session


app.dependency_overrides[get_session] = override_get_db


@pytest_asyncio.fixture(autouse=True)
async def prepare_database():
    # Drop all tables before each test
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    # optional: clear DB after tests


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
