from typing import Any, Generic, TypeVar

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

    async def get(self, db: AsyncSession, id: int) -> ModelType | None:
        return await db.get(self.model, id)

    async def get_all(
        self, db: AsyncSession, skip_id: int = 0, limit: int = 100
    ) -> list[ModelType]:
        result = await db.scalars(
            select(self.model).where(self.model.id > skip_id).limit(limit)
        )

        return result.all()

    async def create(
        self, db: AsyncSession, obj_in: CreateSchemaType | dict[str, Any]
    ) -> ModelType:
        if isinstance(obj_in, dict):
            create_data = obj_in
        else:
            create_data = obj_in.model_dump()

        result = await db.scalars(
            insert(self.model).values(create_data).returning(self.model)
        )

        return result.one()

    async def update(
        self, db: AsyncSession, id: int, obj_in: UpdateSchemaType | dict[str, Any]
    ) -> ModelType:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        result = await db.scalars(
            update(self.model)
            .values(update_data)
            .where(self.model.id == id)
            .returning(self.model)
        )

        return result.one()

    async def delete(self, db: AsyncSession, id: int) -> bool:
        result = await db.execute(delete(self.model).where(self.model.id == id))

        return result.rowcount > 0
