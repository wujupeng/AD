from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.hybrid_identity import CloudPhaseConfig


class HybridIdentityRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_current_phase(self) -> CloudPhaseConfig | None:
        result = await self._session.execute(select(CloudPhaseConfig).limit(1))
        return result.scalar_one_or_none()

    async def update_phase(self, phase_id: str, data: dict[str, Any]) -> CloudPhaseConfig | None:
        existing = await self._session.get(CloudPhaseConfig, phase_id)
        if existing:
            for key, value in data.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            await self._session.flush()
        return existing

    async def update_sync_status(self, phase_id: str, entra_sync_status: str | None = None, intune_status: str | None = None) -> bool:
        values = {}
        if entra_sync_status:
            values["entra_id_sync_status"] = entra_sync_status
        if intune_status:
            values["intune_compliance_status"] = intune_status
        if not values:
            return False
        result = await self._session.execute(update(CloudPhaseConfig).where(CloudPhaseConfig.id == phase_id).values(**values))
        return result.rowcount > 0