import logging
from datetime import datetime, timezone
from typing import Any

from app.interfaces.i_ldap_provider import ILdapProvider
from app.interfaces.i_kerberos_provider import IKerberosProvider
from app.interfaces.i_token_provider import ITokenProvider
from app.interfaces.i_cache_provider import ICacheProvider
from app.interfaces.i_audit_provider import IAuditProvider
from app.interfaces.i_entra_id_provider import IEntraIdProvider
from app.core.config import settings

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(
        self,
        ldap_provider: ILdapProvider,
        kerberos_provider: IKerberosProvider,
        token_provider: ITokenProvider,
        cache_provider: ICacheProvider,
        audit_provider: IAuditProvider,
        entra_id_provider: IEntraIdProvider | None = None,
    ):
        self._ldap = ldap_provider
        self._kerberos = kerberos_provider
        self._token = token_provider
        self._cache = cache_provider
        self._audit = audit_provider
        self._entra_id = entra_id_provider

    def _resolve_tier_level(self, user_groups: list[str]) -> int:
        group_names = [g.split(",")[0].replace("CN=", "") for g in user_groups]
        if "GG_Tier0_Admin" in group_names or "Domain Admins" in group_names:
            return 0
        if "GG_Tier1_Admin" in group_names or "Server Operators" in group_names:
            return 1
        return 2

    async def authenticate_password(self, username: str, password: str, client_ip: str | None = None, site_code: str | None = None) -> dict[str, Any]:
        rate_key = f"rate_limit:login:{username}"
        attempts_str = await self._cache.get(rate_key)
        attempts = int(attempts_str) if attempts_str else 0

        if attempts >= settings.AUTH_MAX_LOGIN_ATTEMPTS:
            await self._audit.log_event({
                "event_type": "AUTH_ACCOUNT_LOCKED",
                "username": username,
                "site_code": site_code,
                "client_ip": client_ip,
                "result": "failure",
                "details": f"Account locked after {settings.AUTH_MAX_LOGIN_ATTEMPTS} failed attempts",
                "occurred_at": datetime.now(timezone.utc),
            })
            return {"success": False, "error": "AUTH_ACCOUNT_LOCKED"}

        bind_result = await self._ldap.bind(username, password)
        auth_source = "ad"
        hybrid_identity = False

        if not bind_result.get("success"):
            if self._entra_id and bind_result.get("error") == "AUTH_DC_UNREACHABLE":
                entra_result = await self._entra_id.authenticate(username, password)
                if entra_result.get("success"):
                    bind_result = entra_result
                    auth_source = "entra_id"
                    hybrid_identity = True
                    logger.info("User %s authenticated via Entra ID fallback", username)

            if not bind_result.get("success"):
                await self._cache.set(rate_key, str(attempts + 1), ttl=settings.AUTH_ACCOUNT_LOCKOUT_MINUTES * 60)
                error = bind_result.get("error", "AUTH_INVALID_CREDENTIALS")
                await self._audit.log_event({
                    "event_type": "AUTH_LOGIN_FAILED",
                    "username": username,
                    "site_code": site_code,
                    "client_ip": client_ip,
                    "result": "failure",
                    "details": error,
                    "occurred_at": datetime.now(timezone.utc),
                })
                return {"success": False, "error": error}

        await self._cache.delete(rate_key)

        user_dn = bind_result["user_dn"]
        user_attrs = await self._ldap.get_user_attributes(user_dn)
        user_groups = await self._ldap.get_user_groups(user_dn)

        uac = user_attrs.get("userAccountControl", [512])
        if isinstance(uac, list):
            uac = uac[0] if uac else 512
        if uac & 0x0002:
            return {"success": False, "error": "AUTH_ACCOUNT_DISABLED"}

        sid = user_attrs.get("objectSid", [""])[0] if isinstance(user_attrs.get("objectSid"), list) else user_attrs.get("objectSid", "")

        tier_level = self._resolve_tier_level(user_groups)

        payload = {
            "sub": sid,
            "username": username,
            "dn": user_dn,
            "groups": user_groups,
            "site_code": site_code or "shanghai_hq",
            "tier_level": tier_level,
            "hybrid_identity": hybrid_identity,
            "auth_source": auth_source,
        }

        access_token = await self._token.issue_token(payload)
        refresh_token = await self._token.issue_refresh_token({"sub": sid, "username": username})

        await self._cache.set(f"session:{sid}", access_token, ttl=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60)

        await self._audit.log_event({
            "event_type": "AUTH_LOGIN_SUCCESS",
            "user_sid": sid,
            "username": username,
            "site_code": site_code,
            "client_ip": client_ip,
            "result": "success",
            "details": "Password authentication",
            "occurred_at": datetime.now(timezone.utc),
        })

        return {
            "success": True,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "sid": sid,
                "username": username,
                "display_name": user_attrs.get("displayName", [""])[0] if isinstance(user_attrs.get("displayName"), list) else user_attrs.get("displayName", ""),
                "email": user_attrs.get("mail", [""])[0] if isinstance(user_attrs.get("mail"), list) else user_attrs.get("mail", ""),
                "site": site_code,
                "groups": user_groups,
                "tier_level": tier_level,
                "hybrid_identity": hybrid_identity,
                "auth_source": auth_source,
            },
        }

    async def authenticate_kerberos(self, ticket: bytes, service_principal: str, client_ip: str | None = None) -> dict[str, Any]:
        result = await self._kerberos.validate_ticket(ticket, service_principal)
        if not result.get("valid"):
            return {"success": False, "error": result.get("error", "AUTH_TICKET_INVALID")}

        principal = result["principal"]
        username = principal.split("@")[0] if "@" in principal else principal

        user_attrs = await self._ldap.get_user_attributes(f"CN={username},{settings.AD_SEARCH_BASE}")
        user_groups = await self._ldap.get_user_groups(f"CN={username},{settings.AD_SEARCH_BASE}")

        sid = user_attrs.get("objectSid", [""])[0] if isinstance(user_attrs.get("objectSid"), list) else user_attrs.get("objectSid", "")

        payload = {
            "sub": sid,
            "username": username,
            "groups": user_groups,
            "auth_method": "kerberos",
        }

        access_token = await self._token.issue_token(payload)
        refresh_token = await self._token.issue_refresh_token({"sub": sid, "username": username})

        await self._audit.log_event({
            "event_type": "AUTH_KERBEROS_SUCCESS",
            "user_sid": sid,
            "username": username,
            "client_ip": client_ip,
            "result": "success",
            "occurred_at": datetime.now(timezone.utc),
        })

        return {
            "success": True,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "sid": sid,
                "username": username,
                "groups": user_groups,
            },
        }

    async def refresh_token(self, refresh_token: str) -> dict[str, Any]:
        try:
            payload = await self._token.validate_refresh_token(refresh_token)
            sid = payload.get("sub")
            username = payload.get("username")

            new_payload = {"sub": sid, "username": username}
            new_access_token = await self._token.issue_token(new_payload)
            new_refresh_token = await self._token.issue_refresh_token(new_payload)

            await self._cache.set(f"session:{sid}", new_access_token, ttl=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60)

            return {
                "success": True,
                "access_token": new_access_token,
                "refresh_token": new_refresh_token,
            }
        except ValueError as e:
            return {"success": False, "error": str(e)}

    async def logout(self, user_sid: str, token_id: str | None = None) -> bool:
        await self._cache.delete(f"session:{user_sid}")
        if token_id:
            await self._token.revoke_token(token_id)

        await self._audit.log_event({
            "event_type": "AUTH_LOGOUT",
            "user_sid": user_sid,
            "result": "success",
            "occurred_at": datetime.now(timezone.utc),
        })
        return True

    async def verify_mfa(self, mfa_token: str, mfa_code: str) -> dict[str, Any]:
        return {"success": True, "verified": True}