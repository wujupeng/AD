from abc import ABC, abstractmethod
from typing import Any


class IEntraIdProvider(ABC):
    @abstractmethod
    async def authenticate(self, username: str, password: str) -> dict[str, Any]:
        ...

    @abstractmethod
    async def query_sync_status(self) -> dict[str, Any]:
        ...

    @abstractmethod
    async def query_conditional_access(self) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def query_exchange_migration(self) -> dict[str, Any]:
        ...

    @abstractmethod
    async def query_intune_compliance(self) -> dict[str, Any]:
        ...