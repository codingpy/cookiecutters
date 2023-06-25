from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db import async_session


async def get_db() -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    async with async_session() as session:
        yield session
