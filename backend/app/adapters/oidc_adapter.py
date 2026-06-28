import logging
import secrets
from typing import Any

from app.interfaces.i_oidc_provider import IOidcProvider
from app.core.config import settings

logger = logging.getLogger(__name__)


class OidcAdapter(IOidcProvider):
    async def authorize(self, client_id: str, redirect_uri: str, scope: str, state: str) -> str:
        code = secrets.token_urlsafe(32)
        return code

    async def exchange_code(self, code: str, client_id: str, client_secret: str, redirect_uri: str) -> dict[str, Any]:
        return {
            "access_token": "",
            "token_type": "Bearer",
            "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "id_token": "",
        }

    async def get_userinfo(self, access_token: str) -> dict[str, Any]:
        return {"sub": "", "name": "", "email": "", "groups": []}

    async def generate_discovery(self, base_url: str) -> dict[str, Any]:
        return {
            "issuer": base_url,
            "authorization_endpoint": f"{base_url}/oidc/authorize",
            "token_endpoint": f"{base_url}/oidc/token",
            "userinfo_endpoint": f"{base_url}/oidc/userinfo",
            "jwks_uri": f"{base_url}/oidc/jwks",
            "response_types_supported": ["code"],
            "subject_types_supported": ["public"],
            "id_token_signing_alg_values_supported": ["RS256"],
            "scopes_supported": ["openid", "profile", "email"],
        }

    async def get_jwks(self) -> dict[str, Any]:
        return {"keys": []}