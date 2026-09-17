from unittest.mock import AsyncMock, MagicMock

import pytest
from catboost import CatBoostRegressor
from pytest_mock import MockerFixture
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool
from testcontainers.community.postgres import PostgresContainer

from app.core.database import Base


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer(
        image="postgres:16-alpine",
        username="test",
        password="test",
        dbname="test",
    ) as pg:
        yield pg


@pytest.fixture(scope="session")
async def test_engine(
    postgres_container: PostgresContainer,
):
    host = postgres_container.get_container_host_ip()
    port = postgres_container.get_exposed_port(5432)
    username = postgres_container.username
    password = postgres_container.password
    dbname = postgres_container.dbname

    url = f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{dbname}"

    engine = create_async_engine(url, echo=False, poolclass=NullPool)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture(scope="session")
def test_session_factory(
    test_engine: AsyncEngine,
):
    return async_sessionmaker(bind=test_engine, expire_on_commit=False)


@pytest.fixture
async def db_session(
    test_session_factory: async_sessionmaker[AsyncSession],
):

    async with test_session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture
def mock_model(mocker: MockerFixture) -> MagicMock:
    model = MagicMock(spec=CatBoostRegressor)
    model.predict = mocker.MagicMock()
    return model


@pytest.fixture
def mock_session() -> AsyncMock:
    session = AsyncMock(spec=AsyncSession)
    return session


@pytest.fixture
def mock_session_factory(mock_session: AsyncMock) -> MagicMock:
    factory = MagicMock(spec=async_sessionmaker)
    factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
    factory.return_value.__aexit__ = AsyncMock(return_value=False)
    return factory



@pytest.fixture
def mock_repository_class() -> MagicMock:
    repo_class = MagicMock()

    repo_instance = MagicMock()
    repo_instance.save = AsyncMock()
    repo_instance.save_batch = AsyncMock()

    repo_class.return_value = repo_instance
    return repo_class
