"""Authentication service implementation."""

import logging

from app.core.exceptions import UnauthorizedError
from app.core.security import create_access_token, hash_password, verify_password
from app.interfaces.authentication import IAuthenticationService
from app.interfaces.repositories.authentication import IAuthenticationRepository
from app.interfaces.repositories.users import IUserCacheRepository, IUserRepository
from app.schemas.authentication import AuthResponse, LoginRequest, RegistrationRequest
from app.schemas.users import UserResponse

logger = logging.getLogger(__name__)


class AuthenticationService(IAuthenticationService):
    """Credential-based authentication service."""

    def __init__(
        self,
        auth_repo: IAuthenticationRepository,
        user_repo: IUserRepository,
        cache_repo: IUserCacheRepository,
    ) -> None:
        self.auth_repo = auth_repo
        self.user_repo = user_repo
        self.cache_repo = cache_repo

    async def register(self, request: RegistrationRequest) -> AuthResponse:
        logger.info("Registering user %s", request.email)
        hashed_password = hash_password(request.password)
        user = await self.auth_repo.create_credentials_user(
            email=request.email,
            full_name=request.full_name,
            hashed_password=hashed_password,
        )
        await self.cache_repo.set_user(user)
        access_token = create_access_token(user.id, {"email": user.email})
        return AuthResponse(access_token=access_token, user=user)

    async def login(self, request: LoginRequest) -> AuthResponse:
        logger.info("Authenticating user %s", request.email)
        user = await self.user_repo.get_by_email(request.email)
        if user is None:
            raise UnauthorizedError(detail="Invalid email or password")

        hashed_password = await self.user_repo.get_hashed_password(user.id)
        if hashed_password is None or not verify_password(request.password, hashed_password):
            raise UnauthorizedError(detail="Invalid email or password")

        await self.cache_repo.set_user(user)
        access_token = create_access_token(user.id, {"email": user.email})
        return AuthResponse(access_token=access_token, user=user)

    async def get_me(self, user_id: str) -> UserResponse:
        cached_user = await self.cache_repo.get_user(user_id)
        if cached_user is not None:
            return cached_user

        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise UnauthorizedError(detail="Authenticated user was not found")

        await self.cache_repo.set_user(user)
        return user
