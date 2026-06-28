from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.settings import ExternalIntegrationConfig


class ExternalIntegrationRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def list_integrations(self, integration_type: str | None = None) -> list[ExternalIntegrationConfig]:
        q = select(ExternalIntegrationConfig).order_by(ExternalIntegrationConfig.integration_name)
        if integration_type:
            q = q.where(ExternalIntegrationConfig.integration_type == integration_type)
        result = await self._session.execute(q)
        return list(result.scalars().all())

    async def get_integration(self, integration_id: str) -> ExternalIntegrationConfig | None:
        result = await self._session.execute(select(ExternalIntegrationConfig).where(ExternalIntegrationConfig.integration_id == integration_id))
        return result.scalar_one_or_none()

    async def create_integration(self, **kwargs: Any) -> ExternalIntegrationConfig:
        config = ExternalIntegrationConfig(**kwargs)
        self._session.add(config)
        await self._session.commit()
        return config

    async def update_integration(self, integration_id: str, **kwargs: Any) -> ExternalIntegrationConfig:
        result = await self._session.execute(select(ExternalIntegrationConfig).where(ExternalIntegrationConfig.integration_id == integration_id))
        c = result.scalar_one_or_none()
        if not c:
            raise ValueError("Integration not found")
        for k, v in kwargs.items():
            if hasattr(c, k) and k != "integration_id":
                setattr(c, k, v)
        await self._session.commit()
        return c

    async def delete_integration(self, integration_id: str) -> bool:
        result = await self._session.execute(select(ExternalIntegrationConfig).where(ExternalIntegrationConfig.integration_id == integration_id))
        c = result.scalar_one_or_none()
        if not c:
            return False
        await self._session.delete(c)
        await self._session.commit()
        return True

    async def update_connection_status(self, integration_id: str, status: str, error: str | None = None) -> ExternalIntegrationConfig:
        result = await self._session.execute(select(ExternalIntegrationConfig).where(ExternalIntegrationConfig.integration_id == integration_id))
        c = result.scalar_one_or_none()
        if not c:
            raise ValueError("Integration not found")
        c.connection_status = status
        c.connection_test_error = error
        await self._session.commit()
        return c