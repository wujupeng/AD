import uuid
from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.settings import DcIsolationPolicy


_DEFAULT_RULES = [
    {
        "rule_id": str(uuid.uuid4()),
        "rule_name": "Allow Internal LDAP/LDAPS/Kerberos/DNS",
        "direction": "inbound",
        "source_address": "10.0.0.0/8",
        "destination_port": "389,636,88,53",
        "protocol": "TCP/UDP",
        "action": "allow",
        "priority": 100,
        "is_enabled": True,
        "description": "Allow internal network to DC LDAP/LDAPS/Kerberos/DNS ports",
        "is_default": True,
    },
    {
        "rule_id": str(uuid.uuid4()),
        "rule_name": "Allow VPN Network",
        "direction": "inbound",
        "source_address": "172.16.0.0/12",
        "destination_port": "389,636,88,53",
        "protocol": "TCP/UDP",
        "action": "allow",
        "priority": 200,
        "is_enabled": True,
        "description": "Allow VPN network to DC LDAP/LDAPS/Kerberos/DNS ports",
        "is_default": True,
    },
    {
        "rule_id": str(uuid.uuid4()),
        "rule_name": "Deny RPC/SMB/RDP",
        "direction": "inbound",
        "source_address": "0.0.0.0/0",
        "destination_port": "135,445,3389",
        "protocol": "TCP",
        "action": "deny",
        "priority": 300,
        "is_enabled": True,
        "description": "Deny RPC/SMB/RDP access from any source",
        "is_default": True,
    },
]


class DcIsolationPolicyRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_policy(self) -> DcIsolationPolicy | None:
        result = await self._session.execute(select(DcIsolationPolicy).limit(1))
        return result.scalar_one_or_none()

    async def get_or_create_default(self) -> DcIsolationPolicy:
        policy = await self.get_policy()
        if policy:
            return policy
        policy = DcIsolationPolicy(
            isolation_enabled=True,
            rules=_DEFAULT_RULES,
            message="DC isolation policy requires firewall/ACL configuration",
            version=1,
        )
        self._session.add(policy)
        await self._session.commit()
        return policy

    async def update_policy(self, policy_id: str, isolation_enabled: bool | None = None, rules: list | None = None, version: int | None = None) -> DcIsolationPolicy:
        result = await self._session.execute(select(DcIsolationPolicy).where(DcIsolationPolicy.policy_id == policy_id))
        p = result.scalar_one_or_none()
        if not p:
            raise ValueError("Policy not found")
        if version is not None and p.version != version:
            raise ValueError(f"Version conflict: expected {p.version}, got {version}")
        if rules is not None:
            for old_rule in (p.rules or []):
                if old_rule.get("is_default") and not any(r.get("rule_id") == old_rule.get("rule_id") for r in rules):
                    raise ValueError(f"Default rule '{old_rule.get('rule_name')}' cannot be deleted, only disabled")
            p.rules = rules
        if isolation_enabled is not None:
            p.isolation_enabled = isolation_enabled
        p.version = (p.version or 0) + 1
        await self._session.commit()
        return p