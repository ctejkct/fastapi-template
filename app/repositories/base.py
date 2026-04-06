"""Base SQLAlchemy repository implementation."""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DatabaseError, NotFoundError

OrmModelT = TypeVar("OrmModelT")
SchemaModelT = TypeVar("SchemaModelT", bound=BaseModel)


class BaseRepository(Generic[OrmModelT, SchemaModelT]):
    """Reusable CRUD operations for SQLAlchemy repositories."""

    orm_model: Type[OrmModelT]
    schema_model: Type[SchemaModelT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _to_schema(self, model: OrmModelT) -> SchemaModelT:
        return self.schema_model.model_validate(model)

    async def get_by_id(self, item_id: str) -> Optional[SchemaModelT]:
        try:
            model = await self.session.get(self.orm_model, item_id)
            if model is None:
                return None
            return self._to_schema(model)
        except Exception as exc:
            raise DatabaseError(detail=f"Failed to load record: {exc}") from exc

    async def get_by_id_or_raise(self, item_id: str) -> SchemaModelT:
        item = await self.get_by_id(item_id)
        if item is None:
            raise NotFoundError(detail=f"{self.orm_model.__name__} with ID {item_id} not found")
        return item

    async def get_all(self, limit: int = 100) -> List[SchemaModelT]:
        try:
            result = await self.session.execute(select(self.orm_model).limit(limit))
            return [self._to_schema(item) for item in result.scalars().all()]
        except Exception as exc:
            raise DatabaseError(detail=f"Failed to list records: {exc}") from exc

    async def exists(self, item_id: str) -> bool:
        return await self.get_by_id(item_id) is not None

    async def delete(self, item_id: str) -> None:
        try:
            model = await self.session.get(self.orm_model, item_id)
            if model is None:
                raise NotFoundError(detail=f"{self.orm_model.__name__} with ID {item_id} not found")
            await self.session.delete(model)
            await self.session.commit()
        except NotFoundError:
            raise
        except Exception as exc:
            await self.session.rollback()
            raise DatabaseError(detail=f"Failed to delete record: {exc}") from exc

    async def create(self, data: Dict[str, Any]) -> SchemaModelT:
        raise NotImplementedError

    async def update(self, item_id: str, data: Dict[str, Any]) -> SchemaModelT:
        raise NotImplementedError
