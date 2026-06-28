import logging
from typing import Any

import ldap3

from app.interfaces.i_tier_security_provider import ITierSecurityProvider
from app.core.config import settings

logger = logging.getLogger(__name__)


class TierSecurityAdapter(ITierSecurityProvider):
    def __init__(self):
        self._server = ldap3.Server(f"dc01.{settings.AD_DOMAIN}", port=settings.AD_LDAPS_PORT, use_ssl=True, connect_timeout=5)

    def _get_svc_connection(self) -> ldap3.Connection:
        svc_upn = f"svc_adbiz@{settings.AD_DOMAIN}"
        return ldap3.Connection(self._server, user=svc_upn, password=settings.AD_SERVICE_ACCOUNT_PASSWORD, auto_bind=True, raise_exceptions=True)

    async def query_tier_overview(self) -> list[dict[str, Any]]:
        return []

    async def query_violations(self, hours: int = 24) -> list[dict[str, Any]]:
        return []

    async def query_laps_password(self, computer_name: str) -> dict[str, Any]:
        try:
            conn = self._get_svc_connection()
            conn.search(
                settings.AD_SEARCH_BASE,
                f"(cn={computer_name})",
                search_scope=ldap3.SUBTREE,
                attributes=["ms-Mcs-AdmPwd", "ms-Mcs-AdmPwdExpirationTime"],
            )
            if conn.entries:
                attrs = conn.entries[0].entry_attributes_as_dict
                conn.unbind()
                return {"computer_name": computer_name, "laps_password": attrs.get("ms-Mcs-AdmPwd", [""])[0] if isinstance(attrs.get("ms-Mcs-AdmPwd"), list) else attrs.get("ms-Mcs-AdmPwd", ""), "expiry": attrs.get("ms-Mcs-AdmPwdExpirationTime", [""])[0] if isinstance(attrs.get("ms-Mcs-AdmPwdExpirationTime"), list) else attrs.get("ms-Mcs-AdmPwdExpirationTime", "")}
            conn.unbind()
            return {"computer_name": computer_name, "error": "Computer not found"}
        except Exception as e:
            logger.warning("LAPS query failed for %s: %s", computer_name, e)
            return {"computer_name": computer_name, "error": str(e)}

    async def query_bitlocker_key(self, computer_name: str) -> dict[str, Any]:
        return {"computer_name": computer_name, "status": "not_implemented", "message": "BitLocker key query requires LDAPS access to BDO container"}

    async def query_credential_guard_status(self, computer_name: str | None = None) -> dict[str, Any]:
        return {"status": "not_implemented"}

    async def query_applocker_wdac_status(self, computer_name: str | None = None) -> dict[str, Any]:
        return {"status": "not_implemented"}

    async def query_security_baseline(self, site: str | None = None) -> dict[str, Any]:
        return {"status": "not_implemented"}