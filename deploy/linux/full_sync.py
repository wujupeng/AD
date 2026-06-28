import asyncio
import sys
sys.path.insert(0, '/home/debian/AD/backend')

from app.core.config import settings
from app.adapters.ldap_adapter import LdapAdapter
from app.adapters.redis_cache_adapter import RedisCacheAdapter
from app.adapters.pg_audit_adapter import PgAuditAdapter
from app.core.database import async_session_factory
from app.repositories.ou_repository import OuRepository
from app.repositories.user_repository import UserRepository
from app.repositories.group_repository import GroupRepository
from app.services.org_sync_service import OrgSyncService
import ldap3


async def full_sync():
    ldap = LdapAdapter()
    cache = RedisCacheAdapter()
    async with async_session_factory() as session:
        audit = PgAuditAdapter(session)
        ou_repo = OuRepository(session)
        user_repo = UserRepository(session)
        group_repo = GroupRepository(session)
        sync_svc = OrgSyncService(ldap, cache, audit, user_repo, ou_repo, group_repo)

        # Full sync: search all OUs, Users, Groups from AD
        print("Syncing OUs...")
        ou_results = await ldap.search(settings.AD_SEARCH_BASE, "(objectClass=organizationalUnit)")
        for ou_data in ou_results:
            dn = ou_data.get("distinguishedName", "")
            if isinstance(dn, list):
                dn = dn[0] if dn else ""
            if not dn:
                continue
            ou_name = ou_data.get("ou", "")
            if isinstance(ou_name, list):
                ou_name = ou_name[0] if ou_name else ""
            parent_dn_parts = dn.split(",", 1)
            parent_dn = parent_dn_parts[1] if len(parent_dn_parts) > 1 else None
            usn = ou_data.get("uSNChanged", 0)
            if isinstance(usn, list):
                usn = usn[0] if usn else 0
            await ou_repo.create_or_update(dn, {
                "ou_name": ou_name,
                "parent_dn": parent_dn,
                "usn_changed": usn,
            })
            print(f"  OU: {dn}")
        print(f"  Total OUs: {len(ou_results)}")

        print("Syncing Users...")
        user_results = await ldap.search(settings.AD_SEARCH_BASE, "(objectClass=user)")
        for user_data in user_results:
            dn = user_data.get("distinguishedName", "")
            if isinstance(dn, list):
                dn = dn[0] if dn else ""
            if not dn:
                continue
            sid = user_data.get("objectSid", "")
            if isinstance(sid, list):
                sid = sid[0] if sid else ""
            username = user_data.get("sAMAccountName", "")
            if isinstance(username, list):
                username = username[0] if username else ""
            display_name = user_data.get("displayName", "")
            if isinstance(display_name, list):
                display_name = display_name[0] if display_name else ""
            email = user_data.get("mail", "")
            if isinstance(email, list):
                email = email[0] if email else ""
            usn = user_data.get("uSNChanged", 0)
            if isinstance(usn, list):
                usn = usn[0] if usn else 0
            ou_dn_parts = dn.split(",", 1)
            ou_dn = ou_dn_parts[1] if len(ou_dn_parts) > 1 else None
            if sid:
                await user_repo.create_or_update(sid, {
                    "dn": dn,
                    "username": username,
                    "display_name": display_name,
                    "email": email,
                    "ou_dn": ou_dn,
                    "usn_changed": usn,
                })
                print(f"  User: {username} ({dn})")
        print(f"  Total Users: {len(user_results)}")

        print("Syncing Groups...")
        group_results = await ldap.search(settings.AD_SEARCH_BASE, "(objectClass=group)")
        for group_data in group_results:
            dn = group_data.get("distinguishedName", "")
            if isinstance(dn, list):
                dn = dn[0] if dn else ""
            if not dn:
                continue
            group_name = group_data.get("cn", "")
            if isinstance(group_name, list):
                group_name = group_name[0] if group_name else ""
            usn = group_data.get("uSNChanged", 0)
            if isinstance(usn, list):
                usn = usn[0] if usn else 0
            ou_dn_parts = dn.split(",", 1)
            ou_dn = ou_dn_parts[1] if len(ou_dn_parts) > 1 else None
            await group_repo.create_or_update(dn, {
                "group_name": group_name,
                "usn_changed": usn,
            })
            print(f"  Group: {group_name} ({dn})")
        print(f"  Total Groups: {len(group_results)}")

        await session.commit()
        print("\nFull sync completed!")


if __name__ == "__main__":
    asyncio.run(full_sync())