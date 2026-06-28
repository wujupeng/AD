from typing import Any
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.settings import LdapDirectoryConfig


class LdapDirectoryConfigRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def list_configs(self) -> list[LdapDirectoryConfig]:
        result = await self._session.execute(select(LdapDirectoryConfig).order_by(LdapDirectoryConfig.config_name))
        return list(result.scalars().all())

    async def get_config(self, config_id: str) -> LdapDirectoryConfig | None:
        result = await self._session.execute(select(LdapDirectoryConfig).where(LdapDirectoryConfig.config_id == config_id))
        return result.scalar_one_or_none()

    async def get_by_name(self, config_name: str) -> LdapDirectoryConfig | None:
        result = await self._session.execute(select(LdapDirectoryConfig).where(LdapDirectoryConfig.config_name == config_name))
        return result.scalar_one_or_none()

    async def create_config(self, **kwargs: Any) -> LdapDirectoryConfig:
        config = LdapDirectoryConfig(**kwargs)
        self._session.add(config)
        await self._session.commit()
        return config

    async def update_config(self, config_id: str, **kwargs: Any) -> LdapDirectoryConfig:
        result = await self._session.execute(select(LdapDirectoryConfig).where(LdapDirectoryConfig.config_id == config_id))
        c = result.scalar_one_or_none()
        if not c:
            raise ValueError("Config not found")
        for k, v in kwargs.items():
            if hasattr(c, k) and k != "config_id":
                setattr(c, k, v)
        await self._session.commit()
        return c

    async def delete_config(self, config_id: str) -> bool:
        result = await self._session.execute(select(LdapDirectoryConfig).where(LdapDirectoryConfig.config_id == config_id))
        c = result.scalar_one_or_none()
        if not c:
            return False
        await self._session.delete(c)
        await self._session.commit()
        return True

    async def update_connection_test(self, config_id: str, status: str, error: str | None = None) -> LdapDirectoryConfig:
        result = await self._session.execute(select(LdapDirectoryConfig).where(LdapDirectoryConfig.config_id == config_id))
        c = result.scalar_one_or_none()
        if not c:
            raise ValueError("Config not found")
        c.connection_test_status = status
        c.connection_test_error = error
        await self._session.commit()
        return c