from abc import ABC, abstractmethod
from typing import Any


class IMailProvider(ABC):
    @abstractmethod
    async def send_mail(self, from_address: str, to_addresses: list[str], subject: str, body: str, is_html: bool = False) -> bool:
        ...

    @abstractmethod
    async def search_contacts(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def get_freebusy(self, email: str, date_from: str, date_to: str) -> list[dict[str, Any]]:
        ...