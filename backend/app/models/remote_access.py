from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Integer, Float, Text, JSON, ARRAY, BigInteger, CheckConstraint, ForeignKey, UniqueConstraint
from datetime import datetime
import uuid

from app.models.ad_objects import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class VpnGateway(Base):
    __tablename__ = "vpn_gateways"

    gateway_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    gateway_name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    gateway_site: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    gateway_ip: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    gateway_role: Mapped[str] = mapped_column(String(16), nullable=False)
    tunnel_protocol: Mapped[str] = mapped_column(String(32), nullable=False)
    max_concurrent_sessions: Mapped[int] = mapped_column(Integer, default=500)
    active_sessions: Mapped[int] = mapped_column(Integer, default=0)
    cpu_usage_percent: Mapped[float] = mapped_column(Float, default=0)
    bandwidth_usage_mbps: Mapped[float] = mapped_column(Float, default=0)
    health_status: Mapped[str] = mapped_column(String(16), default="unknown", index=True)
    served_sites: Mapped[str | None] = mapped_column(ARRAY(String(64)))
    last_health_check: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint("gateway_role IN ('primary','secondary')", name="ck_vpngw_role"),
        CheckConstraint("tunnel_protocol IN ('IKEv2','SSTP','IKEv2_SSTP_Fallback')", name="ck_vpngw_protocol"),
        CheckConstraint("health_status IN ('online','offline','degraded','unknown')", name="ck_vpngw_health"),
    )


class VpnSession(Base):
    __tablename__ = "vpn_sessions"

    session_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_account: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    user_sid: Mapped[str | None] = mapped_column(String(128))
    device_hostname: Mapped[str | None] = mapped_column(String(128))
    user_site: Mapped[str | None] = mapped_column(String(64), index=True)
    tunnel_type: Mapped[str] = mapped_column(String(16), nullable=False)
    connected_gateway_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("vpn_gateways.gateway_id"), index=True)
    connection_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    disconnection_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    client_ip: Mapped[str | None] = mapped_column(String(64))
    assigned_ip: Mapped[str | None] = mapped_column(String(64))
    auth_method: Mapped[str | None] = mapped_column(String(32))
    is_active: Mapped[bool] = mapped_column(default=True, index=True)
    bytes_in: Mapped[int] = mapped_column(BigInteger, default=0)
    bytes_out: Mapped[int] = mapped_column(BigInteger, default=0)

    __table_args__ = (
        CheckConstraint("tunnel_type IN ('device_tunnel','user_tunnel','dual_tunnel')", name="ck_vpnsess_tunnel"),
        CheckConstraint("auth_method IN ('certificate','kerberos','entra_id_mfa','cached_credential')", name="ck_vpnsess_auth"),
    )


class VpnPolicy(Base):
    __tablename__ = "vpn_policies"

    policy_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    policy_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    policy_name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    policy_config: Mapped[dict | None] = mapped_column(JSON)
    target_ou_dns: Mapped[str | None] = mapped_column(ARRAY(String(256)))
    is_enabled: Mapped[bool] = mapped_column(default=True, index=True)

    __table_args__ = (
        CheckConstraint("policy_type IN ('device_tunnel','user_tunnel','gateway_selection','cached_credentials')", name="ck_vpn_pol_type"),
    )


class DeviceClassification(Base):
    __tablename__ = "device_classifications"

    classification_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    device_class: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(128), nullable=False)
    auth_methods: Mapped[str | None] = mapped_column(ARRAY(String(32)))
    vpn_tunnel_type: Mapped[str | None] = mapped_column(String(16))
    cached_logon_count: Mapped[int] = mapped_column(Integer, default=10)
    conditional_access_level: Mapped[str] = mapped_column(String(16), default="standard")
    bitlocker_required: Mapped[bool] = mapped_column(default=True)
    defender_required: Mapped[bool] = mapped_column(default=True)
    target_ou_dn: Mapped[str | None] = mapped_column(String(256))

    __table_args__ = (
        CheckConstraint("device_class IN ('enterprise_laptop','enterprise_desktop','byod','kiosk')", name="ck_devclass_class"),
        CheckConstraint("vpn_tunnel_type IN ('device_and_user','user_only','device_only','none')", name="ck_devclass_tunnel"),
        CheckConstraint("conditional_access_level IN ('standard','enhanced','strict')", name="ck_devclass_ca"),
    )


class RemoteAccessAuditLog(Base):
    __tablename__ = "remote_access_audit_logs"

    log_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    event_type: Mapped[str] = mapped_column(String(48), nullable=False, index=True)
    user_account: Mapped[str | None] = mapped_column(String(128), index=True)
    device_hostname: Mapped[str | None] = mapped_column(String(128))
    source_site: Mapped[str | None] = mapped_column(String(64), index=True)
    vpn_gateway_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("vpn_gateways.gateway_id"), index=True)
    tunnel_type: Mapped[str | None] = mapped_column(String(16))
    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    details: Mapped[dict | None] = mapped_column(JSON)

    __table_args__ = (
        CheckConstraint(
            "event_type IN ("
            "'vpn_connected','vpn_disconnected','kerberos_recovered','kerberos_recovery_failed',"
            "'ntlm_fallback','password_synced','gpo_remote_updated','tunnel_failed',"
            "'gateway_failover','dc_isolation_triggered','cached_cred_used',"
            "'hybrid_join_registered','conditional_access_evaluated',"
            "'bitlocker_remote_operation','defender_alert'"
            ")",
            name="ck_raa_event",
        ),
    )