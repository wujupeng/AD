import asyncio
from app.models.ad_objects import Base, AdOu, AdUser, AdGroup, AdGroupMember
from app.models.audit import AuditEvent
from app.models.auth import AuthSession
from app.models.print import PrintTask, PrintQuota, Printer
from app.models.dfs import DfsAccessLog
from app.models.integration import IntegrationConfig
from app.models.report import ComplianceReport
from app.models.site import SiteConfig
from app.models.dc_management import DcRegistry, DcReplicationLink
from app.models.dfs_replication import DfsReplicationLink, DfsConflictFile
from app.models.tier_security import TierDefinition, ComputerSecurityBaseline
from app.models.hybrid_identity import CloudPhaseConfig
from app.models.pki_management import PkiCertificateTemplate, PkiCertificate, PkiScepPolicy
from app.models.monitoring_alert import MonitoringAlert, BackupJob, AlertNotificationConfig
from app.models.sdwan_integration import SdwanLink
from app.models.secure_print import SecurePrintJob, CardAccountMapping, MfpPrinter, PrintAuditRecord
from app.models.remote_access import VpnGateway, VpnSession, VpnPolicy, DeviceClassification, RemoteAccessAuditLog
from app.models.identity_center import (IdentityLifecycleEvent, HrOnboardingRequest, HrOffboardingRequest,
    HrTransferRequest, PrintCostAuditRecord, Wifi8021xPolicy, AutopilotProfile,
    ConditionalAccessRule, SamlOidcApplication, IdentitySourcePolicy)
from app.models.settings import CachedLogonPolicy, EntraHybridJoinConfig, DcIsolationPolicy, LdapDirectoryConfig, ExternalIntegrationConfig
from app.core.database import engine


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created successfully!")


if __name__ == "__main__":
    asyncio.run(init_db())