from typing import Generic, TypeVar, Union

from pydantic import BaseModel
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, id: int) -> Union[ModelType, None]:
        return await db.get(self.model, id)

    async def get_list(
        self, db: AsyncSession, *, skip_id: int = 0, limit: int = 100
    ) -> list[ModelType]:
        result = await db.scalars(
            select(self.model).where(self.model.id > skip_id).limit(limit)
        )

        return result.all()

    async def create(self, db: AsyncSession, obj_in: CreateSchemaType) -> int:
        result = await db.scalars(
            insert(self.model).values(obj_in.dict()).returning(self.model.id)
        )

        return result.one()

    async def update(self, db: AsyncSession, id: int, obj_in: UpdateSchemaType) -> bool:
        result = await db.execute(
            update(self.model)
            .values(obj_in.dict(exclude_unset=True))
            .where(self.model.id == id)
        )

        return result.rowcount > 0

    async def delete(self, db: AsyncSession, id: int) -> bool:
        result = await db.execute(delete(self.model).where(self.model.id == id))

        return result.rowcount > 0
