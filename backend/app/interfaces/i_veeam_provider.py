from abc import ABC, abstractmethod
from typing import Any


class IVeeamProvider(ABC):
    @abstractmethod
    async def query_backup_status(self) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def query_recovery_points(self, job_name: str) -> list[dict[str, Any]]:
        ...