from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_password_hash, verify_password
from app.models import User
from app.schemas import UserCreate, UserUpdate

from .base import CRUDBase


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        result = await db.scalars(select(User).where(User.email == email))

        return result.first()

    async def create(self, db: AsyncSession, obj_in: UserCreate) -> User:
        create_data = obj_in.model_dump()

        create_data["hashed_password"] = get_password_hash(create_data.pop("password"))

        return await super().create(db, create_data)

    async def update(self, db: AsyncSession, id: int, obj_in: UserUpdate) -> User:
        update_data = obj_in.model_dump(exclude_unset=True)

        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(
                update_data.pop("password")
            )

        return await super().update(db, id, update_data)

    async def authenticate(
        self, db: AsyncSession, email: str, password: str
    ) -> User | None:
        user = await self.get_by_email(db, email)
        if user and verify_password(password, user.hashed_password):
            return user

    async def exists(self, db: AsyncSession, id: int) -> bool:
        result = await db.scalars(select(User).where(User.id == id).exists())

        return result.one()

    async def exists_email(self, db: AsyncSession, email: str) -> bool:
        result = await db.scalars(select(User).where(User.email == email).exists())

        return result.one()


user = CRUDUser(User)
