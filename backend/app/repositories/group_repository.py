from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func

from app.models.ad_objects import AdGroup, AdGroupMember


class GroupRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def list_groups(self, ou_dn: str | None = None, page: int = 1, page_size: int = 50) -> tuple[list[AdGroup], int]:
        query = select(AdGroup).where(AdGroup.is_deleted == False)
        count_query = select(func.count(AdGroup.id)).where(AdGroup.is_deleted == False)

        if ou_dn:
            query = query.where(AdGroup.ou_dn == ou_dn)
            count_query = count_query.where(AdGroup.ou_dn == ou_dn)

        total_result = await self._session.execute(count_query)
        total = total_result.scalar() or 0

        query = query.order_by(AdGroup.group_name).offset((page - 1) * page_size).limit(page_size)
        result = await self._session.execute(query)
        groups = result.scalars().all()

        return list(groups), total

    async def get_by_dn(self, dn: str) -> AdGroup | None:
        result = await self._session.execute(select(AdGroup).where(AdGroup.dn == dn, AdGroup.is_deleted == False))
        return result.scalar_one_or_none()

    async def get_members(self, group_dn: str) -> list[AdGroupMember]:
        result = await self._session.execute(
            select(AdGroupMember).where(AdGroupMember.group_dn == group_dn)
        )
        return list(result.scalars().all())

    async def add_member(self, group_dn: str, member_dn: str, member_sid: str | None = None, member_type: str = "user") -> AdGroupMember:
        member = AdGroupMember(
            group_dn=group_dn,
            member_dn=member_dn,
            member_sid=member_sid,
            member_type=member_type,
            synced_at=datetime.now(timezone.utc),
        )
        self._session.add(member)
        await self._session.flush()
        return member

    async def remove_member(self, group_dn: str, member_dn: str) -> bool:
        result = await self._session.execute(
            select(AdGroupMember).where(
                AdGroupMember.group_dn == group_dn,
                AdGroupMember.member_dn == member_dn,
            )
        )
        member = result.scalar_one_or_none()
        if member:
            await self._session.delete(member)
            await self._session.flush()
            return True
        return False

    async def create_or_update(self, dn: str, data: dict[str, Any]) -> AdGroup:
        existing = await self.get_by_dn(dn)
        if existing:
            for key, value in data.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            existing.synced_at = datetime.now(timezone.utc)
            await self._session.flush()
            return existing
        else:
            group = AdGroup(dn=dn, **data, synced_at=datetime.now(timezone.utc))
            self._session.add(group)
            await self._session.flush()
            return group

    async def soft_delete(self, dn: str) -> bool:
        result = await self._session.execute(
            update(AdGroup).where(AdGroup.dn == dn).values(is_deleted=True, synced_at=datetime.now(timezone.utc))
        )
        return result.rowcount > 0