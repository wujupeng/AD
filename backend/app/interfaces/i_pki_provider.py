from abc import ABC, abstractmethod
from typing import Any


class IPkiProvider(ABC):
    @abstractmethod
    async def create_template(self, template_data: dict[str, Any]) -> dict[str, Any]:
        ...

    @abstractmethod
    async def issue_certificate(self, template_name: str, subject: str, requester_sid: str) -> dict[str, Any]:
        ...

    @abstractmethod
    async def revoke_certificate(self, serial_number: str, reason: str) -> dict[str, Any]:
        ...

    @abstractmethod
    async def renew_certificate(self, serial_number: str) -> dict[str, Any]:
        ...

    @abstractmethod
    async def query_expiring_certificates(self, days: int = 30) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def query_scep_policies(self) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def create_scep_policy(self, policy_data: dict[str, Any]) -> dict[str, Any]:
        ...

    @abstractmethod
    async def query_root_ca_status(self) -> dict[str, Any]:
        ...