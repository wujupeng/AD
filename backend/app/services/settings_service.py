import logging
from typing import Any

from app.repositories.cached_logon_policy_repository import CachedLogonPolicyRepository
from app.repositories.entra_hybrid_join_repository import EntraHybridJoinRepository
from app.repositories.dc_isolation_policy_repository import DcIsolationPolicyRepository
from app.repositories.ldap_directory_config_repository import LdapDirectoryConfigRepository
from app.repositories.external_integration_repository import ExternalIntegrationRepository
from app.repositories.site_config_repository import SiteConfigRepository
from app.repositories.integration_config_repository import IntegrationConfigRepository
from app.adapters.pg_audit_adapter import PgAuditAdapter

logger = logging.getLogger(__name__)


class SettingsService:
    def __init__(
        self,
        cached_logon_repo: CachedLogonPolicyRepository,
        hybrid_join_repo: EntraHybridJoinRepository,
        dc_isolation_repo: DcIsolationPolicyRepository,
        ldap_config_repo: LdapDirectoryConfigRepository,
        external_integration_repo: ExternalIntegrationRepository,
        site_repo: SiteConfigRepository,
        integration_repo: IntegrationConfigRepository,
        audit: PgAuditAdapter,
    ):
        self._cached_logon_repo = cached_logon_repo
        self._hybrid_join_repo = hybrid_join_repo
        self._dc_isolation_repo = dc_isolation_repo
        self._ldap_config_repo = ldap_config_repo
        self._external_integration_repo = external_integration_repo
        self._site_repo = site_repo
        self._integration_repo = integration_repo
        self._audit = audit

    async def get_settings_summary(self) -> dict[str, Any]:
        cached_cred = await self.get_cached_cred_policy()
        hybrid_join = await self.get_hybrid_join_status()
        dc_isolation = await self.get_dc_isolation_policy()
        sites = await self._site_repo.list_sites()
        integrations = await self._integration_repo.list_sp_configs()
        return {
            "cached_cred_policy": cached_cred,
            "hybrid_join_status": hybrid_join,
            "dc_isolation_policy": dc_isolation,
            "sites": [{"site_code": s.site_code, "site_name": s.site_name, "is_active": s.is_active} for s in sites],
            "integrations_count": len(integrations),
        }

    async def get_cached_cred_policy(self) -> dict[str, Any]:
        policy = await self._cached_logon_repo.get_or_create_default()
        return {
            "policy_id": policy.policy_id,
            "policy_name": policy.policy_name,
            "policy_config": policy.policy_config,
            "is_enabled": policy.is_enabled,
            "version": policy.version,
        }

    async def update_cached_cred_policy(self, policy_config: dict | None = None, is_enabled: bool | None = None, version: int | None = None) -> dict[str, Any]:
        if policy_config:
            if policy_config.get("byod", 0) != 0:
                raise ValueError("BYOD devices must not cache domain credentials (byod must be 0)")
            if policy_config.get("kiosk", 0) != 0:
                raise ValueError("Kiosk devices must not cache domain credentials (kiosk must be 0)")
            laptop = policy_config.get("enterprise_laptop", 0)
            if not (1 <= laptop <= 500):
                raise ValueError("enterprise_laptop must be between 1 and 500")
            desktop = policy_config.get("enterprise_desktop", 0)
            if not (1 <= desktop <= 50):
                raise ValueError("enterprise_desktop must be between 1 and 50")
        policy = await self._cached_logon_repo.get_or_create_default()
        updated = await self._cached_logon_repo.update_policy(
            policy.policy_id, policy_config=policy_config, is_enabled=is_enabled, version=version
        )
        return {"policy_id": updated.policy_id, "policy_name": updated.policy_name, "policy_config": updated.policy_config, "is_enabled": updated.is_enabled, "version": updated.version}

    async def get_hybrid_join_status(self) -> dict[str, Any]:
        config = await self._hybrid_join_repo.get_or_create_default()
        return {
            "status": config.status,
            "total_devices": config.total_devices,
            "registered": config.registered,
            "pending": config.pending,
            "failed": config.failed,
            "message": config.message,
        }

    async def configure_hybrid_join(self, entra_connect_server: str | None = None, sync_scope: str | None = None, device_registration_policy: str | None = None) -> dict[str, Any]:
        config = await self._hybrid_join_repo.get_or_create_default()
        if config.status == "not_configured":
            config.status = "configuring"
            config.entra_connect_server = entra_connect_server
            config.sync_scope = sync_scope
            config.device_registration_policy = device_registration_policy
            config.message = "Entra Hybrid Join is being configured (requires Phase2+)"
            from app.core.database import async_session_factory
            session = async_session_factory()
            repo = EntraHybridJoinRepository(session)
            await repo.update_config(config.config_id, status="configuring", entra_connect_server=entra_connect_server, sync_scope=sync_scope, device_registration_policy=device_registration_policy)
        return await self.get_hybrid_join_status()

    async def get_dc_isolation_policy(self) -> dict[str, Any]:
        policy = await self._dc_isolation_repo.get_or_create_default()
        return {
            "policy_id": policy.policy_id,
            "isolation_enabled": policy.isolation_enabled,
            "rules": policy.rules or [],
            "message": policy.message,
            "version": policy.version,
        }

    async def update_dc_isolation_policy(self, isolation_enabled: bool | None = None, rules: list | None = None, version: int | None = None) -> dict[str, Any]:
        policy = await self._dc_isolation_repo.get_or_create_default()
        updated = await self._dc_isolation_repo.update_policy(
            policy.policy_id, isolation_enabled=isolation_enabled, rules=rules, version=version
        )
        return {"policy_id": updated.policy_id, "isolation_enabled": updated.isolation_enabled, "rules": updated.rules or [], "message": updated.message, "version": updated.version}

    async def list_sites(self) -> list[dict[str, Any]]:
        sites = await self._site_repo.list_sites()
        return [
            {
                "site_code": s.site_code,
                "site_name": s.site_name,
                "site_display_name": getattr(s, "site_display_name", None),
                "region": s.region,
                "country": s.country,
                "dc_priority_list": s.dc_priority_list,
                "dfs_servers": s.dfs_servers,
                "print_servers": s.print_servers,
                "vpn_gateway": getattr(s, "vpn_gateway", None),
                "is_active": s.is_active,
            }
            for s in sites
        ]

    async def update_site_config(self, site_code: str, **kwargs: Any) -> dict[str, Any]:
        site = await self._site_repo.get_by_code(site_code)
        if not site:
            raise ValueError(f"Site '{site_code}' not found")
        for k, v in kwargs.items():
            if hasattr(site, k):
                setattr(site, k, v)
        from app.core.database import async_session_factory
        session = async_session_factory()
        await session.commit()
        return {"site_code": site.site_code, "site_name": site.site_name, "updated": True}

    async def list_ldap_configs(self) -> list[dict[str, Any]]:
        configs = await self._ldap_config_repo.list_configs()
        return [{"config_id": c.config_id, "config_name": c.config_name, "server_url": c.server_url, "base_dn": c.base_dn, "is_enabled": c.is_enabled, "connection_test_status": c.connection_test_status} for c in configs]

    async def create_ldap_config(self, **kwargs: Any) -> dict[str, Any]:
        config = await self._ldap_config_repo.create_config(**kwargs)
        return {"config_id": config.config_id, "config_name": config.config_name}

    async def delete_ldap_config(self, config_id: str) -> bool:
        return await self._ldap_config_repo.delete_config(config_id)

    async def list_external_integrations(self, integration_type: str | None = None) -> list[dict[str, Any]]:
        integrations = await self._external_integration_repo.list_integrations(integration_type)
        return [{"integration_id": i.integration_id, "integration_type": i.integration_type, "integration_name": i.integration_name, "server_url": i.server_url, "is_enabled": i.is_enabled, "connection_status": i.connection_status} for i in integrations]

    async def create_external_integration(self, **kwargs: Any) -> dict[str, Any]:
        config = await self._external_integration_repo.create_integration(**kwargs)
        return {"integration_id": config.integration_id, "integration_name": config.integration_name}

    async def delete_external_integration(self, integration_id: str) -> bool:
        return await self._external_integration_repo.delete_integration(integration_id)