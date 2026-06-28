import logging
from typing import Any

from app.interfaces.i_cache_provider import ICacheProvider
from app.repositories.site_config_repository import SiteConfigRepository

logger = logging.getLogger(__name__)


class SiteAwarenessService:
    def __init__(
        self,
        cache_provider: ICacheProvider,
        site_repo: SiteConfigRepository,
    ):
        self._cache = cache_provider
        self._site_repo = site_repo

    async def resolve_site(self, client_ip: str) -> dict[str, Any]:
        site = await self._site_repo.match_by_ip(client_ip)
        if not site:
            site = await self._site_repo.get_by_code("shanghai_hq")
        if not site:
            return {"site_code": "unknown", "site_name": "Unknown", "timezone": "UTC", "language": "en"}
        return {
            "site_code": site.site_code,
            "site_name": site.site_name,
            "timezone": site.timezone,
            "language": site.language,
        }

    async def get_nearest_dc(self, site_code: str) -> str | None:
        dc_list = await self._site_repo.get_dc_priority(site_code)
        for dc in dc_list:
            health = await self._cache.get_dc_health(dc)
            if not health or health.get("status") != "down":
                return dc
        return dc_list[0] if dc_list else None

    async def get_dc_priorities(self, site_code: str) -> list[str]:
        return await self._site_repo.get_dc_priority(site_code)

    async def update_dc_priorities(self, site_code: str, dc_list: list[str]) -> bool:
        site = await self._site_repo.get_by_code(site_code)
        if not site:
            return False
        site.dc_priority_list = dc_list
        return True

    async def get_dc_health_status(self, dc_hostname: str) -> dict[str, Any] | None:
        return await self._cache.get_dc_health(dc_hostname)

    async def is_gc_degraded(self, site_code: str) -> bool:
        degraded = await self._cache.get(f"gc_degraded:{site_code}")
        return degraded == "true"

    async def get_timezone(self, site_code: str) -> str:
        site = await self._site_repo.get_by_code(site_code)
        return site.timezone if site else "UTC"

    async def get_language(self, site_code: str) -> str:
        site = await self._site_repo.get_by_code(site_code)
        return site.language if site else "en"