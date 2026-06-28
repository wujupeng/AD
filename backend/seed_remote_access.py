import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.database import engine
from app.models.remote_access import VpnGateway, VpnPolicy, DeviceClassification

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

VPN_GATEWAYS = [
    {
        "gateway_name": "SH-VPN-GW01",
        "gateway_site": "shanghai_hq",
        "gateway_ip": "10.1.1.100",
        "gateway_role": "primary",
        "tunnel_protocol": "IKEv2_SSTP_Fallback",
        "max_concurrent_sessions": 500,
        "served_sites": ["shanghai_hq", "shanghai_factory", "ningde", "chuzhou", "huaian", "changzhou"],
        "health_status": "online",
    },
    {
        "gateway_name": "HU-VPN-GW01",
        "gateway_site": "hungary",
        "gateway_ip": "10.10.1.100",
        "gateway_role": "secondary",
        "tunnel_protocol": "IKEv2_SSTP_Fallback",
        "max_concurrent_sessions": 300,
        "served_sites": ["hungary", "vietnam", "mexico"],
        "health_status": "online",
    },
]

VPN_POLICIES = [
    {
        "policy_type": "device_tunnel",
        "policy_name": "AlwaysOn-DeviceTunnel",
        "policy_config": {
            "connection_name": "Company Device Tunnel",
            "server_address": "vpn.company.local",
            "tunnel_type": "IKEv2",
            "authentication": "machine_certificate",
            "routing_policy_type": "SplitTunnel",
            "trigger_type": "AlwaysOn",
        },
        "target_ou_dns": ["OU=Servers,DC=company,DC=local", "OU=Workstations,DC=company,DC=local"],
        "is_enabled": True,
    },
    {
        "policy_type": "user_tunnel",
        "policy_name": "AlwaysOn-UserTunnel",
        "policy_config": {
            "connection_name": "Company User Tunnel",
            "server_address": "vpn.company.local",
            "tunnel_type": "IKEv2+SSTP",
            "authentication": "user_certificate+mfa",
            "routing_policy_type": "SplitTunnel",
            "trigger_type": "OnDemand",
        },
        "target_ou_dns": ["OU=Users,DC=company,DC=local"],
        "is_enabled": True,
    },
    {
        "policy_type": "gateway_selection",
        "policy_name": "Gateway-Selection-Rules",
        "policy_config": {
            "rules": [
                {"source_sites": ["shanghai_hq", "shanghai_factory", "ningde", "chuzhou", "huaian", "changzhou"], "primary_gateway": "SH-VPN-GW01", "secondary_gateway": "HU-VPN-GW01", "failover_threshold_seconds": 5},
                {"source_sites": ["hungary", "vietnam", "mexico"], "primary_gateway": "HU-VPN-GW01", "secondary_gateway": "SH-VPN-GW01", "failover_threshold_seconds": 5},
            ]
        },
        "is_enabled": True,
    },
    {
        "policy_type": "cached_credentials",
        "policy_name": "Cached-Logon-Count-Policy",
        "policy_config": {
            "enterprise_laptop": 100,
            "enterprise_desktop": 10,
            "byod": 0,
            "kiosk": 0,
        },
        "is_enabled": True,
    },
]

DEVICE_CLASSIFICATIONS = [
    {
        "device_class": "enterprise_laptop",
        "display_name": "企业笔记本",
        "auth_methods": ["kerberos", "certificate"],
        "vpn_tunnel_type": "device_and_user",
        "cached_logon_count": 100,
        "conditional_access_level": "standard",
        "bitlocker_required": True,
        "defender_required": True,
        "target_ou_dn": "OU=Laptops,OU=Workstations,DC=company,DC=local",
    },
    {
        "device_class": "enterprise_desktop",
        "display_name": "企业台式机",
        "auth_methods": ["kerberos"],
        "vpn_tunnel_type": "none",
        "cached_logon_count": 10,
        "conditional_access_level": "standard",
        "bitlocker_required": True,
        "defender_required": True,
        "target_ou_dn": "OU=Desktops,OU=Workstations,DC=company,DC=local",
    },
    {
        "device_class": "byod",
        "display_name": "BYOD设备",
        "auth_methods": ["entra_id_mfa"],
        "vpn_tunnel_type": "user_only",
        "cached_logon_count": 0,
        "conditional_access_level": "enhanced",
        "bitlocker_required": False,
        "defender_required": False,
        "target_ou_dn": "",
    },
    {
        "device_class": "kiosk",
        "display_name": "Kiosk终端",
        "auth_methods": ["kerberos"],
        "vpn_tunnel_type": "device_only",
        "cached_logon_count": 0,
        "conditional_access_level": "strict",
        "bitlocker_required": True,
        "defender_required": True,
        "target_ou_dn": "OU=Kiosks,OU=Workstations,DC=company,DC=local",
    },
]


async def seed_remote_access():
    async with AsyncSessionLocal() as session:
        for gw_data in VPN_GATEWAYS:
            result = await session.execute(select(VpnGateway).where(VpnGateway.gateway_name == gw_data["gateway_name"]))
            if result.scalar_one_or_none() is None:
                gw = VpnGateway(**gw_data)
                session.add(gw)
                print(f"  Seeded VPN Gateway: {gw_data['gateway_name']}")
        await session.commit()

        for pol_data in VPN_POLICIES:
            result = await session.execute(select(VpnPolicy).where(VpnPolicy.policy_name == pol_data["policy_name"]))
            if result.scalar_one_or_none() is None:
                pol = VpnPolicy(**pol_data)
                session.add(pol)
                print(f"  Seeded VPN Policy: {pol_data['policy_name']}")
        await session.commit()

        for dc_data in DEVICE_CLASSIFICATIONS:
            result = await session.execute(select(DeviceClassification).where(DeviceClassification.device_class == dc_data["device_class"]))
            if result.scalar_one_or_none() is None:
                dc = DeviceClassification(**dc_data)
                session.add(dc)
                print(f"  Seeded Device Classification: {dc_data['device_class']}")
        await session.commit()

    print("Remote access seed data completed!")


async def main():
    from app.models.ad_objects import Base
    from app.models.remote_access import VpnGateway, VpnSession, VpnPolicy, DeviceClassification, RemoteAccessAuditLog
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("All tables created/verified.")
    await seed_remote_access()


if __name__ == "__main__":
    asyncio.run(main())