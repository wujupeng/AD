import logging
from typing import Any

from app.interfaces.i_ldap_provider import ILdapProvider
from app.interfaces.i_cache_provider import ICacheProvider

logger = logging.getLogger(__name__)


class PermissionService:
    def __init__(
        self,
        ldap_provider: ILdapProvider,
        cache_provider: ICacheProvider,
    ):
        self._ldap = ldap_provider
        self._cache = cache_provider

    async def check_permission(self, user_sid: str, resource: str, action: str) -> dict[str, Any]:
        effective_perms = await self.get_effective_permissions(user_sid)
        resource_perms = effective_perms.get("resources", {}).get(resource, {})
        if action in resource_perms.get("allowed_actions", []):
            return {"allowed": True, "reason": "Granted by group membership", "groups": resource_perms.get("granting_groups", [])}
        return {"allowed": False, "reason": "No matching permission found", "groups": []}

    async def resolve_groups(self, user_sid: str) -> list[dict[str, Any]]:
        cache_key = f"perm:groups:{user_sid}"
        cached = await self._cache.get(cache_key)
        if cached:
            import json
            return json.loads(cached)

        user_dn = ""
        groups = await self._ldap.get_user_groups(user_dn)
        result = [{"dn": g, "name": g.split(",")[0].replace("CN=", "")} for g in groups]

        await self._cache.set(cache_key, __import__("json").dumps(result), ttl=300)
        return result

    async def get_effective_permissions(self, user_sid: str) -> dict[str, Any]:
        cache_key = f"perm:effective:{user_sid}"
        cached = await self._cache.get(cache_key)
        if cached:
            import json
            return json.loads(cached)

        groups = await self.resolve_groups(user_sid)
        global_groups = [g for g in groups if g["name"].startswith("GG_")]
        domain_local_groups = [g for g in groups if g["name"].startswith("DL_")]

        result = {
            "user_sid": user_sid,
            "global_groups": global_groups,
            "domain_local_groups": domain_local_groups,
            "resources": {},
        }

        await self._cache.set(cache_key, __import__("json").dumps(result), ttl=300)
        return result

    async def invalidate_cache(self, user_sid: str | None = None) -> int:
        if user_sid:
            await self._cache.delete(f"perm:groups:{user_sid}")
            await self._cache.delete(f"perm:effective:{user_sid}")
            return 2
        return 0