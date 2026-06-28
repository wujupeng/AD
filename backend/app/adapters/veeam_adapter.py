import logging
from typing import Any

import httpx

from app.interfaces.i_veeam_provider import IVeeamProvider

logger = logging.getLogger(__name__)


class VeeamAdapter(IVeeamProvider):
    def __init__(self):
        self._base_url: str | None = None
        self._api_key: str | None = None

    async def query_backup_status(self) -> list[dict[str, Any]]:
        if not self._base_url:
            return []
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(f"{self._base_url}/api/v1/jobs", headers={"X-API-Key": self._api_key or ""})
                if resp.status_code == 200:
                    return resp.json().get("data", [])
        except Exception as e:
            logger.warning("Veeam API query failed: %s", e)
        return []

    async def query_recovery_points(self, job_name: str) -> list[dict[str, Any]]:
        if not self._base_url:
            return []
        return []