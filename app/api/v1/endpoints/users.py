"""User endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import DbSession, get_user_cache_repository
from app.interfaces.users import IUsersService
from app.repositories.user_repository import UserRepository
from app.schemas.common import DataResponse, ListResponse
from app.schemas.users import UserCreateRequest, UserResponse, UserUpdateRequest
from app.services.users import UsersService

router = APIRouter(prefix="/users", tags=["Users"])


def get_users_service(session: DbSession) -> IUsersService:
    """Wire the user service graph."""
    repo = UserRepository(session)
    cache_repo = get_user_cache_repository()
    return UsersService(repo, cache_repo)


@router.post("", response_model=DataResponse[UserResponse], status_code=status.HTTP_201_CREATED)
async def create_user(
    request: UserCreateRequest,
    service: Annotated[IUsersService, Depends(get_users_service)],
) -> DataResponse[UserResponse]:
    """Create a user."""
    return DataResponse(data=await service.create_user(request))


@router.get("/{user_id}", response_model=DataResponse[UserResponse], status_code=status.HTTP_200_OK)
async def get_user(
    user_id: str,
    service: Annotated[IUsersService, Depends(get_users_service)],
) -> DataResponse[UserResponse]:
    """Get a user by id."""
    return DataResponse(data=await service.get_user(user_id))


@router.get("", response_model=ListResponse[UserResponse], status_code=status.HTTP_200_OK)
async def list_users(
    service: Annotated[IUsersService, Depends(get_users_service)],
    limit: int = Query(default=100, ge=1, le=500),
) -> ListResponse[UserResponse]:
    """List users."""
    users = await service.list_users(limit=limit)
    return ListResponse(data=users, total=len(users), limit=limit)


@router.patch("/{user_id}", response_model=DataResponse[UserResponse], status_code=status.HTTP_200_OK)
async def update_user(
    user_id: str,
    request: UserUpdateRequest,
    service: Annotated[IUsersService, Depends(get_users_service)],
) -> DataResponse[UserResponse]:
    """Update a user."""
    return DataResponse(data=await service.update_user(user_id, request))
