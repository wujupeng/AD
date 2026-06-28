from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.middleware import RequestIdMiddleware
from app.schemas.response import ApiError, ApiResponse


def create_app() -> FastAPI:
    application = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
    )

    application.add_middleware(RequestIdMiddleware)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    _register_exception_handlers(application)
    _register_routers(application)

    @application.get("/health", tags=["Health"])
    async def health_check():
        return ApiResponse(data={"status": "healthy", "version": settings.APP_VERSION})

    return application


def _register_exception_handlers(application: FastAPI):
    @application.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content=ApiResponse(
                code=500,
                message="Internal Server Error",
                data=ApiError(code="INTERNAL_ERROR", message=str(exc)).model_dump(),
                request_id=getattr(request.state, "request_id", None),
            ).model_dump(),
        )


def _register_routers(application: FastAPI):
    from app.routers import auth_router, integration_router, org_router, permission_router, dfs_router, print_router, mail_router, audit_router, health_router
    from app.routers import dc_management_router, dfs_management_router, pki_management_router, tier_security_router, hybrid_identity_router, monitoring_alert_router, sdwan_router, secure_print_router
    from app.routers import remote_access_router, vpn_management_router
    from app.routers import identity_center_router
    from app.routers import settings_router

    application.include_router(auth_router.router, prefix="/api")
    application.include_router(integration_router.router, prefix="/api")
    application.include_router(org_router.router, prefix="/api")
    application.include_router(permission_router.router, prefix="/api")
    application.include_router(dfs_router.router, prefix="/api")
    application.include_router(print_router.router, prefix="/api")
    application.include_router(mail_router.router, prefix="/api")
    application.include_router(audit_router.router, prefix="/api")
    application.include_router(health_router.router, prefix="/api")

    application.include_router(dc_management_router.router, prefix="/api")
    application.include_router(dfs_management_router.router, prefix="/api")
    application.include_router(pki_management_router.router, prefix="/api")
    application.include_router(tier_security_router.router, prefix="/api")
    application.include_router(hybrid_identity_router.router, prefix="/api")
    application.include_router(monitoring_alert_router.router, prefix="/api")
    application.include_router(sdwan_router.router, prefix="/api")
    application.include_router(secure_print_router.router, prefix="/api")
    application.include_router(remote_access_router.router, prefix="/api")
    application.include_router(vpn_management_router.router, prefix="/api")
    application.include_router(identity_center_router.router, prefix="/api")
    application.include_router(settings_router.router, prefix="/api")

    @application.on_event("startup")
    async def init_services():
        from app.core.database import async_session_factory
        from app.adapters.remote_access_adapter import RemoteAccessAdapter
        from app.adapters.vpn_adapter import VpnAdapter
        from app.adapters.defender_adapter import DefenderAdapter
        from app.repositories.vpn_gateway_repository import VpnGatewayRepository
        from app.repositories.vpn_session_repository import VpnSessionRepository
        from app.repositories.vpn_policy_repository import VpnPolicyRepository
        from app.repositories.device_classification_repository import DeviceClassificationRepository
        from app.repositories.remote_access_audit_repository import RemoteAccessAuditRepository
        from app.services.remote_access_service import RemoteAccessService

        ra_adapter = RemoteAccessAdapter()
        vpn_adapter = VpnAdapter()
        defender_adapter = DefenderAdapter()
        session = async_session_factory()
        svc = RemoteAccessService(
            vpn_gateway_repo=VpnGatewayRepository(session),
            vpn_session_repo=VpnSessionRepository(session),
            vpn_policy_repo=VpnPolicyRepository(session),
            device_classification_repo=DeviceClassificationRepository(session),
            remote_access_audit_repo=RemoteAccessAuditRepository(session),
            remote_access_provider=ra_adapter,
            vpn_provider=vpn_adapter,
            defender_provider=defender_adapter,
        )
        remote_access_router._remote_access_service = svc
        vpn_management_router._remote_access_service = svc

        from app.repositories.identity_center_repositories import (
            IdentityLifecycleEventRepository, HrOnboardingRequestRepository,
            HrOffboardingRequestRepository, HrTransferRequestRepository,
            PrintCostAuditRepository, Wifi8021xPolicyRepository,
            AutopilotProfileRepository, ConditionalAccessRuleRepository,
            SamlOidcApplicationRepository, IdentitySourcePolicyRepository,
        )
        from app.services.identity_center_service import IdentityCenterService

        ic_session = async_session_factory()
        ic_svc = IdentityCenterService(
            lifecycle_repo=IdentityLifecycleEventRepository(ic_session),
            onboarding_repo=HrOnboardingRequestRepository(ic_session),
            offboarding_repo=HrOffboardingRequestRepository(ic_session),
            transfer_repo=HrTransferRequestRepository(ic_session),
            print_cost_repo=PrintCostAuditRepository(ic_session),
            wifi_policy_repo=Wifi8021xPolicyRepository(ic_session),
            autopilot_repo=AutopilotProfileRepository(ic_session),
            ca_rule_repo=ConditionalAccessRuleRepository(ic_session),
            saml_oidc_repo=SamlOidcApplicationRepository(ic_session),
            identity_source_repo=IdentitySourcePolicyRepository(ic_session),
        )
        identity_center_router._service = ic_svc

        from app.adapters.system_monitor_adapter import SystemMonitorAdapter
        from app.adapters.redis_cache_adapter import RedisCacheAdapter
        from app.services.system_monitor_service import SystemMonitorService

        cache = RedisCacheAdapter()
        monitor_adapter = SystemMonitorAdapter(cache)
        monitor_svc = SystemMonitorService(monitor_adapter, cache)
        health_router._monitor_service = monitor_svc

        from app.repositories.cached_logon_policy_repository import CachedLogonPolicyRepository
        from app.repositories.entra_hybrid_join_repository import EntraHybridJoinRepository
        from app.repositories.dc_isolation_policy_repository import DcIsolationPolicyRepository
        from app.repositories.ldap_directory_config_repository import LdapDirectoryConfigRepository
        from app.repositories.external_integration_repository import ExternalIntegrationRepository
        from app.repositories.site_config_repository import SiteConfigRepository
        from app.repositories.integration_config_repository import IntegrationConfigRepository
        from app.adapters.pg_audit_adapter import PgAuditAdapter
        from app.services.settings_service import SettingsService

        settings_session = async_session_factory()
        settings_svc = SettingsService(
            cached_logon_repo=CachedLogonPolicyRepository(settings_session),
            hybrid_join_repo=EntraHybridJoinRepository(settings_session),
            dc_isolation_repo=DcIsolationPolicyRepository(settings_session),
            ldap_config_repo=LdapDirectoryConfigRepository(settings_session),
            external_integration_repo=ExternalIntegrationRepository(settings_session),
            site_repo=SiteConfigRepository(settings_session),
            integration_repo=IntegrationConfigRepository(settings_session),
            audit=PgAuditAdapter(settings_session),
        )
        settings_router._service = settings_svc


app = create_app()