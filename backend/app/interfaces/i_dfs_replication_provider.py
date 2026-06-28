from abc import ABC, abstractmethod
from typing import Any


class IDfsReplicationProvider(ABC):
    @abstractmethod
    async def query_namespace_structure(self, namespace_path: str) -> dict[str, Any]:
        ...

    @abstractmethod
    async def query_replication_status(self, link_id: str | None = None) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def query_conflict_files(self, resolved: bool | None = None) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def query_cluster_status(self) -> dict[str, Any]:
        ...