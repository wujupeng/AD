from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.settings import CachedLogonPolicy


class CachedLogonPolicyRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_policy(self) -> CachedLogonPolicy | None:
        result = await self._session.execute(select(CachedLogonPolicy).limit(1))
        return result.scalar_one_or_none()

    async def get_or_create_default(self) -> CachedLogonPolicy:
        policy = await self.get_policy()
        if policy:
            return policy
        policy = CachedLogonPolicy(
            policy_name="Cached-Logon-Count-Policy",
            policy_config={"enterprise_laptop": 100, "enterprise_desktop": 10, "byod": 0, "kiosk": 0},
            is_enabled=True,
            version=1,
        )
        self._session.add(policy)
        await self._session.commit()
        return policy

    async def update_policy(self, policy_id: str, policy_config: dict | None = None, is_enabled: bool | None = None, version: int | None = None) -> CachedLogonPolicy:
        policy = await self._session.execute(select(CachedLogonPolicy).where(CachedLogonPolicy.policy_id == policy_id))
        p = policy.scalar_one_or_none()
        if not p:
            raise ValueError("Policy not found")
        if version is not None and p.version != version:
            raise ValueError(f"Version conflict: expected {p.version}, got {version}")
        if policy_config is not None:
            p.policy_config = policy_config
        if is_enabled is not None:
            p.is_enabled = is_enabled
        p.version = (p.version or 0) + 1
        await self._session.commit()
        return p