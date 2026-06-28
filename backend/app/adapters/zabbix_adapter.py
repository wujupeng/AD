import logging
from typing import Any

from app.interfaces.i_monitoring_provider import IMonitoringProvider

logger = logging.getLogger(__name__)


class ZabbixAdapter(IMonitoringProvider):
    def __init__(self):
        self._api_url: str | None = None
        self._api_key: str | None = None

    async def query_active_alerts(self, severity: str | None = None) -> list[dict[str, Any]]:
        if not self._api_url:
            return []
        return []

    async def acknowledge_alert(self, alert_id: str) -> dict[str, Any]:
        return {"alert_id": alert_id, "status": "not_configured"}

    async def query_grafana_dashboards(self) -> list[dict[str, Any]]:
        return []