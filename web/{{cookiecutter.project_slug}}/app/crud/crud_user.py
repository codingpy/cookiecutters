from typing import Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_password_hash, verify_password
from app.models import User
from app.schemas import UserCreate, UserUpdate

from .base import CRUDBase


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_email(self, db: AsyncSession, email: str) -> Union[User, None]:
        result = await db.scalars(select(User).where(User.email == email))

        return result.first()

    async def create(self, db: AsyncSession, obj_in: UserCreate) -> int:
        obj_in: dict = obj_in.dict()

        obj_in["hashed_password"] = get_password_hash(obj_in.pop("password"))

        return await super().create(db, obj_in)

    async def update(self, db: AsyncSession, id: int, obj_in: UserUpdate) -> bool:
        obj_in: dict = obj_in.dict(exclude_unset=True)

        if "password" in obj_in:
            obj_in["hashed_password"] = get_password_hash(obj_in.pop("password"))

        return await super().update(db, id, obj_in)

    async def authenticate(
        self, db: AsyncSession, email: str, password: str
    ) -> Union[User, None]:
        user = await self.get_by_email(db, email)
        if user and verify_password(password, user.hashed_password):
            return user


user = CRUDUser(User)
