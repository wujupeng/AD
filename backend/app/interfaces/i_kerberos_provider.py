from abc import ABC, abstractmethod
from typing import Any


class IKerberosProvider(ABC):
    @abstractmethod
    async def validate_ticket(self, ticket: bytes, service_principal: str) -> dict[str, Any]:
        ...

    @abstractmethod
    async def extract_principal(self, ticket: bytes) -> str:
        ...