from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.identity_center import IdentityLifecycleEvent, HrOnboardingRequest, HrOffboardingRequest, HrTransferRequest, PrintCostAuditRecord, Wifi8021xPolicy, AutopilotProfile, ConditionalAccessRule, SamlOidcApplication, IdentitySourcePolicy
from datetime import datetime, timedelta


class IdentityLifecycleEventRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, data: dict[str, Any]) -> IdentityLifecycleEvent:
        try:
            event = IdentityLifecycleEvent(**data)
            self._session.add(event)
            await self._session.commit()
            return event
        except Exception:
            await self._session.rollback()
            raise

    async def get_by_account(self, ad_account: str, limit: int = 100) -> list[IdentityLifecycleEvent]:
        result = await self._session.execute(
            select(IdentityLifecycleEvent).where(IdentityLifecycleEvent.ad_account == ad_account).order_by(IdentityLifecycleEvent.event_time.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def get_recent(self, limit: int = 100, offset: int = 0) -> list[IdentityLifecycleEvent]:
        result = await self._session.execute(
            select(IdentityLifecycleEvent).order_by(IdentityLifecycleEvent.event_time.desc()).limit(limit).offset(offset)
        )
        return list(result.scalars().all())


class HrOnboardingRequestRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, data: dict[str, Any]) -> HrOnboardingRequest:
        try:
            req = HrOnboardingRequest(**data)
            self._session.add(req)
            await self._session.commit()
            return req
        except Exception:
            await self._session.rollback()
            raise

    async def get_by_id(self, request_id: str) -> HrOnboardingRequest | None:
        result = await self._session.execute(select(HrOnboardingRequest).where(HrOnboardingRequest.request_id == request_id))
        return result.scalar_one_or_none()

    async def get_all(self, limit: int = 50) -> list[HrOnboardingRequest]:
        result = await self._session.execute(select(HrOnboardingRequest).order_by(HrOnboardingRequest.created_at.desc()).limit(limit))
        return list(result.scalars().all())


class HrOffboardingRequestRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, data: dict[str, Any]) -> HrOffboardingRequest:
        try:
            req = HrOffboardingRequest(**data)
            self._session.add(req)
            await self._session.commit()
            return req
        except Exception:
            await self._session.rollback()
            raise

    async def get_by_id(self, request_id: str) -> HrOffboardingRequest | None:
        result = await self._session.execute(select(HrOffboardingRequest).where(HrOffboardingRequest.request_id == request_id))
        return result.scalar_one_or_none()

    async def get_all(self, limit: int = 50) -> list[HrOffboardingRequest]:
        result = await self._session.execute(select(HrOffboardingRequest).order_by(HrOffboardingRequest.created_at.desc()).limit(limit))
        return list(result.scalars().all())


class HrTransferRequestRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, data: dict[str, Any]) -> HrTransferRequest:
        try:
            req = HrTransferRequest(**data)
            self._session.add(req)
            await self._session.commit()
            return req
        except Exception:
            await self._session.rollback()
            raise

    async def get_by_id(self, request_id: str) -> HrTransferRequest | None:
        result = await self._session.execute(select(HrTransferRequest).where(HrTransferRequest.request_id == request_id))
        return result.scalar_one_or_none()

    async def get_all(self, limit: int = 50) -> list[HrTransferRequest]:
        result = await self._session.execute(select(HrTransferRequest).order_by(HrTransferRequest.created_at.desc()).limit(limit))
        return list(result.scalars().all())


class PrintCostAuditRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, data: dict[str, Any]) -> PrintCostAuditRecord:
        try:
            record = PrintCostAuditRecord(**data)
            self._session.add(record)
            await self._session.commit()
            return record
        except Exception:
            await self._session.rollback()
            raise

    async def get_recent(self, limit: int = 100, offset: int = 0) -> list[PrintCostAuditRecord]:
        result = await self._session.execute(
            select(PrintCostAuditRecord).order_by(PrintCostAuditRecord.operation_time.desc()).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def get_stats_by_department(self) -> list[dict[str, Any]]:
        from sqlalchemy import func
        result = await self._session.execute(
            select(PrintCostAuditRecord.department, func.count(PrintCostAuditRecord.cost_audit_id), func.sum(PrintCostAuditRecord.page_count), func.sum(PrintCostAuditRecord.estimated_cost))
            .where(PrintCostAuditRecord.department.isnot(None))
            .group_by(PrintCostAuditRecord.department)
        )
        return [{"department": r[0], "job_count": r[1], "total_pages": r[2] or 0, "total_cost": float(r[3] or 0)} for r in result.all()]


class Wifi8021xPolicyRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_all(self) -> list[Wifi8021xPolicy]:
        result = await self._session.execute(select(Wifi8021xPolicy).order_by(Wifi8021xPolicy.policy_name))
        return list(result.scalars().all())

    async def create(self, data: dict[str, Any]) -> Wifi8021xPolicy:
        policy = Wifi8021xPolicy(**data)
        self._session.add(policy)
        await self._session.commit()
        return policy

    async def update(self, policy_id: str, **kwargs: Any) -> None:
        from sqlalchemy import update
        await self._session.execute(update(Wifi8021xPolicy).where(Wifi8021xPolicy.policy_id == policy_id).values(**kwargs))
        await self._session.commit()


class AutopilotProfileRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_all(self) -> list[AutopilotProfile]:
        result = await self._session.execute(select(AutopilotProfile).order_by(AutopilotProfile.profile_name))
        return list(result.scalars().all())

    async def create(self, data: dict[str, Any]) -> AutopilotProfile:
        profile = AutopilotProfile(**data)
        self._session.add(profile)
        await self._session.commit()
        return profile

    async def update(self, profile_id: str, **kwargs: Any) -> None:
        from sqlalchemy import update
        await self._session.execute(update(AutopilotProfile).where(AutopilotProfile.profile_id == profile_id).values(**kwargs))
        await self._session.commit()


class ConditionalAccessRuleRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_all(self) -> list[ConditionalAccessRule]:
        result = await self._session.execute(select(ConditionalAccessRule).order_by(ConditionalAccessRule.priority))
        return list(result.scalars().all())

    async def create(self, data: dict[str, Any]) -> ConditionalAccessRule:
        rule = ConditionalAccessRule(**data)
        self._session.add(rule)
        await self._session.commit()
        return rule

    async def update(self, rule_id: str, **kwargs: Any) -> None:
        from sqlalchemy import update
        await self._session.execute(update(ConditionalAccessRule).where(ConditionalAccessRule.rule_id == rule_id).values(**kwargs))
        await self._session.commit()


class SamlOidcApplicationRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_all(self) -> list[SamlOidcApplication]:
        result = await self._session.execute(select(SamlOidcApplication).order_by(SamlOidcApplication.app_name))
        return list(result.scalars().all())

    async def create(self, data: dict[str, Any]) -> SamlOidcApplication:
        app = SamlOidcApplication(**data)
        self._session.add(app)
        await self._session.commit()
        return app

    async def update(self, app_id: str, **kwargs: Any) -> None:
        from sqlalchemy import update
        await self._session.execute(update(SamlOidcApplication).where(SamlOidcApplication.app_id == app_id).values(**kwargs))
        await self._session.commit()

    async def delete(self, app_id: str) -> None:
        result = await self._session.execute(select(SamlOidcApplication).where(SamlOidcApplication.app_id == app_id))
        app = result.scalar_one_or_none()
        if app:
            await self._session.delete(app)
            await self._session.commit()


class IdentitySourcePolicyRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_all(self) -> list[IdentitySourcePolicy]:
        result = await self._session.execute(select(IdentitySourcePolicy))
        return list(result.scalars().all())

    async def update(self, policy_id: str, **kwargs: Any) -> None:
        from sqlalchemy import update
        await self._session.execute(update(IdentitySourcePolicy).where(IdentitySourcePolicy.policy_id == policy_id).values(**kwargs))
        await self._session.commit()