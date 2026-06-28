import logging
from typing import Any

from app.interfaces.i_oidc_provider import IOidcProvider
from app.interfaces.i_token_provider import ITokenProvider
from app.interfaces.i_cache_provider import ICacheProvider
from app.interfaces.i_audit_provider import IAuditProvider
from app.repositories.integration_config_repository import IntegrationConfigRepository

logger = logging.getLogger(__name__)


class OidcProviderService:
    def __init__(
        self,
        oidc_provider: IOidcProvider,
        token_provider: ITokenProvider,
        cache_provider: ICacheProvider,
        audit_provider: IAuditProvider,
        integration_repo: IntegrationConfigRepository,
    ):
        self._oidc = oidc_provider
        self._token = token_provider
        self._cache = cache_provider
        self._audit = audit_provider
        self._integration_repo = integration_repo

    async def authorize(self, client_id: str, redirect_uri: str, scope: str, state: str) -> dict[str, Any]:
        sp_config = await self._integration_repo.list_sp_configs(sp_type="oidc")
        matching = [s for s in sp_config if s.client_id == client_id]
        if not matching:
            return {"success": False, "error": "INVALID_CLIENT_ID"}

        code = await self._oidc.authorize(client_id, redirect_uri, scope, state)
        await self._cache.set(f"auth_code:{code}", f"{client_id}:{redirect_uri}:{state}", ttl=60)

        return {"success": True, "code": code, "state": state}

    async def exchange_code(self, code: str, client_id: str, client_secret: str, redirect_uri: str) -> dict[str, Any]:
        cached = await self._cache.get(f"auth_code:{code}")
        if not cached:
            return {"success": False, "error": "INVALID_AUTH_CODE"}

        await self._cache.delete(f"auth_code:{code}")

        token_result = await self._oidc.exchange_code(code, client_id, client_secret, redirect_uri)
        return {"success": True, **token_result}

    async def get_userinfo(self, access_token: str) -> dict[str, Any]:
        return await self._oidc.get_userinfo(access_token)

    async def get_discovery(self, base_url: str) -> dict[str, Any]:
        return await self._oidc.generate_discovery(base_url)

    async def get_jwks(self) -> dict[str, Any]:
        return await self._oidc.get_jwks()