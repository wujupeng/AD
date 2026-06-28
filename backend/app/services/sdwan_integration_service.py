import logging
from typing import Any

from app.interfaces.i_sdwan_provider import ISdwanProvider
from app.interfaces.i_cache_provider import ICacheProvider
from app.interfaces.i_audit_provider import IAuditProvider
from app.repositories.sdwan_repository import SdwanRepository

logger = logging.getLogger(__name__)


class SdwanIntegrationService:
    def __init__(
        self,
        sdwan_provider: ISdwanProvider,
        cache_provider: ICacheProvider,
        audit_provider: IAuditProvider,
        sdwan_repo: SdwanRepository,
    ):
        self._sdwan = sdwan_provider
        self._cache = cache_provider
        self._audit = audit_provider
        self._sdwan_repo = sdwan_repo

    async def list_links(self) -> list[dict[str, Any]]:
        links = await self._sdwan_repo.list_links()
        return [{"link_id": l.link_id, "source_site": l.source_site, "target_site": l.target_site, "bandwidth_mbps": l.bandwidth_mbps, "latency_ms": l.latency_ms, "packet_loss_percent": l.packet_loss_percent, "link_status": l.link_status} for l in links]

    async def get_qos_policies(self) -> list[dict[str, Any]]:
        return await self._sdwan.query_qos_policies()

    async def get_impact_analysis(self) -> dict[str, Any]:
        links = await self._sdwan_repo.list_links()
        impacted_services = []
        for link in links:
            if link.link_status == "down":
                impacted_services.append({"link": f"{link.source_site} -> {link.target_site}", "affected_services": ["AD Replication", "DFS-R", "Cross-site Print"]})
            elif link.latency_ms and link.latency_ms > 200:
                impacted_services.append({"link": f"{link.source_site} -> {link.target_site}", "affected_services": ["DFS-R (slow sync)", "Cross-site Print (slow)"], "latency_ms": link.latency_ms})
            elif link.packet_loss_percent and link.packet_loss_percent > 5:
                impacted_services.append({"link": f"{link.source_site} -> {link.target_site}", "affected_services": ["AD Replication (unstable)"], "packet_loss_percent": link.packet_loss_percent})
        return {"total_links": len(links), "impacted_services": impacted_services}