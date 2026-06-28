from abc import ABC, abstractmethod
from typing import Any


class IPrintProvider(ABC):
    @abstractmethod
    async def list_printers(self, site_code: str | None = None) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def submit_task(self, printer_name: str, document_path: str, options: dict[str, Any] | None = None) -> str:
        ...

    @abstractmethod
    async def get_task_status(self, task_id: str) -> dict[str, Any]:
        ...

    @abstractmethod
    async def check_quota(self, user_sid: str, month: str) -> dict[str, Any]:
        ...