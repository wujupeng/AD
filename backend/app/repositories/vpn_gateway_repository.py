from typing import Any
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.remote_access import VpnGateway


class VpnGatewayRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_all(self) -> list[VpnGateway]:
        result = await self._session.execute(select(VpnGateway).order_by(VpnGateway.gateway_name))
        return list(result.scalars().all())

    async def get_by_id(self, gateway_id: str) -> VpnGateway | None:
        result = await self._session.execute(select(VpnGateway).where(VpnGateway.gateway_id == gateway_id))
        return result.scalar_one_or_none()

    async def get_by_site(self, site: str) -> list[VpnGateway]:
        result = await self._session.execute(select(VpnGateway).where(VpnGateway.gateway_site == site))
        return list(result.scalars().all())

    async def get_by_role(self, role: str) -> list[VpnGateway]:
        result = await self._session.execute(select(VpnGateway).where(VpnGateway.gateway_role == role))
        return list(result.scalars().all())

    async def get_by_health(self, health_status: str) -> list[VpnGateway]:
        result = await self._session.execute(select(VpnGateway).where(VpnGateway.health_status == health_status))
        return list(result.scalars().all())

    async def get_serving_site(self, site: str) -> list[VpnGateway]:
        result = await self._session.execute(select(VpnGateway))
        gateways = list(result.scalars().all())
        return [gw for gw in gateways if gw.served_sites and site in gw.served_sites]

    async def update_status(self, gateway_id: str, **kwargs: Any) -> None:
        await self._session.execute(update(VpnGateway).where(VpnGateway.gateway_id == gateway_id).values(**kwargs))
        await self._session.commit()