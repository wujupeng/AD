from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.audit import AuditEvent


class AuditRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def query_logs(
        self,
        date_from: Any | None = None,
        date_to: Any | None = None,
        user_sid: str | None = None,
        event_type: str | None = None,
        site_code: str | None = None,
        result: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[dict], int]:
        query = select(AuditEvent)
        count_query = select(func.count(AuditEvent.id))

        conditions = []
        if date_from:
            conditions.append(AuditEvent.occurred_at >= date_from)
        if date_to:
            conditions.append(AuditEvent.occurred_at <= date_to)
        if user_sid:
            conditions.append(AuditEvent.user_sid == user_sid)
        if event_type:
            conditions.append(AuditEvent.event_type == event_type)
        if site_code:
            conditions.append(AuditEvent.site_code == site_code)
        if result:
            conditions.append(AuditEvent.result == result)

        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))

        total_result = await self._session.execute(count_query)
        total = total_result.scalar() or 0

        query = query.order_by(AuditEvent.occurred_at.desc()).offset((page - 1) * page_size).limit(page_size)
        rows = await self._session.execute(query)
        records = rows.scalars().all()

        items = [
            {
                "id": r.id,
                "event_type": r.event_type,
                "event_category": r.event_category,
                "user_sid": r.user_sid,
                "username": r.username,
                "site_code": r.site_code,
                "client_ip": r.client_ip,
                "resource": r.resource,
                "action": r.action,
                "result": r.result,
                "details": r.details,
                "occurred_at": r.occurred_at.isoformat() if r.occurred_at else None,
            }
            for r in records
        ]

        return items, total