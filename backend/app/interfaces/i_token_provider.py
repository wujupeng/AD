from abc import ABC, abstractmethod
from typing import Any


class ITokenProvider(ABC):
    @abstractmethod
    async def issue_token(self, payload: dict[str, Any], expires_delta: int | None = None) -> str:
        ...

    @abstractmethod
    async def validate_token(self, token: str) -> dict[str, Any]:
        ...

    @abstractmethod
    async def validate_refresh_token(self, refresh_token: str) -> dict[str, Any]:
        ...

    @abstractmethod
    async def issue_refresh_token(self, payload: dict[str, Any]) -> str:
        ...

    @abstractmethod
    async def revoke_token(self, token_id: str) -> bool:
        ...