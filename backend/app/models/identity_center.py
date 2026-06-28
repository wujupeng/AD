from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Integer, Float, Text, JSON, ARRAY, BigInteger, Boolean, CheckConstraint, ForeignKey, UniqueConstraint
from datetime import datetime
import uuid

from app.models.ad_objects import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class IdentityLifecycleEvent(Base):
    __tablename__ = "identity_lifecycle_events"

    event_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    ad_account: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    ad_sid: Mapped[str | None] = mapped_column(String(64))
    trigger_source: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    request_id: Mapped[str | None] = mapped_column(String(36), index=True)
    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    old_value: Mapped[str | None] = mapped_column(String(512))
    new_value: Mapped[str | None] = mapped_column(String(512))
    affected_systems: Mapped[str | None] = mapped_column(ARRAY(String(64)), default=list)
    details: Mapped[dict | None] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint(
            "event_type IN ("
            "'onboarding_started','onboarding_completed','onboarding_partial_failed',"
            "'offboarding_started','offboarding_completed','offboarding_partial_failed',"
            "'transfer_started','transfer_completed','transfer_partial_failed',"
            "'card_authenticated','card_deactivated','card_replaced',"
            "'print_convergence_auth','wifi_8021x_auth','autopilot_deployed',"
            "'conditional_access_evaluated','identity_source_violation',"
            "'entra_cloud_only_detected','group_membership_changed',"
            "'permission_changed','role_changed'"
            ")",
            name="ck_ile_event",
        ),
        CheckConstraint("trigger_source IN ('hr_system','admin_manual','system_auto','card_auth')", name="ck_ile_trigger"),
    )


class HrOnboardingRequest(Base):
    __tablename__ = "hr_onboarding_requests"

    request_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    employee_name: Mapped[str] = mapped_column(String(128), nullable=False)
    employee_name_en: Mapped[str | None] = mapped_column(String(128))
    department: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    position: Mapped[str] = mapped_column(String(128), nullable=False)
    site: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    sam_account_name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    card_id: Mapped[str | None] = mapped_column(String(128))
    card_type: Mapped[str | None] = mapped_column(String(32))
    device_type: Mapped[str | None] = mapped_column(String(32))
    erp_role: Mapped[str | None] = mapped_column(String(64))
    mes_permission: Mapped[str | None] = mapped_column(String(64))
    plm_permission: Mapped[str | None] = mapped_column(String(64))
    gitlab_role: Mapped[str | None] = mapped_column(String(64))
    manager_account: Mapped[str | None] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(String(32), default="pending", index=True)
    step_results: Mapped[dict | None] = mapped_column(JSON, default=dict)
    trigger_source: Mapped[str] = mapped_column(String(32), default="hr_system")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    estimated_completion_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint("status IN ('pending','in_progress','completed','partial_failed','failed')", name="ck_onboard_status"),
        CheckConstraint("card_type IN ('ic_card','nfc_mifare','nfc_hid','employee_badge')", name="ck_onboard_card"),
        CheckConstraint("device_type IN ('enterprise_laptop','enterprise_desktop','kiosk')", name="ck_onboard_device"),
        CheckConstraint("trigger_source IN ('hr_system','admin_manual')", name="ck_onboard_trigger"),
    )


class HrOffboardingRequest(Base):
    __tablename__ = "hr_offboarding_requests"

    request_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    ad_account: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    offboarding_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    mailbox_retention_days: Mapped[int] = mapped_column(Integer, default=30)
    mailbox_forward_to: Mapped[str | None] = mapped_column(String(128))
    wipe_device: Mapped[bool] = mapped_column(Boolean, default=True)
    revoke_all_access: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[str] = mapped_column(String(32), default="pending", index=True)
    step_results: Mapped[dict | None] = mapped_column(JSON, default=dict)
    trigger_source: Mapped[str] = mapped_column(String(32), default="hr_system")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    estimated_completion_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint("status IN ('pending','in_progress','completed','partial_failed','failed')", name="ck_offboard_status"),
        CheckConstraint("trigger_source IN ('hr_system','admin_manual')", name="ck_offboard_trigger"),
    )


class HrTransferRequest(Base):
    __tablename__ = "hr_transfer_requests"

    request_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    ad_account: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    old_department: Mapped[str] = mapped_column(String(64), nullable=False)
    new_department: Mapped[str] = mapped_column(String(64), nullable=False)
    old_site: Mapped[str] = mapped_column(String(64), nullable=False)
    new_site: Mapped[str] = mapped_column(String(64), nullable=False)
    new_position: Mapped[str | None] = mapped_column(String(128))
    new_erp_role: Mapped[str | None] = mapped_column(String(64))
    new_mes_permission: Mapped[str | None] = mapped_column(String(64))
    new_plm_permission: Mapped[str | None] = mapped_column(String(64))
    new_gitlab_role: Mapped[str | None] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32), default="pending", index=True)
    step_results: Mapped[dict | None] = mapped_column(JSON, default=dict)
    trigger_source: Mapped[str] = mapped_column(String(32), default="hr_system")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    estimated_completion_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint("status IN ('pending','in_progress','completed','partial_failed','failed')", name="ck_transfer_status"),
        CheckConstraint("trigger_source IN ('hr_system','admin_manual')", name="ck_transfer_trigger"),
    )


class PrintCostAuditRecord(Base):
    __tablename__ = "print_cost_audit_records"

    cost_audit_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    job_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("secure_print_jobs.job_id"), index=True)
    owner_account: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    owner_sid: Mapped[str | None] = mapped_column(String(64))
    department: Mapped[str | None] = mapped_column(String(128), index=True)
    operation_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    country: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    factory: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    printer_name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    page_count: Mapped[int] = mapped_column(Integer, default=0)
    duplex_mode: Mapped[str | None] = mapped_column(String(16))
    color_mode: Mapped[str | None] = mapped_column(String(16))
    paper_size: Mapped[str] = mapped_column(String(16), default="A4")
    estimated_cost: Mapped[float] = mapped_column(Float, default=0)
    cost_currency: Mapped[str] = mapped_column(String(8), default="CNY")
    cost_per_page: Mapped[float] = mapped_column(Float, default=0)
    auth_method: Mapped[str | None] = mapped_column(String(16))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("duplex_mode IN ('simplex','duplex_long','duplex_short')", name="ck_pcar_duplex"),
        CheckConstraint("color_mode IN ('color','grayscale')", name="ck_pcar_color"),
        CheckConstraint("paper_size IN ('A4','A3','Letter','Legal')", name="ck_pcar_paper"),
        CheckConstraint("cost_currency IN ('CNY','USD','EUR','HUF','VND','MXN')", name="ck_pcar_currency"),
        CheckConstraint("auth_method IN ('card','nfc','pin','qrcode','system')", name="ck_pcar_auth"),
    )


class Wifi8021xPolicy(Base):
    __tablename__ = "wifi_8021x_policies"

    policy_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    policy_name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    ssid: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    auth_method: Mapped[str] = mapped_column(String(32), default="EAP_TLS")
    certificate_template: Mapped[str] = mapped_column(String(128), nullable=False)
    required_group: Mapped[str] = mapped_column(String(128), nullable=False)
    nps_server: Mapped[str] = mapped_column(String(256), nullable=False)
    nps_port: Mapped[int] = mapped_column(Integer, default=1812)
    target_ou_dns: Mapped[str | None] = mapped_column(ARRAY(String(256)), default=list)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("auth_method IN ('EAP_TLS','PEAP_MSCHAPv2')", name="ck_wifi_auth"),
    )


class AutopilotProfile(Base):
    __tablename__ = "autopilot_profiles"

    profile_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    profile_name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    target_ou_dn: Mapped[str] = mapped_column(String(512), nullable=False)
    domain_join_type: Mapped[str] = mapped_column(String(32), default="HybridAzureAD", index=True)
    intune_compliance_policy: Mapped[str] = mapped_column(String(128), nullable=False)
    vpn_profile: Mapped[str | None] = mapped_column(String(128))
    wifi_profile: Mapped[str | None] = mapped_column(String(128))
    app_list: Mapped[str | None] = mapped_column(ARRAY(String(128)), default=list)
    device_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("domain_join_type IN ('HybridAzureAD','AzureAD')", name="ck_autopilot_join"),
        CheckConstraint("device_type IN ('enterprise_laptop','enterprise_desktop','kiosk')", name="ck_autopilot_device"),
    )


class ConditionalAccessRule(Base):
    __tablename__ = "conditional_access_rules"

    rule_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    rule_name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    conditions: Mapped[dict | None] = mapped_column(JSON, default=dict)
    controls: Mapped[dict | None] = mapped_column(JSON, default=dict)
    target_resources: Mapped[str | None] = mapped_column(ARRAY(String(128)), default=list)
    priority: Mapped[int] = mapped_column(Integer, default=100, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class SamlOidcApplication(Base):
    __tablename__ = "saml_oidc_applications"

    app_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    app_name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    protocol: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(16), default="active", index=True)
    entity_id: Mapped[str | None] = mapped_column(String(512))
    client_id: Mapped[str | None] = mapped_column(String(256))
    client_secret_hash: Mapped[str | None] = mapped_column(String(256))
    redirect_uris: Mapped[str | None] = mapped_column(ARRAY(String(512)), default=list)
    acs_url: Mapped[str | None] = mapped_column(String(512))
    slo_url: Mapped[str | None] = mapped_column(String(512))
    sp_metadata: Mapped[dict | None] = mapped_column(JSON)
    allowed_groups: Mapped[str | None] = mapped_column(ARRAY(String(128)), default=list)
    last_auth_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    total_users: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("protocol IN ('SAML_2_0','OIDC')", name="ck_app_protocol"),
        CheckConstraint("status IN ('active','inactive','error')", name="ck_app_status"),
    )


class IdentitySourcePolicy(Base):
    __tablename__ = "identity_source_policies"

    policy_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    policy_name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    primary_source: Mapped[str] = mapped_column(String(32), default="ActiveDirectory")
    internet_extension: Mapped[str] = mapped_column(String(32), default="EntraID")
    allow_cloud_only_users: Mapped[bool] = mapped_column(Boolean, default=False)
    sync_failure_threshold_hours: Mapped[int] = mapped_column(Integer, default=24)
    downstream_systems: Mapped[str | None] = mapped_column(ARRAY(String(64)), default=list)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("primary_source IN ('ActiveDirectory')", name="ck_isp_source"),
        CheckConstraint("internet_extension IN ('EntraID','None')", name="ck_isp_extension"),
    )