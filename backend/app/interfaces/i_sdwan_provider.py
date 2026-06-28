from abc import ABC, abstractmethod
from typing import Any


class ISdwanProvider(ABC):
    @abstractmethod
    async def query_link_status(self) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def query_qos_policies(self) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def query_impact_analysis(self) -> dict[str, Any]:
        ...