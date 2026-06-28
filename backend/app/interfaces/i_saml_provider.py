from abc import ABC, abstractmethod
from typing import Any


class ISamlProvider(ABC):
    @abstractmethod
    async def sign_assertion(self, attributes: dict[str, Any], audience: str, recipient: str) -> str:
        ...

    @abstractmethod
    async def validate_authn_request(self, request_xml: str) -> dict[str, Any]:
        ...

    @abstractmethod
    async def generate_metadata(self) -> str:
        ...

    @abstractmethod
    async def parse_logout_request(self, request_xml: str) -> dict[str, Any]:
        ...