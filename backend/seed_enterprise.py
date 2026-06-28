import asyncio
import uuid
from datetime import datetime, timezone, timedelta
from app.core.database import async_session_factory, engine
from app.models.ad_objects import Base
from app.models.dc_management import DcRegistry
from app.models.tier_security import TierDefinition
from app.models.hybrid_identity import CloudPhaseConfig
from app.models.site import SiteConfig
import json


DC_SEED_DATA = [
    {"dc_hostname": "DC01-SH-HQ", "dc_site": "shanghai_hq", "dc_ip_address": "10.1.1.1", "is_gc": True, "is_dns_integrated": True, "fsmo_roles": ["PDC", "RID", "Infrastructure"], "health_status": "healthy", "os_version": "Windows Server 2022"},
    {"dc_hostname": "DC02-SH-HQ", "dc_site": "shanghai_hq", "dc_ip_address": "10.1.1.2", "is_gc": True, "is_dns_integrated": True, "fsmo_roles": [], "health_status": "healthy", "os_version": "Windows Server 2022"},
    {"dc_hostname": "DC01-SH-FACTORY", "dc_site": "shanghai_factory", "dc_ip_address": "10.1.2.1", "is_gc": True, "is_dns_integrated": True, "fsmo_roles": [], "health_status": "healthy", "os_version": "Windows Server 2022"},
    {"dc_hostname": "DC01-ND", "dc_site": "ningde", "dc_ip_address": "10.2.1.1", "is_gc": True, "is_dns_integrated": True, "fsmo_roles": [], "health_status": "healthy", "os_version": "Windows Server 2022"},
    {"dc_hostname": "DC01-CZ", "dc_site": "chuzhou", "dc_ip_address": "10.3.1.1", "is_gc": True, "is_dns_integrated": True, "fsmo_roles": [], "health_status": "healthy", "os_version": "Windows Server 2022"},
    {"dc_hostname": "DC01-HA", "dc_site": "huaian", "dc_ip_address": "10.4.1.1", "is_gc": True, "is_dns_integrated": True, "fsmo_roles": [], "health_status": "healthy", "os_version": "Windows Server 2022"},
    {"dc_hostname": "DC01-CZC", "dc_site": "changzhou", "dc_ip_address": "10.5.1.1", "is_gc": True, "is_dns_integrated": True, "fsmo_roles": [], "health_status": "healthy", "os_version": "Windows Server 2022"},
    {"dc_hostname": "DC01-HU", "dc_site": "hungary", "dc_ip_address": "10.10.1.1", "is_gc": True, "is_dns_integrated": True, "fsmo_roles": ["Schema Master", "Domain Naming Master"], "health_status": "healthy", "os_version": "Windows Server 2022"},
    {"dc_hostname": "DC01-VN", "dc_site": "vietnam", "dc_ip_address": "10.11.1.1", "is_gc": True, "is_dns_integrated": True, "fsmo_roles": [], "health_status": "healthy", "os_version": "Windows Server 2022"},
    {"dc_hostname": "DC01-MX", "dc_site": "mexico", "dc_ip_address": "10.12.1.1", "is_gc": True, "is_dns_integrated": True, "fsmo_roles": [], "health_status": "healthy", "os_version": "Windows Server 2022"},
]

TIER_SEED_DATA = [
    {"tier_level": 0, "tier_name": "Tier0 - Identity & Infrastructure", "server_list": ["DC01-SH-HQ", "DC02-SH-HQ", "DC01-HU", "CA01"], "admin_groups": ["GG_Tier0_Admin", "Domain Admins"], "login_restriction": "Only Tier0 admins can log on to Tier0 servers"},
    {"tier_level": 1, "tier_name": "Tier1 - Server Infrastructure", "server_list": ["File01", "File02", "Print01", "Print02", "Exchange01"], "admin_groups": ["GG_Tier1_Admin", "Server Operators"], "login_restriction": "Tier0 admins must not log on to Tier1 servers; Tier1 admins can manage Tier1 servers"},
    {"tier_level": 2, "tier_name": "Tier2 - Endpoints", "server_list": [], "admin_groups": ["GG_Tier2_HelpDesk", "GG_IT_HelpDesk"], "login_restriction": "Tier0/1 admins must not log on to Tier2 endpoints; HelpDesk can assist users"},
]

SITE_SEED_DATA = [
    {"site_code": "shanghai_hq", "site_name": "Shanghai HQ", "region": "China", "country": "CN", "subnet_ranges": "10.1.1.0/24,10.1.10.0/24", "dc_priority_list": ["DC01-SH-HQ", "DC02-SH-HQ"], "timezone": "Asia/Shanghai", "language": "zh-CN", "dfs_servers": ["File01", "File02"], "print_servers": ["Print01", "Print02"]},
    {"site_code": "shanghai_factory", "site_name": "Shanghai Factory", "region": "China", "country": "CN", "subnet_ranges": "10.1.2.0/24", "dc_priority_list": ["DC01-SH-FACTORY", "DC01-SH-HQ"], "timezone": "Asia/Shanghai", "language": "zh-CN", "dfs_servers": ["File01"], "print_servers": ["Print01"]},
    {"site_code": "ningde", "site_name": "Ningde Factory", "region": "China", "country": "CN", "subnet_ranges": "10.2.1.0/24", "dc_priority_list": ["DC01-ND", "DC01-SH-HQ"], "timezone": "Asia/Shanghai", "language": "zh-CN", "dfs_servers": [], "print_servers": []},
    {"site_code": "chuzhou", "site_name": "Chuzhou Factory", "region": "China", "country": "CN", "subnet_ranges": "10.3.1.0/24", "dc_priority_list": ["DC01-CZ", "DC01-SH-HQ"], "timezone": "Asia/Shanghai", "language": "zh-CN", "dfs_servers": [], "print_servers": []},
    {"site_code": "huaian", "site_name": "Huaian Factory", "region": "China", "country": "CN", "subnet_ranges": "10.4.1.0/24", "dc_priority_list": ["DC01-HA", "DC01-SH-HQ"], "timezone": "Asia/Shanghai", "language": "zh-CN", "dfs_servers": [], "print_servers": []},
    {"site_code": "changzhou", "site_name": "Changzhou Factory", "region": "China", "country": "CN", "subnet_ranges": "10.5.1.0/24", "dc_priority_list": ["DC01-CZC", "DC01-SH-HQ"], "timezone": "Asia/Shanghai", "language": "zh-CN", "dfs_servers": [], "print_servers": []},
    {"site_code": "hungary", "site_name": "Hungary Factory", "region": "Europe", "country": "HU", "subnet_ranges": "10.10.1.0/24", "dc_priority_list": ["DC01-HU", "DC01-SH-HQ"], "timezone": "Europe/Budapest", "language": "hu", "dfs_servers": [], "print_servers": []},
    {"site_code": "vietnam", "site_name": "Vietnam Factory", "region": "SE Asia", "country": "VN", "subnet_ranges": "10.11.1.0/24", "dc_priority_list": ["DC01-VN", "DC01-SH-HQ"], "timezone": "Asia/Ho_Chi_Minh", "language": "vi", "dfs_servers": [], "print_servers": []},
    {"site_code": "mexico", "site_name": "Mexico Factory", "region": "North America", "country": "MX", "subnet_ranges": "10.12.1.0/24", "dc_priority_list": ["DC01-MX", "DC01-SH-HQ"], "timezone": "America/Mexico_City", "language": "es-MX", "dfs_servers": [], "print_servers": []},
]


async def seed_enterprise():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("All tables created/verified.")

    async with async_session_factory() as session:
        for dc_data in DC_SEED_DATA:
            existing = await session.get(DcRegistry, dc_data["dc_hostname"])
            if not existing:
                dc = DcRegistry(**dc_data)
                session.add(dc)
                print(f"  Seeded DC: {dc_data['dc_hostname']}")
        await session.commit()

        for tier_data in TIER_SEED_DATA:
            existing = await session.get(TierDefinition, tier_data["tier_level"])
            if not existing:
                tier = TierDefinition(**tier_data)
                session.add(tier)
                print(f"  Seeded Tier: {tier_data['tier_name']}")
        await session.commit()

        phase = CloudPhaseConfig(
            id=str(uuid.uuid4()),
            current_phase="Phase1",
            entra_id_sync_status="not_configured",
            intune_compliance_status="not_configured",
        )
        session.add(phase)
        await session.commit()
        print("  Seeded CloudPhaseConfig: Phase1")

        for site_data in SITE_SEED_DATA:
            from sqlalchemy import select
            result = await session.execute(select(SiteConfig).where(SiteConfig.site_code == site_data["site_code"]))
            if not result.scalar_one_or_none():
                site = SiteConfig(
                    site_code=site_data["site_code"],
                    site_name=site_data["site_name"],
                    region=site_data["region"],
                    country=site_data["country"],
                    subnet_ranges=site_data["subnet_ranges"],
                    dc_priority_list=site_data["dc_priority_list"],
                    timezone=site_data["timezone"],
                    language=site_data["language"],
                    dfs_servers=site_data.get("dfs_servers"),
                    print_servers=site_data.get("print_servers"),
                )
                session.add(site)
                print(f"  Seeded Site: {site_data['site_code']}")
        await session.commit()

    print("\nEnterprise seed data completed!")


if __name__ == "__main__":
    asyncio.run(seed_enterprise())