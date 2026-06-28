import logging
import asyncio
from datetime import datetime, timezone
from typing import Any

from app.interfaces.i_dc_management_provider import IDcManagementProvider
from app.interfaces.i_cache_provider import ICacheProvider
from app.interfaces.i_audit_provider import IAuditProvider
from app.repositories.dc_repository import DcRepository

logger = logging.getLogger(__name__)


class DcManagementService:
    def __init__(
        self,
        dc_provider: IDcManagementProvider,
        cache_provider: ICacheProvider,
        audit_provider: IAuditProvider,
        dc_repo: DcRepository,
    ):
        self._dc_provider = dc_provider
        self._cache = cache_provider
        self._audit = audit_provider
        self._dc_repo = dc_repo

    async def list_dcs(self) -> list[dict[str, Any]]:
        dcs = await self._dc_repo.list_all()
        return [{"dc_hostname": dc.dc_hostname, "dc_site": dc.dc_site, "dc_ip_address": dc.dc_ip_address, "is_gc": dc.is_gc, "health_status": dc.health_status, "fsmo_roles": dc.fsmo_roles or [], "os_version": dc.os_version} for dc in dcs]

    async def get_dc(self, dc_hostname: str) -> dict[str, Any] | None:
        dc = await self._dc_repo.get_by_hostname(dc_hostname)
        if not dc:
            return None
        return {"dc_hostname": dc.dc_hostname, "dc_site": dc.dc_site, "dc_ip_address": dc.dc_ip_address, "is_gc": dc.is_gc, "is_dns_integrated": dc.is_dns_integrated, "fsmo_roles": dc.fsmo_roles or [], "health_status": dc.health_status, "os_version": dc.os_version, "config_baseline": dc.config_baseline, "last_health_check": str(dc.last_health_check) if dc.last_health_check else None}

    async def check_dc_health(self, dc_hostname: str) -> dict[str, Any]:
        result = await self._dc_provider.query_dc_health(dc_hostname)
        now = datetime.now(timezone.utc)
        status = result.get("status", "unknown")
        await self._dc_repo.update_health(dc_hostname, status, now)
        await self._cache.set_hash(f"dc_health:{dc_hostname}", "status", status)
        if "ldap_response_ms" in result:
            await self._cache.set_hash(f"dc_health:{dc_hostname}", "ldap_ms", str(result["ldap_response_ms"]))
        return result

    async def check_all_dc_health(self) -> list[dict[str, Any]]:
        dcs = await self._dc_repo.list_all()
        results = await asyncio.gather(*[self.check_dc_health(dc.dc_hostname) for dc in dcs], return_exceptions=True)
        return [r if isinstance(r, dict) else {"dc_hostname": dcs[i].dc_hostname, "status": "error", "error": str(r)} for i, r in enumerate(results)]

    async def get_replication_topology(self) -> list[dict[str, Any]]:
        links = await self._dc_repo.list_replication_links()
        return [{"link_id": l.link_id, "source_dc": l.source_dc, "target_dc": l.target_dc, "source_site": l.source_site, "target_site": l.target_site, "replication_delay_seconds": l.replication_delay_seconds, "consecutive_failures": l.consecutive_failures, "link_status": l.link_status} for l in links]

    async def get_fsmo_roles(self) -> dict[str, Any]:
        dcs = await self._dc_repo.list_all()
        roles = {}
        for dc in dcs:
            for role in (dc.fsmo_roles or []):
                roles[role] = dc.dc_hostname
        return roles

    async def transfer_fsmo_role(self, role: str, target_dc: str) -> dict[str, Any]:
        result = await self._dc_provider.transfer_fsmo_role(role, target_dc)
        await self._audit.log_event({"event_type": "dc_management", "action": "fsmo_transfer", "resource": f"FSMO:{role}", "details": f"Transfer {role} to {target_dc}", "result": "success" if result.get("status") != "error" else "failure", "occurred_at": datetime.now(timezone.utc)})
        return result

    async def get_config_baseline(self, dc_hostname: str) -> dict[str, Any]:
        dc = await self._dc_repo.get_by_hostname(dc_hostname)
        if not dc:
            return {"error": "DC not found"}
        return {"dc_hostname": dc_hostname, "config_baseline": dc.config_baseline or {}}

    async def check_config_drift(self, dc_hostname: str) -> dict[str, Any]:
        current = await self._dc_provider.query_dc_config(dc_hostname)
        dc = await self._dc_repo.get_by_hostname(dc_hostname)
        if not dc or not dc.config_baseline:
            return {"dc_hostname": dc_hostname, "drift_detected": False, "message": "No baseline configured"}
        drift = {}
        for key, baseline_value in dc.config_baseline.items():
            current_value = current.get(key)
            if current_value != baseline_value:
                drift[key] = {"baseline": baseline_value, "current": current_value}
        if drift:
            await self._audit.log_event({"event_type": "dc_management", "action": "config_drift", "resource": dc_hostname, "details": str(drift), "result": "warning", "occurred_at": datetime.now(timezone.utc)})
        return {"dc_hostname": dc_hostname, "drift_detected": len(drift) > 0, "drift": drift}