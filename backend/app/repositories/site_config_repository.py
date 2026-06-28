from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.site import SiteConfig


class SiteConfigRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def match_by_ip(self, client_ip: str) -> SiteConfig | None:
        sites = await self._session.execute(
            select(SiteConfig).where(SiteConfig.is_active == True)
        )
        for site in sites.scalars().all():
            for subnet_range in site.subnet_ranges.split(","):
                subnet = subnet_range.strip()
                if self._ip_in_subnet(client_ip, subnet):
                    return site
        return None

    async def get_by_code(self, site_code: str) -> SiteConfig | None:
        result = await self._session.execute(
            select(SiteConfig).where(SiteConfig.site_code == site_code, SiteConfig.is_active == True)
        )
        return result.scalar_one_or_none()

    async def list_sites(self) -> list[SiteConfig]:
        result = await self._session.execute(
            select(SiteConfig).where(SiteConfig.is_active == True).order_by(SiteConfig.site_code)
        )
        return list(result.scalars().all())

    async def get_dc_priority(self, site_code: str) -> list[str]:
        site = await self.get_by_code(site_code)
        if site:
            return site.dc_priority_list
        return []

    def _ip_in_subnet(self, ip: str, subnet: str) -> bool:
        import ipaddress
        try:
            return ipaddress.ip_address(ip) in ipaddress.ip_network(subnet, strict=False)
        except ValueError:
            return False