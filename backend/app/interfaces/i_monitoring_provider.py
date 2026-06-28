from abc import ABC, abstractmethod
from typing import Any


class IMonitoringProvider(ABC):
    @abstractmethod
    async def query_active_alerts(self, severity: str | None = None) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def acknowledge_alert(self, alert_id: str) -> dict[str, Any]:
        ...

    @abstractmethod
    async def query_grafana_dashboards(self) -> list[dict[str, Any]]:
        ...