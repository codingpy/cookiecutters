from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app import crud, schemas
from app.config import settings

engine = create_async_engine(settings.sqlalchemy_database_uri)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def init_db(db: AsyncSession) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next line
    # Base.metadata.create_all(bind=engine)

    if await crud.user.exists_email(db, settings.first_superuser):
        return

    user_in = schemas.UserCreate(
        email=settings.first_superuser,
        password=settings.first_superuser_password,
        is_superuser=True,
    )
    await crud.user.create(db, user_in)
