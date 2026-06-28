import logging
from typing import Any

from app.interfaces.i_saml_provider import ISamlProvider
from app.interfaces.i_cache_provider import ICacheProvider
from app.interfaces.i_audit_provider import IAuditProvider
from app.repositories.integration_config_repository import IntegrationConfigRepository

logger = logging.getLogger(__name__)


class SamlProviderService:
    def __init__(
        self,
        saml_provider: ISamlProvider,
        cache_provider: ICacheProvider,
        audit_provider: IAuditProvider,
        integration_repo: IntegrationConfigRepository,
    ):
        self._saml = saml_provider
        self._cache = cache_provider
        self._audit = audit_provider
        self._integration_repo = integration_repo

    async def handle_sso(self, sp_name: str, authn_request: str, user_sid: str, user_attributes: dict[str, Any]) -> dict[str, Any]:
        sp_config = await self._integration_repo.get_sp_config(sp_name)
        if not sp_config:
            return {"success": False, "error": "SP_NOT_FOUND"}

        attribute_mappings = await self._integration_repo.get_attribute_mappings(sp_name)
        role_mappings = await self._integration_repo.get_role_mappings(sp_name)

        saml_attributes = {}
        for mapping in attribute_mappings:
            ad_value = user_attributes.get(mapping.ad_attribute)
            if ad_value:
                saml_attributes[mapping.claim_name] = ad_value if isinstance(ad_value, str) else ad_value[0] if isinstance(ad_value, list) else str(ad_value)

        for role_mapping in role_mappings:
            if "groups" in user_attributes:
                groups = user_attributes["groups"]
                if isinstance(groups, list) and role_mapping.ad_group_dn in groups:
                    saml_attributes.setdefault("roles", []).append(role_mapping.app_role)

        assertion = await self._saml.sign_assertion(
            attributes=saml_attributes,
            audience=sp_config.entity_id,
            recipient=sp_config.acs_url or "",
        )

        await self._audit.log_event({
            "event_type": "SAML_SSO_SUCCESS",
            "user_sid": user_sid,
            "resource": sp_name,
            "result": "success",
            "occurred_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc),
        })

        return {
            "success": True,
            "assertion": assertion,
            "acs_url": sp_config.acs_url,
        }

    async def get_metadata(self) -> str:
        return await self._saml.generate_metadata()

    async def handle_slo(self, sp_name: str, logout_request: str) -> dict[str, Any]:
        result = await self._saml.parse_logout_request(logout_request)
        return result