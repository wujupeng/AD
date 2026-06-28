import logging
from typing import Any

import ldap3

from app.interfaces.i_dc_management_provider import IDcManagementProvider
from app.core.config import settings

logger = logging.getLogger(__name__)


class DcManagementAdapter(IDcManagementProvider):
    def __init__(self):
        self._servers: dict[str, ldap3.Server] = {}

    def _get_server(self, dc_hostname: str) -> ldap3.Server:
        if dc_hostname not in self._servers:
            self._servers[dc_hostname] = ldap3.Server(
                dc_hostname, port=settings.AD_LDAPS_PORT, use_ssl=True, connect_timeout=5
            )
        return self._servers[dc_hostname]

    def _get_svc_connection(self, dc_hostname: str) -> ldap3.Connection:
        server = self._get_server(dc_hostname)
        svc_upn = f"svc_adbiz@{settings.AD_DOMAIN}"
        return ldap3.Connection(server, user=svc_upn, password=settings.AD_SERVICE_ACCOUNT_PASSWORD, auto_bind=True, raise_exceptions=True)

    async def query_dc_health(self, dc_hostname: str) -> dict[str, Any]:
        try:
            import time
            start = time.monotonic()
            conn = self._get_svc_connection(dc_hostname)
            ldap_ms = int((time.monotonic() - start) * 1000)
            conn.unbind()
            return {"dc_hostname": dc_hostname, "status": "healthy", "ldap_response_ms": ldap_ms}
        except Exception as e:
            logger.warning("DC health check failed for %s: %s", dc_hostname, e)
            return {"dc_hostname": dc_hostname, "status": "unreachable", "error": str(e)}

    async def query_replication_metadata(self, dc_hostname: str) -> list[dict[str, Any]]:
        try:
            conn = self._get_svc_connection(dc_hostname)
            conn.search(
                settings.AD_SEARCH_BASE,
                "(objectClass=*)",
                search_scope=ldap3.BASE,
                attributes=["msDS-HasDomainNCs", "fSMORoleOwner"],
            )
            results = []
            for entry in conn.entries:
                results.append(entry.entry_attributes_as_dict)
            conn.unbind()
            return results
        except Exception as e:
            logger.warning("Replication metadata query failed for %s: %s", dc_hostname, e)
            return []

    async def transfer_fsmo_role(self, role: str, target_dc: str) -> dict[str, Any]:
        return {"role": role, "target_dc": target_dc, "status": "not_implemented", "message": "FSMO transfer requires PowerShell Remoting"}

    async def query_dc_config(self, dc_hostname: str) -> dict[str, Any]:
        try:
            conn = self._get_svc_connection(dc_hostname)
            conn.search(
                settings.AD_SEARCH_BASE,
                "(objectClass=*)",
                search_scope=ldap3.BASE,
                attributes=["defaultNamingContext", "rootDomainNamingContext", "dnsHostName", "supportedLDAPVersion"],
            )
            config = {}
            if conn.entries:
                config = conn.entries[0].entry_attributes_as_dict
            conn.unbind()
            return config
        except Exception as e:
            logger.warning("DC config query failed for %s: %s", dc_hostname, e)
            return {"error": str(e)}

    async def query_gpo_links(self, ou_dn: str) -> list[dict[str, Any]]:
        try:
            conn = self._get_svc_connection(next(iter(self._servers), f"dc01.{settings.AD_DOMAIN}"))
            conn.search(
                ou_dn,
                "(objectClass=*)",
                search_scope=ldap3.BASE,
                attributes=["gPLink", "gPOptions"],
            )
            results = []
            if conn.entries:
                attrs = conn.entries[0].entry_attributes_as_dict
                gplink_raw = attrs.get("gPLink", [""])[0] if isinstance(attrs.get("gPLink"), list) else attrs.get("gPLink", "")
                if gplink_raw:
                    results.append({"ou_dn": ou_dn, "gPLink": gplink_raw, "gPOptions": attrs.get("gPOptions", [0])[0] if isinstance(attrs.get("gPOptions"), list) else attrs.get("gPOptions", 0)})
            conn.unbind()
            return results
        except Exception as e:
            logger.warning("GPO links query failed for %s: %s", ou_dn, e)
            return []