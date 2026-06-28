from abc import ABC, abstractmethod
from typing import Any


class IDcManagementProvider(ABC):
    @abstractmethod
    async def query_dc_health(self, dc_hostname: str) -> dict[str, Any]:
        ...

    @abstractmethod
    async def query_replication_metadata(self, dc_hostname: str) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def transfer_fsmo_role(self, role: str, target_dc: str) -> dict[str, Any]:
        ...

    @abstractmethod
    async def query_dc_config(self, dc_hostname: str) -> dict[str, Any]:
        ...

    @abstractmethod
    async def query_gpo_links(self, ou_dn: str) -> list[dict[str, Any]]:
        ...