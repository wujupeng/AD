import logging
from datetime import datetime, timezone
from typing import Any

from app.interfaces.i_monitoring_provider import IMonitoringProvider
from app.interfaces.i_veeam_provider import IVeeamProvider
from app.interfaces.i_cache_provider import ICacheProvider
from app.interfaces.i_audit_provider import IAuditProvider
from app.repositories.alert_repository import AlertRepository

logger = logging.getLogger(__name__)


class MonitoringAlertService:
    def __init__(
        self,
        monitoring_provider: IMonitoringProvider,
        veeam_provider: IVeeamProvider,
        cache_provider: ICacheProvider,
        audit_provider: IAuditProvider,
        alert_repo: AlertRepository,
    ):
        self._monitoring = monitoring_provider
        self._veeam = veeam_provider
        self._cache = cache_provider
        self._audit = audit_provider
        self._alert_repo = alert_repo

    async def list_alerts(self, severity: str | None = None, category: str | None = None, acknowledged: bool | None = None) -> list[dict[str, Any]]:
        alerts = await self._alert_repo.list_alerts(severity, category, acknowledged)
        return [{"alert_id": a.alert_id, "source_system": a.source_system, "severity": a.severity, "category": a.category, "title": a.title, "description": a.description, "trigger_time": str(a.trigger_time), "acknowledged": a.acknowledged, "resolved": a.resolved} for a in alerts]

    async def acknowledge_alert(self, alert_id: str) -> bool:
        return await self._alert_repo.acknowledge_alert(alert_id)

    async def get_grafana_dashboards(self) -> list[dict[str, Any]]:
        return await self._monitoring.query_grafana_dashboards()

    async def get_backup_status(self) -> list[dict[str, Any]]:
        jobs = await self._alert_repo.list_backup_jobs()
        return [{"job_name": j.job_name, "backup_type": j.backup_type, "last_execution_time": str(j.last_execution_time) if j.last_execution_time else None, "last_execution_status": j.last_execution_status, "retention_policy": j.retention_policy} for j in jobs]

    async def get_alert_notification_configs(self) -> list[dict[str, Any]]:
        configs = await self._alert_repo.list_notification_configs()
        return [{"id": c.id, "severity": c.severity, "category": c.category, "recipient_groups": c.recipient_groups, "channels": c.channels, "is_enabled": c.is_enabled} for c in configs]