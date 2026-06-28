from typing import Any

from fastapi import Request

from app.core.database import async_session_factory
from app.adapters.ldap_adapter import LdapAdapter
from app.adapters.kerberos_adapter import KerberosAdapter
from app.adapters.jwt_token_adapter import JwtTokenAdapter
from app.adapters.saml_adapter import SamlAdapter
from app.adapters.oidc_adapter import OidcAdapter
from app.adapters.dfs_adapter import DfsAdapter
from app.adapters.print_adapter import PrintAdapter
from app.adapters.exchange_adapter import ExchangeAdapter
from app.adapters.redis_cache_adapter import RedisCacheAdapter
from app.adapters.pg_audit_adapter import PgAuditAdapter
from app.adapters.dc_management_adapter import DcManagementAdapter
from app.adapters.dfs_replication_adapter import DfsReplicationAdapter
from app.adapters.pki_adapter import PkiAdapter
from app.adapters.tier_security_adapter import TierSecurityAdapter
from app.adapters.entra_id_adapter import EntraIdAdapter
from app.adapters.zabbix_adapter import ZabbixAdapter
from app.adapters.veeam_adapter import VeeamAdapter
from app.adapters.sdwan_adapter import SdwanAdapter
from app.adapters.secure_print_adapter import SecurePrintAdapter, CardMappingAdapter, PrintAuditAdapter
from app.adapters.remote_access_adapter import RemoteAccessAdapter
from app.adapters.vpn_adapter import VpnAdapter
from app.adapters.defender_adapter import DefenderAdapter
from app.repositories.user_repository import UserRepository
from app.repositories.ou_repository import OuRepository
from app.repositories.group_repository import GroupRepository
from app.repositories.audit_repository import AuditRepository
from app.repositories.print_task_repository import PrintTaskRepository
from app.repositories.dfs_access_repository import DfsAccessRepository
from app.repositories.integration_config_repository import IntegrationConfigRepository
from app.repositories.site_config_repository import SiteConfigRepository
from app.repositories.dc_repository import DcRepository
from app.repositories.dfs_replication_repository import DfsReplicationRepository
from app.repositories.pki_repository import PkiRepository
from app.repositories.tier_security_repository import TierSecurityRepository
from app.repositories.hybrid_identity_repository import HybridIdentityRepository
from app.repositories.alert_repository import AlertRepository
from app.repositories.sdwan_repository import SdwanRepository
from app.repositories.secure_print_repository import SecurePrintJobRepository, CardMappingRepository, MfpPrinterRepository, PrintAuditRepository
from app.repositories.vpn_gateway_repository import VpnGatewayRepository
from app.repositories.vpn_session_repository import VpnSessionRepository
from app.repositories.vpn_policy_repository import VpnPolicyRepository
from app.repositories.device_classification_repository import DeviceClassificationRepository
from app.repositories.remote_access_audit_repository import RemoteAccessAuditRepository
from app.repositories.identity_center_repositories import (
    IdentityLifecycleEventRepository, HrOnboardingRequestRepository,
    HrOffboardingRequestRepository, HrTransferRequestRepository,
    PrintCostAuditRepository, Wifi8021xPolicyRepository,
    AutopilotProfileRepository, ConditionalAccessRuleRepository,
    SamlOidcApplicationRepository, IdentitySourcePolicyRepository,
)
from app.services.auth_service import AuthService
from app.services.saml_provider import SamlProviderService
from app.services.oidc_provider import OidcProviderService
from app.services.org_sync_service import OrgSyncService
from app.services.permission_service import PermissionService
from app.services.site_awareness_service import SiteAwarenessService
from app.services.file_service import FileService
from app.services.print_service import PrintService
from app.services.mail_service import MailService
from app.services.audit_service import AuditService
from app.services.event_bus_service import EventBusService
from app.services.dc_management_service import DcManagementService
from app.services.dfs_replication_service import DfsReplicationService
from app.services.pki_management_service import PkiManagementService
from app.services.tier_security_service import TierSecurityService
from app.services.hybrid_identity_service import HybridIdentityService
from app.services.monitoring_alert_service import MonitoringAlertService
from app.services.sdwan_integration_service import SdwanIntegrationService
from app.services.secure_print_service import SecurePrintService
from app.services.remote_access_service import RemoteAccessService
from app.services.identity_center_service import IdentityCenterService
from app.interfaces.i_token_provider import ITokenProvider


_ldap = LdapAdapter()
_kerberos = KerberosAdapter()
_token = JwtTokenAdapter()
_saml = SamlAdapter()
_oidc = OidcAdapter()
_dfs = DfsAdapter()
_print = PrintAdapter()
_exchange = ExchangeAdapter()
_cache = RedisCacheAdapter()
_dc_mgmt = DcManagementAdapter()
_dfs_repl = DfsReplicationAdapter()
_pki = PkiAdapter()
_tier_sec = TierSecurityAdapter()
_entra_id = EntraIdAdapter()
_zabbix = ZabbixAdapter()
_veeam = VeeamAdapter()
_sdwan = SdwanAdapter()
_sp = SecurePrintAdapter()
_card = CardMappingAdapter()
_print_audit = PrintAuditAdapter()
_ra = RemoteAccessAdapter()
_vpn = VpnAdapter()
_defender = DefenderAdapter()


async def get_current_user(request: Request) -> dict[str, Any] | None:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header[7:]
    try:
        payload = await _token.validate_token(token)
        return payload
    except ValueError:
        return None


async def require_admin(request: Request) -> dict[str, Any]:
    user = await get_current_user(request)
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Not authenticated")
    groups = user.get("groups", [])
    if not any("Domain Admins" in g or "Enterprise Admins" in g for g in groups):
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


async def get_auth_service(request: Request) -> AuthService:
    session = async_session_factory()
    audit = PgAuditAdapter(session)
    return AuthService(_ldap, _kerberos, _token, _cache, audit)


async def get_saml_service(request: Request) -> SamlProviderService:
    session = async_session_factory()
    audit = PgAuditAdapter(session)
    integration_repo = IntegrationConfigRepository(session)
    return SamlProviderService(_saml, _cache, audit, integration_repo)


async def get_oidc_service(request: Request) -> OidcProviderService:
    session = async_session_factory()
    audit = PgAuditAdapter(session)
    integration_repo = IntegrationConfigRepository(session)
    return OidcProviderService(_oidc, _token, _cache, audit, integration_repo)


async def get_permission_service(request: Request) -> PermissionService:
    return PermissionService(_ldap, _cache)


async def get_file_service(request: Request) -> FileService:
    session = async_session_factory()
    audit = PgAuditAdapter(session)
    permission = PermissionService(_ldap, _cache)
    site_repo = SiteConfigRepository(session)
    site_awareness = SiteAwarenessService(_cache, site_repo)
    dfs_repo = DfsAccessRepository(session)
    return FileService(_dfs, audit, permission, site_awareness, dfs_repo)


async def get_print_service(request: Request) -> PrintService:
    session = async_session_factory()
    audit = PgAuditAdapter(session)
    permission = PermissionService(_ldap, _cache)
    print_repo = PrintTaskRepository(session)
    return PrintService(_print, audit, permission, print_repo)


async def get_mail_service(request: Request) -> MailService:
    session = async_session_factory()
    audit = PgAuditAdapter(session)
    return MailService(_exchange, _cache, audit)


async def get_audit_service(request: Request) -> AuditService:
    session = async_session_factory()
    audit = PgAuditAdapter(session)
    return AuditService(audit)


async def get_user_repo(request: Request) -> UserRepository:
    return UserRepository(async_session_factory())


async def get_ou_repo(request: Request) -> OuRepository:
    return OuRepository(async_session_factory())


async def get_group_repo(request: Request) -> GroupRepository:
    return GroupRepository(async_session_factory())


async def get_integration_repo(request: Request) -> IntegrationConfigRepository:
    return IntegrationConfigRepository(async_session_factory())


def get_dc_management_service(request: Request) -> DcManagementService:
    session = async_session_factory()
    audit = PgAuditAdapter(session)
    dc_repo = DcRepository(session)
    return DcManagementService(_dc_mgmt, _cache, audit, dc_repo)


def get_dfs_replication_service(request: Request) -> DfsReplicationService:
    session = async_session_factory()
    audit = PgAuditAdapter(session)
    dfs_repo = DfsReplicationRepository(session)
    return DfsReplicationService(_dfs_repl, _cache, audit, dfs_repo)


def get_pki_management_service(request: Request) -> PkiManagementService:
    session = async_session_factory()
    audit = PgAuditAdapter(session)
    pki_repo = PkiRepository(session)
    return PkiManagementService(_pki, _cache, audit, pki_repo)


def get_tier_security_service(request: Request) -> TierSecurityService:
    session = async_session_factory()
    audit = PgAuditAdapter(session)
    tier_repo = TierSecurityRepository(session)
    return TierSecurityService(_tier_sec, _cache, audit, tier_repo)


def get_hybrid_identity_service(request: Request) -> HybridIdentityService:
    session = async_session_factory()
    audit = PgAuditAdapter(session)
    hybrid_repo = HybridIdentityRepository(session)
    return HybridIdentityService(_entra_id, _cache, audit, hybrid_repo)


def get_monitoring_alert_service(request: Request) -> MonitoringAlertService:
    session = async_session_factory()
    audit = PgAuditAdapter(session)
    alert_repo = AlertRepository(session)
    return MonitoringAlertService(_zabbix, _veeam, _cache, audit, alert_repo)


def get_sdwan_integration_service(request: Request) -> SdwanIntegrationService:
    session = async_session_factory()
    audit = PgAuditAdapter(session)
    sdwan_repo = SdwanRepository(session)
    return SdwanIntegrationService(_sdwan, _cache, audit, sdwan_repo)


def get_secure_print_service(request: Request) -> SecurePrintService:
    session = async_session_factory()
    audit = PgAuditAdapter(session)
    job_repo = SecurePrintJobRepository(session)
    card_repo = CardMappingRepository(session)
    mfp_repo = MfpPrinterRepository(session)
    audit_repo = PrintAuditRepository(session)
    return SecurePrintService(_sp, _card, _print_audit, _ldap, _cache, audit, job_repo, card_repo, mfp_repo, audit_repo)


def get_remote_access_service(request: Request) -> RemoteAccessService:
    session = async_session_factory()
    gw_repo = VpnGatewayRepository(session)
    sess_repo = VpnSessionRepository(session)
    pol_repo = VpnPolicyRepository(session)
    dc_repo = DeviceClassificationRepository(session)
    raa_repo = RemoteAccessAuditRepository(session)
    return RemoteAccessService(
        vpn_gateway_repo=gw_repo,
        vpn_session_repo=sess_repo,
        vpn_policy_repo=pol_repo,
        device_classification_repo=dc_repo,
        remote_access_audit_repo=raa_repo,
        remote_access_provider=_ra,
        vpn_provider=_vpn,
        defender_provider=_defender,
    )


def get_identity_center_service(request: Request) -> IdentityCenterService:
    session = async_session_factory()
    return IdentityCenterService(
        lifecycle_repo=IdentityLifecycleEventRepository(session),
        onboarding_repo=HrOnboardingRequestRepository(session),
        offboarding_repo=HrOffboardingRequestRepository(session),
        transfer_repo=HrTransferRequestRepository(session),
        print_cost_repo=PrintCostAuditRepository(session),
        wifi_policy_repo=Wifi8021xPolicyRepository(session),
        autopilot_repo=AutopilotProfileRepository(session),
        ca_rule_repo=ConditionalAccessRuleRepository(session),
        saml_oidc_repo=SamlOidcApplicationRepository(session),
        identity_source_repo=IdentitySourcePolicyRepository(session),
    )