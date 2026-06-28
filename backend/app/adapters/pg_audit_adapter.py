import hashlib
import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.interfaces.i_audit_provider import IAuditProvider
from app.models.audit import AuditEvent

logger = logging.getLogger(__name__)


class PgAuditAdapter(IAuditProvider):
    def __init__(self, session: AsyncSession):
        self._session = session

    def _compute_hash(self, event_data: str, previous_hash: str) -> str:
        combined = f"{previous_hash}{event_data}"
        return hashlib.sha256(combined.encode()).hexdigest()

    async def _get_last_hash(self) -> str:
        result = await self._session.execute(
            select(AuditEvent.event_hash).order_by(AuditEvent.id.desc()).limit(1)
        )
        row = result.scalar_one_or_none()
        return row or "0" * 64

    async def log_event(self, event: dict[str, Any]) -> str:
        previous_hash = await self._get_last_hash()
        event_data = json.dumps(event, sort_keys=True, default=str)
        event_hash = self._compute_hash(event_data, previous_hash)

        record = AuditEvent(
            event_hash=event_hash,
            previous_hash=previous_hash,
            event_type=event.get("event_type", ""),
            event_category=event.get("event_category"),
            user_sid=event.get("user_sid"),
            username=event.get("username"),
            site_code=event.get("site_code"),
            client_ip=event.get("client_ip"),
            resource=event.get("resource"),
            action=event.get("action"),
            result=event.get("result", "success"),
            details=event.get("details"),
            request_id=event.get("request_id"),
            occurred_at=event.get("occurred_at", datetime.now(timezone.utc)),
        )
        self._session.add(record)
        await self._session.flush()
        await self._session.commit()
        return str(record.id)

    async def query_logs(self, filters: dict[str, Any], page: int = 1, page_size: int = 50) -> dict[str, Any]:
        query = select(AuditEvent)
        count_query = select(func.count(AuditEvent.id))

        conditions = []
        if filters.get("event_type"):
            conditions.append(AuditEvent.event_type == filters["event_type"])
        if filters.get("user_sid"):
            conditions.append(AuditEvent.user_sid == filters["user_sid"])
        if filters.get("site_code"):
            conditions.append(AuditEvent.site_code == filters["site_code"])
        if filters.get("result"):
            conditions.append(AuditEvent.result == filters["result"])
        if filters.get("date_from"):
            conditions.append(AuditEvent.occurred_at >= filters["date_from"])
        if filters.get("date_to"):
            conditions.append(AuditEvent.occurred_at <= filters["date_to"])

        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))

        total_result = await self._session.execute(count_query)
        total = total_result.scalar() or 0

        query = query.order_by(AuditEvent.occurred_at.desc()).offset((page - 1) * page_size).limit(page_size)
        result = await self._session.execute(query)
        records = result.scalars().all()

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": [
                {
                    "id": r.id,
                    "event_type": r.event_type,
                    "user_sid": r.user_sid,
                    "username": r.username,
                    "site_code": r.site_code,
                    "resource": r.resource,
                    "action": r.action,
                    "result": r.result,
                    "occurred_at": r.occurred_at.isoformat() if r.occurred_at else None,
                }
                for r in records
            ],
        }

    async def check_integrity(self, date_from: str | None = None, date_to: str | None = None) -> dict[str, Any]:
        query = select(AuditEvent).order_by(AuditEvent.id.asc())
        if date_from:
            query = query.where(AuditEvent.occurred_at >= date_from)
        if date_to:
            query = query.where(AuditEvent.occurred_at <= date_to)

        result = await self._session.execute(query)
        records = result.scalars().all()

        broken_chains = []
        for i in range(1, len(records)):
            expected_previous = records[i - 1].event_hash
            if records[i].previous_hash != expected_previous:
                broken_chains.append({
                    "record_id": records[i].id,
                    "expected_previous_hash": expected_previous,
                    "actual_previous_hash": records[i].previous_hash,
                })

        return {
            "total_records": len(records),
            "broken_chains": len(broken_chains),
            "details": broken_chains[:10],
            "is_valid": len(broken_chains) == 0,
        }

    async def generate_report(self, report_type: str, date_from: str, date_to: str) -> str:
        import uuid
        return str(uuid.uuid4())


import json