from abc import ABC, abstractmethod
from typing import Any


class ISecurePrintProvider(ABC):
    @abstractmethod
    async def submit_job(self, job_data: dict[str, Any]) -> dict[str, Any]:
        ...

    @abstractmethod
    async def release_job(self, job_id: str, printer_name: str) -> dict[str, Any]:
        ...

    @abstractmethod
    async def cancel_job(self, job_id: str) -> dict[str, Any]:
        ...

    @abstractmethod
    async def query_cluster_status(self) -> dict[str, Any]:
        ...


class ICardMappingProvider(ABC):
    @abstractmethod
    async def resolve_card(self, card_id: str) -> dict[str, Any]:
        ...


class IPrintAuditProvider(ABC):
    @abstractmethod
    async def record_operation(self, operation_data: dict[str, Any]) -> str:
        ...

    @abstractmethod
    async def query_statistics(self, filters: dict[str, Any]) -> dict[str, Any]:
        ...