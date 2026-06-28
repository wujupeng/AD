from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_

from app.models.ad_objects import AdUser


class UserRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_sid(self, sid: str) -> AdUser | None:
        result = await self._session.execute(select(AdUser).where(AdUser.sid == sid, AdUser.is_deleted == False))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> AdUser | None:
        result = await self._session.execute(select(AdUser).where(AdUser.username == username, AdUser.is_deleted == False))
        return result.scalar_one_or_none()

    async def list_users(
        self,
        ou_dn: str | None = None,
        site_code: str | None = None,
        department: str | None = None,
        is_enabled: bool | None = None,
        search: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[AdUser], int]:
        from sqlalchemy import func, or_

        query = select(AdUser).where(AdUser.is_deleted == False)
        count_query = select(func.count(AdUser.id)).where(AdUser.is_deleted == False)

        if ou_dn:
            query = query.where(AdUser.ou_dn == ou_dn)
            count_query = count_query.where(AdUser.ou_dn == ou_dn)
        if site_code:
            query = query.where(AdUser.site_code == site_code)
            count_query = count_query.where(AdUser.site_code == site_code)
        if department:
            query = query.where(AdUser.department == department)
            count_query = count_query.where(AdUser.department == department)
        if is_enabled is not None:
            query = query.where(AdUser.is_enabled == is_enabled)
            count_query = count_query.where(AdUser.is_enabled == is_enabled)
        if search:
            pattern = f"%{search}%"
            search_cond = or_(
                AdUser.username.ilike(pattern),
                AdUser.display_name.ilike(pattern),
                AdUser.email.ilike(pattern),
                AdUser.department.ilike(pattern),
            )
            query = query.where(search_cond)
            count_query = count_query.where(search_cond)

        total_result = await self._session.execute(count_query)
        total = total_result.scalar() or 0

        query = query.order_by(AdUser.username).offset((page - 1) * page_size).limit(page_size)
        result = await self._session.execute(query)
        users = result.scalars().all()

        return list(users), total

    async def create_or_update(self, sid: str, data: dict[str, Any]) -> AdUser:
        existing = await self.get_by_sid(sid)
        if existing:
            for key, value in data.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            existing.synced_at = datetime.now(timezone.utc)
            await self._session.flush()
            return existing
        else:
            user = AdUser(sid=sid, **data, synced_at=datetime.now(timezone.utc))
            self._session.add(user)
            await self._session.flush()
            return user

    async def soft_delete(self, sid: str) -> bool:
        result = await self._session.execute(
            update(AdUser).where(AdUser.sid == sid).values(is_deleted=True, synced_at=datetime.now(timezone.utc))
        )
        return result.rowcount > 0