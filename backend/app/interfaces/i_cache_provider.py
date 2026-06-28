from abc import ABC, abstractmethod
from typing import Any


class ICacheProvider(ABC):
    @abstractmethod
    async def get(self, key: str) -> str | None:
        ...

    @abstractmethod
    async def set(self, key: str, value: str, ttl: int | None = None) -> bool:
        ...

    @abstractmethod
    async def delete(self, key: str) -> bool:
        ...

    @abstractmethod
    async def get_hash(self, name: str, key: str) -> str | None:
        ...

    @abstractmethod
    async def set_hash(self, name: str, key: str, value: str) -> bool:
        ...

    @abstractmethod
    async def publish(self, channel: str, message: str) -> int:
        ...

    @abstractmethod
    async def subscribe(self, channel: str, callback: Any) -> None:
        ...

    @abstractmethod
    async def mark_dc_down(self, dc_hostname: str, ttl: int = 300) -> bool:
        ...

    @abstractmethod
    async def get_dc_health(self, dc_hostname: str) -> dict[str, Any] | None:
        ...