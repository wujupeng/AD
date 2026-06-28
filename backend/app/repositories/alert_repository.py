from typing import Any
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.monitoring_alert import MonitoringAlert, BackupJob, AlertNotificationConfig


class AlertRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def list_alerts(self, severity: str | None = None, category: str | None = None, acknowledged: bool | None = None) -> list[MonitoringAlert]:
        query = select(MonitoringAlert).order_by(MonitoringAlert.trigger_time.desc())
        if severity:
            query = query.where(MonitoringAlert.severity == severity)
        if category:
            query = query.where(MonitoringAlert.category == category)
        if acknowledged is not None:
            query = query.where(MonitoringAlert.acknowledged == acknowledged)
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def get_alert(self, alert_id: str) -> MonitoringAlert | None:
        return await self._session.get(MonitoringAlert, alert_id)

    async def create_alert(self, data: dict[str, Any]) -> MonitoringAlert:
        alert = MonitoringAlert(**data)
        self._session.add(alert)
        await self._session.flush()
        return alert

    async def acknowledge_alert(self, alert_id: str) -> bool:
        result = await self._session.execute(update(MonitoringAlert).where(MonitoringAlert.alert_id == alert_id).values(acknowledged=True))
        return result.rowcount > 0

    async def resolve_alert(self, alert_id: str) -> bool:
        result = await self._session.execute(update(MonitoringAlert).where(MonitoringAlert.alert_id == alert_id).values(resolved=True, acknowledged=True))
        return result.rowcount > 0

    async def list_backup_jobs(self) -> list[BackupJob]:
        result = await self._session.execute(select(BackupJob))
        return list(result.scalars().all())

    async def upsert_backup_job(self, backup_job_id: str, data: dict[str, Any]) -> BackupJob:
        existing = await self._session.get(BackupJob, backup_job_id)
        if existing:
            for key, value in data.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            await self._session.flush()
            return existing
        job = BackupJob(backup_job_id=backup_job_id, **data)
        self._session.add(job)
        await self._session.flush()
        return job

    async def list_notification_configs(self) -> list[AlertNotificationConfig]:
        result = await self._session.execute(select(AlertNotificationConfig).where(AlertNotificationConfig.is_enabled == True))
        return list(result.scalars().all())

    async def upsert_notification_config(self, config_id: str, data: dict[str, Any]) -> AlertNotificationConfig:
        existing = await self._session.get(AlertNotificationConfig, config_id)
        if existing:
            for key, value in data.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            await self._session.flush()
            return existing
        config = AlertNotificationConfig(id=config_id, **data)
        self._session.add(config)
        await self._session.flush()
        return config