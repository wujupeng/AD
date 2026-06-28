from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.sdwan_integration import SdwanLink


class SdwanRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def list_links(self) -> list[SdwanLink]:
        result = await self._session.execute(select(SdwanLink))
        return list(result.scalars().all())

    async def get_link(self, link_id: str) -> SdwanLink | None:
        return await self._session.get(SdwanLink, link_id)

    async def list_by_status(self, link_status: str) -> list[SdwanLink]:
        result = await self._session.execute(select(SdwanLink).where(SdwanLink.link_status == link_status))
        return list(result.scalars().all())

    async def upsert_link(self, link_id: str, data: dict[str, Any]) -> SdwanLink:
        existing = await self.get_link(link_id)
        if existing:
            for key, value in data.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            await self._session.flush()
            return existing
        link = SdwanLink(link_id=link_id, **data)
        self._session.add(link)
        await self._session.flush()
        return link