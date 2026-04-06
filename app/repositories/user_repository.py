"""PostgreSQL-backed user repository."""

from typing import Any, Dict, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, DatabaseError, NotFoundError
from app.db.models import UserORM
from app.interfaces.repositories.authentication import IAuthenticationRepository
from app.interfaces.repositories.users import IUserRepository
from app.repositories.base import BaseRepository
from app.schemas.users import UserResponse


class UserRepository(BaseRepository[UserORM, UserResponse], IUserRepository, IAuthenticationRepository):
    """User repository using SQLAlchemy async sessions."""

    orm_model = UserORM
    schema_model = UserResponse

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_email(self, email: str) -> Optional[UserResponse]:
        try:
            result = await self.session.execute(select(UserORM).where(UserORM.email == email))
            user = result.scalar_one_or_none()
            if user is None:
                return None
            return self._to_schema(user)
        except Exception as exc:
            raise DatabaseError(detail=f"Failed to load user by email: {exc}") from exc

    async def get_hashed_password(self, user_id: str) -> Optional[str]:
        try:
            user = await self.session.get(UserORM, user_id)
            if user is None:
                return None
            return user.hashed_password
        except Exception as exc:
            raise DatabaseError(detail=f"Failed to load password hash: {exc}") from exc

    async def create_credentials_user(
        self, email: str, full_name: str, hashed_password: str
    ) -> UserResponse:
        return await self.create(
            {"email": email, "full_name": full_name, "hashed_password": hashed_password}
        )

    async def create(self, data: Dict[str, Any]) -> UserResponse:
        existing = await self.get_by_email(data["email"])
        if existing is not None:
            raise ConflictError(detail="User with this email already exists")

        try:
            user = UserORM(
                email=data["email"],
                full_name=data["full_name"],
                hashed_password=data["hashed_password"],
                is_active=data.get("is_active", True),
            )
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            return self._to_schema(user)
        except ConflictError:
            raise
        except Exception as exc:
            await self.session.rollback()
            raise DatabaseError(detail=f"Failed to create user: {exc}") from exc

    async def update(self, item_id: str, data: Dict[str, Any]) -> UserResponse:
        try:
            user = await self.session.get(UserORM, item_id)
            if user is None:
                raise NotFoundError(detail=f"User with ID {item_id} not found")

            for field in ("full_name", "is_active"):
                if field in data and data[field] is not None:
                    setattr(user, field, data[field])

            await self.session.commit()
            await self.session.refresh(user)
            return self._to_schema(user)
        except NotFoundError:
            raise
        except Exception as exc:
            await self.session.rollback()
            raise DatabaseError(detail=f"Failed to update user: {exc}") from exc
