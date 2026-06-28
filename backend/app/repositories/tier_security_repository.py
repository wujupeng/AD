from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from app.models.tier_security import TierDefinition, ComputerSecurityBaseline


class TierSecurityRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def list_tiers(self) -> list[TierDefinition]:
        result = await self._session.execute(select(TierDefinition).order_by(TierDefinition.tier_level))
        return list(result.scalars().all())

    async def get_tier(self, tier_level: int) -> TierDefinition | None:
        return await self._session.get(TierDefinition, tier_level)

    async def update_tier(self, tier_level: int, data: dict[str, Any]) -> TierDefinition | None:
        existing = await self.get_tier(tier_level)
        if existing:
            for key, value in data.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            await self._session.flush()
        return existing

    async def list_baselines(self, site: str | None = None, compliance_status: str | None = None) -> list[ComputerSecurityBaseline]:
        query = select(ComputerSecurityBaseline)
        if site:
            query = query.where(ComputerSecurityBaseline.site == site)
        if compliance_status:
            query = query.where(ComputerSecurityBaseline.compliance_status == compliance_status)
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def get_baseline(self, computer_name: str) -> ComputerSecurityBaseline | None:
        return await self._session.get(ComputerSecurityBaseline, computer_name)

    async def upsert_baseline(self, computer_name: str, data: dict[str, Any]) -> ComputerSecurityBaseline:
        existing = await self.get_baseline(computer_name)
        if existing:
            for key, value in data.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            await self._session.flush()
            return existing
        baseline = ComputerSecurityBaseline(computer_name=computer_name, **data)
        self._session.add(baseline)
        await self._session.flush()
        return baseline

    async def get_compliance_stats(self) -> dict[str, Any]:
        total_result = await self._session.execute(select(func.count()).select_from(ComputerSecurityBaseline))
        total = total_result.scalar() or 0
        compliant_result = await self._session.execute(select(func.count()).select_from(ComputerSecurityBaseline).where(ComputerSecurityBaseline.compliance_status == "compliant"))
        compliant = compliant_result.scalar() or 0
        return {"total": total, "compliant": compliant, "non_compliant": total - compliant, "compliance_rate": round(compliant / total * 100, 1) if total > 0 else 0}