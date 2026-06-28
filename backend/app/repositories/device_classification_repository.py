from typing import Any
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.remote_access import DeviceClassification


class DeviceClassificationRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_all(self) -> list[DeviceClassification]:
        result = await self._session.execute(select(DeviceClassification).order_by(DeviceClassification.device_class))
        return list(result.scalars().all())

    async def get_by_class(self, device_class: str) -> DeviceClassification | None:
        result = await self._session.execute(select(DeviceClassification).where(DeviceClassification.device_class == device_class))
        return result.scalar_one_or_none()

    async def get_by_ca_level(self, level: str) -> list[DeviceClassification]:
        result = await self._session.execute(select(DeviceClassification).where(DeviceClassification.conditional_access_level == level))
        return list(result.scalars().all())

    async def update_policy(self, device_class: str, **kwargs: Any) -> None:
        await self._session.execute(update(DeviceClassification).where(DeviceClassification.device_class == device_class).values(**kwargs))
        await self._session.commit()