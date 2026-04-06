"""Common shared schemas."""

from datetime import datetime
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class BaseSchema(BaseModel):
    """Base schema config."""

    model_config = {"from_attributes": True, "populate_by_name": True}


class TimestampMixin(BaseSchema):
    """Shared timestamp fields."""

    created_at: Optional[datetime] = Field(None)
    updated_at: Optional[datetime] = Field(None)


class SuccessResponse(BaseSchema):
    """Standard success wrapper."""

    success: bool = Field(default=True)
    message: Optional[str] = Field(default=None)


class DataResponse(BaseSchema, Generic[T]):
    """Standard single-resource wrapper."""

    success: bool = Field(default=True)
    data: T


class ListResponse(BaseSchema, Generic[T]):
    """Standard collection wrapper."""

    success: bool = Field(default=True)
    data: List[T]
    total: int
    limit: int
    offset: int = 0


class HealthStatus(BaseSchema):
    """Health check payload."""

    status: str
    version: str
    environment: str
