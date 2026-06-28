from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.settings import EntraHybridJoinConfig


class EntraHybridJoinRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_config(self) -> EntraHybridJoinConfig | None:
        result = await self._session.execute(select(EntraHybridJoinConfig).limit(1))
        return result.scalar_one_or_none()

    async def get_or_create_default(self) -> EntraHybridJoinConfig:
        config = await self.get_config()
        if config:
            return config
        config = EntraHybridJoinConfig(
            status="not_configured",
            total_devices=0,
            registered=0,
            pending=0,
            failed=0,
            message="Entra Hybrid Join requires Phase2+",
        )
        self._session.add(config)
        await self._session.commit()
        return config

    async def update_config(self, config_id: str, **kwargs: Any) -> EntraHybridJoinConfig:
        result = await self._session.execute(select(EntraHybridJoinConfig).where(EntraHybridJoinConfig.config_id == config_id))
        c = result.scalar_one_or_none()
        if not c:
            raise ValueError("Config not found")
        for k, v in kwargs.items():
            if hasattr(c, k):
                setattr(c, k, v)
        await self._session.commit()
        return c