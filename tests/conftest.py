import asyncio
from unittest import mock

import pytest
import pytest_asyncio

from fastapi.testclient import TestClient
from redis import StrictRedis
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from main import app
from src.conf.config import config
from src.database.models import Base, User
from src.database.db import get_db
from src.services.auth import auth_service
from utils.cache import RedisCache

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
)

TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)

test_user = {"username": "test_user", "email": "test@example.com", "password": "12345678"}


@pytest.fixture(scope="module", autouse=True)
def init_models_wrap():
    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        async with TestingSessionLocal() as session:
            hash_password = auth_service.get_password_hash(test_user["password"])
            current_user = User(username=test_user["username"],
                                email=test_user["email"],
                                password=hash_password,
                                confirmed=True)
            session.add(current_user)
            await session.commit()

    asyncio.run(init_models())


@pytest.fixture(scope="module")
def client():
    # Dependency override

    async def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        except Exception as err:
            print(err)
            await session.rollback()
        finally:
            await session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)


@pytest_asyncio.fixture()
async def get_token():
    token = await auth_service.create_access_token(data={"sub": test_user.get("email")})
    return token


@pytest.fixture(scope="session")
def redis_test_client():
    redis = StrictRedis(
        host=config.REDIS_DOMAIN,
        port=config.REDIS_PORT,
        db=1
    )
    yield redis
    redis.flushall()


@pytest.fixture(scope="function", autouse=True)
def mock_cache_decorator(monkeypatch, redis_test_client):
    mock_cache = mock.Mock(return_value=mock.Mock())
    monkeypatch.setattr("utils.cache.RedisCache.cache", mock_cache)  # Подмена декоратора
    monkeypatch.setattr("utils.cache.RedisCache.redis", redis_test_client)  # Подмена клиента
    yield mock_cache

