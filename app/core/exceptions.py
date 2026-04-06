"""Custom exceptions and exception handlers for the API."""

import logging
from typing import Any, Dict, Optional

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class APIException(Exception):
    """Base exception for API-facing failures."""

    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: str = "An unexpected error occurred",
        error_code: str = "INTERNAL_ERROR",
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        self.status_code = status_code
        self.detail = detail
        self.error_code = error_code
        self.headers = headers
        super().__init__(detail)


class NotFoundError(APIException):
    """Raised when a resource cannot be found."""

    def __init__(self, detail: str = "Resource not found") -> None:
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail, error_code="NOT_FOUND")


class ValidationError(APIException):
    """Raised when domain validation fails."""

    def __init__(self, detail: str = "Validation error") -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code="VALIDATION_ERROR",
        )


class UnauthorizedError(APIException):
    """Raised when authentication fails."""

    def __init__(self, detail: str = "Unauthorized") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="UNAUTHORIZED",
            headers={"WWW-Authenticate": "Bearer"},
        )


class ConflictError(APIException):
    """Raised when a write conflicts with existing state."""

    def __init__(self, detail: str = "Resource conflict") -> None:
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail, error_code="CONFLICT")


class DatabaseError(APIException):
    """Raised when persistence operations fail."""

    def __init__(self, detail: str = "Database operation failed") -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="DATABASE_ERROR",
        )


class ExternalServiceError(APIException):
    """Raised when Redis or another external dependency is unavailable."""

    def __init__(self, detail: str = "External service unavailable") -> None:
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=detail,
            error_code="EXTERNAL_SERVICE_ERROR",
        )


def create_error_response(status_code: int, detail: str, error_code: str, path: str) -> Dict[str, Any]:
    """Create the standard error payload."""
    return {
        "success": False,
        "error": {
            "status_code": status_code,
            "code": error_code,
            "message": detail,
            "path": path,
        },
    }


async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """Translate APIException instances to JSON responses."""
    log_fn = logger.error if exc.status_code >= 500 else logger.warning
    log_fn("API exception [%s] %s", exc.status_code, exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(exc.status_code, exc.detail, exc.error_code, str(request.url.path)),
        headers=exc.headers,
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Translate unexpected exceptions to safe JSON responses."""
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=create_error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "An unexpected error occurred",
            "INTERNAL_ERROR",
            str(request.url.path),
        ),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register application exception handlers."""
    app.add_exception_handler(APIException, api_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
