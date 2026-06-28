from abc import ABC, abstractmethod
from typing import Any


class IPermissionProvider(ABC):
    @abstractmethod
    async def check_permission(self, user_sid: str, resource: str, action: str) -> dict[str, Any]:
        ...

    @abstractmethod
    async def resolve_groups(self, user_sid: str) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def get_effective_permissions(self, user_sid: str) -> dict[str, Any]:
        ...

    @abstractmethod
    async def invalidate_cache(self, user_sid: str | None = None) -> int:
        ...