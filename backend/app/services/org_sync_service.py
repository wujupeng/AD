import logging
from datetime import datetime, timezone
from typing import Any

from app.interfaces.i_ldap_provider import ILdapProvider
from app.interfaces.i_cache_provider import ICacheProvider
from app.interfaces.i_audit_provider import IAuditProvider
from app.repositories.user_repository import UserRepository
from app.repositories.ou_repository import OuRepository
from app.repositories.group_repository import GroupRepository

logger = logging.getLogger(__name__)


class OrgSyncService:
    def __init__(
        self,
        ldap_provider: ILdapProvider,
        cache_provider: ICacheProvider,
        audit_provider: IAuditProvider,
        user_repo: UserRepository,
        ou_repo: OuRepository,
        group_repo: GroupRepository,
    ):
        self._ldap = ldap_provider
        self._cache = cache_provider
        self._audit = audit_provider
        self._user_repo = user_repo
        self._ou_repo = ou_repo
        self._group_repo = group_repo

    async def sync_incremental(self) -> dict[str, Any]:
        usn_str = await self._cache.get("sync_usn:latest")
        usn_from = int(usn_str) if usn_str else 0

        stats = {"ous": {"created": 0, "updated": 0, "deleted": 0}, "users": {"created": 0, "updated": 0, "deleted": 0}, "groups": {"created": 0, "updated": 0, "deleted": 0}}

        ou_changes = await self._ldap.search_changed_objects("", usn_from, object_class="organizationalUnit")
        for ou_data in ou_changes:
            dn = ou_data.get("distinguishedName", [""])[0] if isinstance(ou_data.get("distinguishedName"), list) else ou_data.get("distinguishedName", "")
            if not dn:
                continue
            is_deleted = ou_data.get("isDeleted", [False])[0] if isinstance(ou_data.get("isDeleted"), list) else ou_data.get("isDeleted", False)
            if is_deleted:
                await self._ou_repo.soft_delete(dn)
                stats["ous"]["deleted"] += 1
            else:
                existing = await self._ou_repo.get_by_dn(dn)
                if existing:
                    stats["ous"]["updated"] += 1
                else:
                    stats["ous"]["created"] += 1
                await self._ou_repo.create_or_update(dn, {
                    "ou_name": ou_data.get("ou", [""])[0] if isinstance(ou_data.get("ou"), list) else ou_data.get("ou", ""),
                    "parent_dn": ou_data.get("parent_dn"),
                    "usn_changed": ou_data.get("uSNChanged", [0])[0] if isinstance(ou_data.get("uSNChanged"), list) else ou_data.get("uSNChanged", 0),
                })

        user_changes = await self._ldap.search_changed_objects("", usn_from, object_class="user")
        for user_data in user_changes:
            dn = user_data.get("distinguishedName", [""])[0] if isinstance(user_data.get("distinguishedName"), list) else user_data.get("distinguishedName", "")
            if not dn:
                continue
            is_deleted = user_data.get("isDeleted", [False])[0] if isinstance(user_data.get("isDeleted"), list) else user_data.get("isDeleted", False)
            sid = user_data.get("objectSid", [""])[0] if isinstance(user_data.get("objectSid"), list) else user_data.get("objectSid", "")
            if is_deleted:
                await self._user_repo.soft_delete(sid)
                stats["users"]["deleted"] += 1
            else:
                await self._user_repo.create_or_update(sid, {
                    "dn": dn,
                    "username": user_data.get("sAMAccountName", [""])[0] if isinstance(user_data.get("sAMAccountName"), list) else user_data.get("sAMAccountName", ""),
                    "display_name": user_data.get("displayName", [""])[0] if isinstance(user_data.get("displayName"), list) else user_data.get("displayName", ""),
                    "email": user_data.get("mail", [""])[0] if isinstance(user_data.get("mail"), list) else user_data.get("mail", ""),
                    "usn_changed": user_data.get("uSNChanged", [0])[0] if isinstance(user_data.get("uSNChanged"), list) else user_data.get("uSNChanged", 0),
                })
                existing = await self._user_repo.get_by_sid(sid)
                if existing and existing.synced_at:
                    stats["users"]["updated"] += 1
                else:
                    stats["users"]["created"] += 1

        group_changes = await self._ldap.search_changed_objects("", usn_from, object_class="group")
        for group_data in group_changes:
            dn = group_data.get("distinguishedName", [""])[0] if isinstance(group_data.get("distinguishedName"), list) else group_data.get("distinguishedName", "")
            if not dn:
                continue
            is_deleted = group_data.get("isDeleted", [False])[0] if isinstance(group_data.get("isDeleted"), list) else group_data.get("isDeleted", False)
            if is_deleted:
                await self._group_repo.soft_delete(dn)
                stats["groups"]["deleted"] += 1
            else:
                await self._group_repo.create_or_update(dn, {
                    "group_name": group_data.get("cn", [""])[0] if isinstance(group_data.get("cn"), list) else group_data.get("cn", ""),
                    "usn_changed": group_data.get("uSNChanged", [0])[0] if isinstance(group_data.get("uSNChanged"), list) else group_data.get("uSNChanged", 0),
                })
                existing = await self._group_repo.get_by_dn(dn)
                if existing and existing.synced_at:
                    stats["groups"]["updated"] += 1
                else:
                    stats["groups"]["created"] += 1

        max_usn = max(
            ou_data.get("uSNChanged", [0])[0] if isinstance(ou_data.get("uSNChanged"), list) else ou_data.get("uSNChanged", 0)
            for ou_data in ou_changes
        ) if ou_changes else usn_from
        await self._cache.set("sync_usn:latest", str(max_usn))

        await self._audit.log_event({
            "event_type": "ORG_SYNC_COMPLETED",
            "result": "success",
            "details": str(stats),
            "occurred_at": datetime.now(timezone.utc),
        })

        return stats