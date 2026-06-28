from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.integration import IntegrationConfig, AttributeMapping, RoleMapping


class IntegrationConfigRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def list_sp_configs(self, sp_type: str | None = None) -> list[IntegrationConfig]:
        query = select(IntegrationConfig).where(IntegrationConfig.is_enabled == True)
        if sp_type:
            query = query.where(IntegrationConfig.sp_type == sp_type)
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def get_sp_config(self, sp_name: str) -> IntegrationConfig | None:
        result = await self._session.execute(select(IntegrationConfig).where(IntegrationConfig.sp_name == sp_name))
        return result.scalar_one_or_none()

    async def create_sp_config(self, data: dict[str, Any]) -> IntegrationConfig:
        config = IntegrationConfig(**data)
        self._session.add(config)
        await self._session.flush()
        return config

    async def update_sp_config(self, sp_name: str, data: dict[str, Any]) -> IntegrationConfig | None:
        config = await self.get_sp_config(sp_name)
        if config:
            for key, value in data.items():
                if hasattr(config, key):
                    setattr(config, key, value)
            await self._session.flush()
        return config

    async def delete_sp_config(self, sp_name: str) -> bool:
        config = await self.get_sp_config(sp_name)
        if config:
            config.is_enabled = False
            await self._session.flush()
            return True
        return False

    async def get_attribute_mappings(self, sp_name: str) -> list[AttributeMapping]:
        result = await self._session.execute(
            select(AttributeMapping).where(AttributeMapping.sp_name == sp_name)
        )
        return list(result.scalars().all())

    async def get_role_mappings(self, sp_name: str) -> list[RoleMapping]:
        result = await self._session.execute(
            select(RoleMapping).where(RoleMapping.sp_name == sp_name).order_by(RoleMapping.priority)
        )
        return list(result.scalars().all())