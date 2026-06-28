import logging
from typing import Any

import httpx

from app.interfaces.i_secure_print_provider import ISecurePrintProvider, ICardMappingProvider, IPrintAuditProvider

logger = logging.getLogger(__name__)


class SecurePrintAdapter(ISecurePrintProvider):
    def __init__(self):
        self._cluster_url: str | None = None

    async def submit_job(self, job_data: dict[str, Any]) -> dict[str, Any]:
        if not self._cluster_url:
            return {"status": "not_configured", "message": "Print Cluster URL not configured"}
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(f"{self._cluster_url}/api/jobs", json=job_data)
                if resp.status_code == 200:
                    return resp.json()
        except Exception as e:
            logger.warning("Print Cluster submit failed: %s", e)
        return {"status": "error", "message": "Failed to submit job to Print Cluster"}

    async def release_job(self, job_id: str, printer_name: str) -> dict[str, Any]:
        if not self._cluster_url:
            return {"status": "not_configured"}
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(f"{self._cluster_url}/api/jobs/{job_id}/release", json={"printer_name": printer_name})
                if resp.status_code == 200:
                    return resp.json()
        except Exception as e:
            logger.warning("Print Cluster release failed: %s", e)
        return {"status": "error", "message": "Failed to release job"}

    async def cancel_job(self, job_id: str) -> dict[str, Any]:
        if not self._cluster_url:
            return {"status": "not_configured"}
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.delete(f"{self._cluster_url}/api/jobs/{job_id}")
                if resp.status_code == 200:
                    return resp.json()
        except Exception as e:
            logger.warning("Print Cluster cancel failed: %s", e)
        return {"status": "error"}

    async def query_cluster_status(self) -> dict[str, Any]:
        if not self._cluster_url:
            return {"status": "not_configured"}
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{self._cluster_url}/api/status")
                if resp.status_code == 200:
                    return resp.json()
        except Exception as e:
            logger.warning("Print Cluster status query failed: %s", e)
        return {"status": "unreachable"}


class CardMappingAdapter(ICardMappingProvider):
    def __init__(self):
        pass

    async def resolve_card(self, card_id: str) -> dict[str, Any]:
        return {"card_id": card_id, "status": "not_found", "message": "Card mapping requires database lookup via CardMappingRepository"}


class PrintAuditAdapter(IPrintAuditProvider):
    def __init__(self):
        pass

    async def record_operation(self, operation_data: dict[str, Any]) -> str:
        return "audit_not_implemented"

    async def query_statistics(self, filters: dict[str, Any]) -> dict[str, Any]:
        return {"total": 0, "items": []}