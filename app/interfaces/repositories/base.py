"""Base repository interface."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, TypeVar

T = TypeVar("T")


class IRepository(ABC, Generic[T]):
    """Generic repository contract used by services."""

    @abstractmethod
    async def get_by_id(self, item_id: str) -> Optional[T]:
        """Get a record by id."""

    @abstractmethod
    async def get_all(self, limit: int = 100) -> List[T]:
        """Get all records up to a limit."""

    @abstractmethod
    async def create(self, data: Dict[str, Any]) -> T:
        """Create a record."""

    @abstractmethod
    async def update(self, item_id: str, data: Dict[str, Any]) -> T:
        """Update a record."""

    @abstractmethod
    async def delete(self, item_id: str) -> None:
        """Delete a record."""

    @abstractmethod
    async def exists(self, item_id: str) -> bool:
        """Check whether a record exists."""
