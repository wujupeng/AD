import logging
from datetime import datetime, timezone
from typing import Any

from app.interfaces.i_tier_security_provider import ITierSecurityProvider
from app.interfaces.i_cache_provider import ICacheProvider
from app.interfaces.i_audit_provider import IAuditProvider
from app.repositories.tier_security_repository import TierSecurityRepository

logger = logging.getLogger(__name__)


class TierSecurityService:
    def __init__(
        self,
        tier_provider: ITierSecurityProvider,
        cache_provider: ICacheProvider,
        audit_provider: IAuditProvider,
        tier_repo: TierSecurityRepository,
    ):
        self._tier_provider = tier_provider
        self._cache = cache_provider
        self._audit = audit_provider
        self._tier_repo = tier_repo

    async def get_tier_overview(self) -> list[dict[str, Any]]:
        tiers = await self._tier_repo.list_tiers()
        return [{"tier_level": t.tier_level, "tier_name": t.tier_name, "server_list": t.server_list or [], "admin_groups": t.admin_groups or [], "login_restriction": t.login_restriction} for t in tiers]

    async def get_violations(self, hours: int = 24) -> list[dict[str, Any]]:
        return await self._tier_provider.query_violations(hours)

    async def get_laps_password(self, computer_name: str) -> dict[str, Any]:
        result = await self._tier_provider.query_laps_password(computer_name)
        await self._audit.log_event({"event_type": "tier_violation", "action": "laps_password_read", "resource": computer_name, "result": "success", "occurred_at": datetime.now(timezone.utc)})
        return result

    async def get_bitlocker_key(self, computer_name: str) -> dict[str, Any]:
        return await self._tier_provider.query_bitlocker_key(computer_name)

    async def get_credential_guard_status(self, computer_name: str | None = None) -> dict[str, Any]:
        return await self._tier_provider.query_credential_guard_status(computer_name)

    async def get_applocker_wdac_status(self, computer_name: str | None = None) -> dict[str, Any]:
        return await self._tier_provider.query_applocker_wdac_status(computer_name)

    async def get_security_baseline(self, site: str | None = None) -> dict[str, Any]:
        baselines = await self._tier_repo.list_baselines(site)
        stats = await self._tier_repo.get_compliance_stats()
        items = [{"computer_name": b.computer_name, "site": b.site, "laps_enabled": b.laps_enabled, "credential_guard_enabled": b.credential_guard_enabled, "bitlocker_enabled": b.bitlocker_enabled, "defender_enabled": b.defender_enabled, "compliance_status": b.compliance_status} for b in baselines]
        return {"statistics": stats, "items": items}

    async def check_tier_violation(self, user_tier_level: int, target_tier_level: int) -> bool:
        if user_tier_level > target_tier_level:
            await self._audit.log_event({"event_type": "tier_violation", "action": "cross_tier_login_blocked", "details": f"Tier{user_tier_level} user attempted to access Tier{target_tier_level} resource", "result": "blocked", "occurred_at": datetime.now(timezone.utc)})
            return True
        return False