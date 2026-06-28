import logging
from typing import Any

import httpx

from app.interfaces.i_sdwan_provider import ISdwanProvider

logger = logging.getLogger(__name__)


class SdwanAdapter(ISdwanProvider):
    def __init__(self):
        self._controller_url: str | None = None
        self._api_key: str | None = None

    async def query_link_status(self) -> list[dict[str, Any]]:
        if not self._controller_url:
            return []
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(f"{self._controller_url}/api/v1/links", headers={"Authorization": f"Bearer {self._api_key or ''}"})
                if resp.status_code == 200:
                    return resp.json().get("data", [])
        except Exception as e:
            logger.warning("SD-WAN API query failed: %s", e)
        return []

    async def query_qos_policies(self) -> list[dict[str, Any]]:
        if not self._controller_url:
            return []
        return []

    async def query_impact_analysis(self) -> dict[str, Any]:
        if not self._controller_url:
            return {"status": "not_configured"}
        return {"status": "ok", "impacted_services": []}