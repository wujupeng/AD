from typing import Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.remote_access import RemoteAccessAuditLog
from datetime import datetime, timedelta


class RemoteAccessAuditRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, log_data: dict[str, Any]) -> RemoteAccessAuditLog:
        log = RemoteAccessAuditLog(**log_data)
        self._session.add(log)
        await self._session.commit()
        return log

    async def get_by_event_type(self, event_type: str, limit: int = 100) -> list[RemoteAccessAuditLog]:
        result = await self._session.execute(
            select(RemoteAccessAuditLog).where(RemoteAccessAuditLog.event_type == event_type).order_by(RemoteAccessAuditLog.event_time.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_user(self, user_account: str, limit: int = 100) -> list[RemoteAccessAuditLog]:
        result = await self._session.execute(
            select(RemoteAccessAuditLog).where(RemoteAccessAuditLog.user_account == user_account).order_by(RemoteAccessAuditLog.event_time.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_site(self, site: str, limit: int = 100) -> list[RemoteAccessAuditLog]:
        result = await self._session.execute(
            select(RemoteAccessAuditLog).where(RemoteAccessAuditLog.source_site == site).order_by(RemoteAccessAuditLog.event_time.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def get_recent(self, hours: int = 24, limit: int = 200) -> list[RemoteAccessAuditLog]:
        since = datetime.utcnow() - timedelta(hours=hours)
        result = await self._session.execute(
            select(RemoteAccessAuditLog).where(RemoteAccessAuditLog.event_time >= since).order_by(RemoteAccessAuditLog.event_time.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def get_stats_24h(self) -> dict[str, int]:
        since = datetime.utcnow() - timedelta(hours=24)
        result = await self._session.execute(
            select(RemoteAccessAuditLog.event_type, func.count(RemoteAccessAuditLog.log_id))
            .where(RemoteAccessAuditLog.event_time >= since)
            .group_by(RemoteAccessAuditLog.event_type)
        )
        return {row[0]: row[1] for row in result.all()}