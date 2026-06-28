from abc import ABC, abstractmethod
from typing import Any


class IAuditProvider(ABC):
    @abstractmethod
    async def log_event(self, event: dict[str, Any]) -> str:
        ...

    @abstractmethod
    async def query_logs(self, filters: dict[str, Any], page: int = 1, page_size: int = 50) -> dict[str, Any]:
        ...

    @abstractmethod
    async def check_integrity(self, date_from: str | None = None, date_to: str | None = None) -> dict[str, Any]:
        ...

    @abstractmethod
    async def generate_report(self, report_type: str, date_from: str, date_to: str) -> str:
        ...