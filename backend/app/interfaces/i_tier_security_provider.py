from abc import ABC, abstractmethod
from typing import Any


class ITierSecurityProvider(ABC):
    @abstractmethod
    async def query_tier_overview(self) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def query_violations(self, hours: int = 24) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def query_laps_password(self, computer_name: str) -> dict[str, Any]:
        ...

    @abstractmethod
    async def query_bitlocker_key(self, computer_name: str) -> dict[str, Any]:
        ...

    @abstractmethod
    async def query_credential_guard_status(self, computer_name: str | None = None) -> dict[str, Any]:
        ...

    @abstractmethod
    async def query_applocker_wdac_status(self, computer_name: str | None = None) -> dict[str, Any]:
        ...

    @abstractmethod
    async def query_security_baseline(self, site: str | None = None) -> dict[str, Any]:
        ...