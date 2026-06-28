from abc import ABC, abstractmethod
from typing import Any


class IOidcProvider(ABC):
    @abstractmethod
    async def authorize(self, client_id: str, redirect_uri: str, scope: str, state: str) -> str:
        ...

    @abstractmethod
    async def exchange_code(self, code: str, client_id: str, client_secret: str, redirect_uri: str) -> dict[str, Any]:
        ...

    @abstractmethod
    async def get_userinfo(self, access_token: str) -> dict[str, Any]:
        ...

    @abstractmethod
    async def generate_discovery(self, base_url: str) -> dict[str, Any]:
        ...

    @abstractmethod
    async def get_jwks(self) -> dict[str, Any]:
        ...