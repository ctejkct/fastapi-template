"""Authentication endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.deps import CurrentUserIdDep, DbSession, get_user_cache_repository
from app.interfaces.authentication import IAuthenticationService
from app.repositories.user_repository import UserRepository
from app.schemas.authentication import AuthResponse, LoginRequest, RegistrationRequest
from app.services.authentication import AuthenticationService

router = APIRouter(prefix="/authentication", tags=["Authentication"])


def get_auth_service(session: DbSession) -> IAuthenticationService:
    """Wire the authentication service graph."""
    user_repo = UserRepository(session)
    cache_repo = get_user_cache_repository()
    return AuthenticationService(user_repo, user_repo, cache_repo)


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    request: RegistrationRequest,
    auth_service: Annotated[IAuthenticationService, Depends(get_auth_service)],
) -> AuthResponse:
    """Register a user and issue an access token."""
    return await auth_service.register(request)


@router.post("/login", response_model=AuthResponse, status_code=status.HTTP_200_OK)
async def login_user(
    request: LoginRequest,
    auth_service: Annotated[IAuthenticationService, Depends(get_auth_service)],
) -> AuthResponse:
    """Authenticate a user and issue an access token."""
    return await auth_service.login(request)


@router.get("/me", status_code=status.HTTP_200_OK)
async def get_me(
    current_user_id: CurrentUserIdDep,
    auth_service: Annotated[IAuthenticationService, Depends(get_auth_service)],
):
    """Return the authenticated user."""
    return await auth_service.get_me(current_user_id)
