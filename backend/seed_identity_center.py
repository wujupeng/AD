import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.database import engine
from app.models.identity_center import IdentitySourcePolicy

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

IDENTITY_SOURCE_POLICY = {
    "policy_name": "EnterpriseIdentitySourcePolicy",
    "primary_source": "ActiveDirectory",
    "internet_extension": "EntraID",
    "allow_cloud_only_users": False,
    "sync_failure_threshold_hours": 24,
    "downstream_systems": ["EntraID", "ERP", "MES", "PLM", "GitLab", "SecurePrint", "VPN", "WiFi"],
    "is_enabled": True,
}


async def seed_identity_center():
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(IdentitySourcePolicy).where(IdentitySourcePolicy.policy_name == IDENTITY_SOURCE_POLICY["policy_name"])
        )
        if result.scalar_one_or_none() is None:
            policy = IdentitySourcePolicy(**IDENTITY_SOURCE_POLICY)
            session.add(policy)
            print(f"  Seeded Identity Source Policy: {IDENTITY_SOURCE_POLICY['policy_name']}")
        await session.commit()

    print("Identity center seed data completed!")


async def main():
    from app.models.ad_objects import Base
    from app.models.identity_center import (IdentityLifecycleEvent, HrOnboardingRequest, HrOffboardingRequest,
        HrTransferRequest, PrintCostAuditRecord, Wifi8021xPolicy, AutopilotProfile,
        ConditionalAccessRule, SamlOidcApplication, IdentitySourcePolicy)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("All tables created/verified.")
    await seed_identity_center()


if __name__ == "__main__":
    asyncio.run(main())