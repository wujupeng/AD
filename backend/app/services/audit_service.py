import logging
from datetime import datetime, timezone
from typing import Any

from app.interfaces.i_audit_provider import IAuditProvider

logger = logging.getLogger(__name__)

ENTERPRISE_EVENT_TYPES = [
    "tier_violation", "pki_operation", "dc_management",
    "dfs_replication", "secure_print_operation",
]


class AuditService:
    def __init__(self, audit_provider: IAuditProvider):
        self._audit = audit_provider

    async def log_event(self, event: dict[str, Any]) -> str:
        return await self._audit.log_event(event)

    async def query_logs(self, filters: dict[str, Any], page: int = 1, page_size: int = 50) -> dict[str, Any]:
        return await self._audit.query_logs(filters, page, page_size)

    async def check_integrity(self, date_from: str | None = None, date_to: str | None = None) -> dict[str, Any]:
        return await self._audit.check_integrity(date_from, date_to)

    async def generate_report(self, report_type: str, date_from: str, date_to: str) -> str:
        return await self._audit.generate_report(report_type, date_from, date_to)

    async def generate_tier_compliance_report(self, date_from: str, date_to: str) -> dict[str, Any]:
        filters = {"event_type": "tier_violation", "occurred_at_from": date_from, "occurred_at_to": date_to}
        result = await self._audit.query_logs(filters, page_size=1000)
        violations = result.get("items", [])
        return {"total_violations": len(violations), "violations": violations, "period": f"{date_from} to {date_to}"}

    async def generate_pki_audit_report(self, date_from: str, date_to: str) -> dict[str, Any]:
        filters = {"event_type": "pki_operation", "occurred_at_from": date_from, "occurred_at_to": date_to}
        result = await self._audit.query_logs(filters, page_size=1000)
        operations = result.get("items", [])
        return {"total_operations": len(operations), "operations": operations, "period": f"{date_from} to {date_to}"}

    async def generate_permission_matrix_report(self, date_from: str, date_to: str) -> dict[str, Any]:
        filters = {"event_category": "permission", "occurred_at_from": date_from, "occurred_at_to": date_to}
        result = await self._audit.query_logs(filters, page_size=1000)
        changes = result.get("items", [])
        return {"total_changes": len(changes), "changes": changes, "period": f"{date_from} to {date_to}"}