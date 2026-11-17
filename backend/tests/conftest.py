import sys
import asyncio
import pytest

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# pyrefly: ignore [missing-import]
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.postgres import async_session_maker
from app.db.redis import connect_to_redis, close_redis_connection
from app.db.mongodb import connect_to_mongo, close_mongo_connection

@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_databases():
    await connect_to_mongo()
    await connect_to_redis()
    yield
    await close_mongo_connection()
    await close_redis_connection()

@pytest_asyncio.fixture(scope="function")
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

@pytest_asyncio.fixture(scope="function")
async def db_session():
    async with async_session_maker() as session:
        yield session
