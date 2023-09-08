from collections.abc import AsyncIterator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import async_session
from app.main import app
from tests.utils import get_superuser_token_headers


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def db() -> AsyncIterator[AsyncSession]:
    async with async_session() as session:
        yield session


@pytest.fixture(scope="module")
async def client() -> AsyncIterator[AsyncClient]:
    async with AsyncClient(base_url="http://test", app=app) as ac:
        yield ac


@pytest.fixture(scope="module")
async def superuser_token_headers(client: AsyncClient) -> dict[str, str]:
    return await get_superuser_token_headers(client)
