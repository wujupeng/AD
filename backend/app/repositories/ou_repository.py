from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func

from app.models.ad_objects import AdOu


class OuRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_tree(self) -> list[AdOu]:
        result = await self._session.execute(
            select(AdOu).where(AdOu.is_deleted == False).order_by(AdOu.dn)
        )
        return list(result.scalars().all())

    async def get_by_dn(self, dn: str) -> AdOu | None:
        result = await self._session.execute(select(AdOu).where(AdOu.dn == dn, AdOu.is_deleted == False))
        return result.scalar_one_or_none()

    async def create_or_update(self, dn: str, data: dict[str, Any]) -> AdOu:
        existing = await self.get_by_dn(dn)
        if existing:
            for key, value in data.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            existing.synced_at = datetime.now(timezone.utc)
            await self._session.flush()
            return existing
        else:
            ou = AdOu(dn=dn, **data, synced_at=datetime.now(timezone.utc))
            self._session.add(ou)
            await self._session.flush()
            return ou

    async def soft_delete(self, dn: str) -> bool:
        result = await self._session.execute(
            update(AdOu).where(AdOu.dn == dn).values(is_deleted=True, synced_at=datetime.now(timezone.utc))
        )
        return result.rowcount > 0

    async def migrate_users_to_parent(self, ou_dn: str) -> int:
        from app.models.ad_objects import AdUser
        parent_dn = (await self.get_by_dn(ou_dn)).parent_dn if await self.get_by_dn(ou_dn) else None
        if not parent_dn:
            return 0
        result = await self._session.execute(
            update(AdUser).where(AdUser.ou_dn == ou_dn).values(ou_dn=parent_dn)
        )
        return result.rowcount