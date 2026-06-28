from typing import Any
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.remote_access import VpnPolicy


class VpnPolicyRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_all(self) -> list[VpnPolicy]:
        result = await self._session.execute(select(VpnPolicy).order_by(VpnPolicy.policy_type))
        return list(result.scalars().all())

    async def get_by_type(self, policy_type: str) -> list[VpnPolicy]:
        result = await self._session.execute(select(VpnPolicy).where(VpnPolicy.policy_type == policy_type))
        return list(result.scalars().all())

    async def get_enabled(self) -> list[VpnPolicy]:
        result = await self._session.execute(select(VpnPolicy).where(VpnPolicy.is_enabled == True))
        return list(result.scalars().all())

    async def get_by_name(self, policy_name: str) -> VpnPolicy | None:
        result = await self._session.execute(select(VpnPolicy).where(VpnPolicy.policy_name == policy_name))
        return result.scalar_one_or_none()

    async def update_config(self, policy_id: str, config: dict[str, Any]) -> None:
        await self._session.execute(update(VpnPolicy).where(VpnPolicy.policy_id == policy_id).values(policy_config=config))
        await self._session.commit()

    async def update_enabled(self, policy_id: str, is_enabled: bool) -> None:
        await self._session.execute(update(VpnPolicy).where(VpnPolicy.policy_id == policy_id).values(is_enabled=is_enabled))
        await self._session.commit()