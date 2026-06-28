from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.dc_management import DcRegistry, DcReplicationLink


class DcRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def list_all(self) -> list[DcRegistry]:
        result = await self._session.execute(select(DcRegistry).order_by(DcRegistry.dc_site, DcRegistry.dc_hostname))
        return list(result.scalars().all())

    async def get_by_hostname(self, dc_hostname: str) -> DcRegistry | None:
        return await self._session.get(DcRegistry, dc_hostname)

    async def list_by_site(self, site: str) -> list[DcRegistry]:
        result = await self._session.execute(select(DcRegistry).where(DcRegistry.dc_site == site))
        return list(result.scalars().all())

    async def list_by_health(self, health_status: str) -> list[DcRegistry]:
        result = await self._session.execute(select(DcRegistry).where(DcRegistry.health_status == health_status))
        return list(result.scalars().all())

    async def create_or_update(self, dc_hostname: str, data: dict[str, Any]) -> DcRegistry:
        existing = await self.get_by_hostname(dc_hostname)
        if existing:
            for key, value in data.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            await self._session.flush()
            return existing
        dc = DcRegistry(dc_hostname=dc_hostname, **data)
        self._session.add(dc)
        await self._session.flush()
        return dc

    async def update_health(self, dc_hostname: str, health_status: str, last_health_check=None) -> bool:
        result = await self._session.execute(
            update(DcRegistry).where(DcRegistry.dc_hostname == dc_hostname).values(health_status=health_status, last_health_check=last_health_check)
        )
        return result.rowcount > 0

    async def list_replication_links(self) -> list[DcReplicationLink]:
        result = await self._session.execute(select(DcReplicationLink))
        return list(result.scalars().all())

    async def get_replication_link(self, link_id: str) -> DcReplicationLink | None:
        return await self._session.get(DcReplicationLink, link_id)

    async def upsert_replication_link(self, link_id: str, data: dict[str, Any]) -> DcReplicationLink:
        existing = await self.get_replication_link(link_id)
        if existing:
            for key, value in data.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            await self._session.flush()
            return existing
        link = DcReplicationLink(link_id=link_id, **data)
        self._session.add(link)
        await self._session.flush()
        return link