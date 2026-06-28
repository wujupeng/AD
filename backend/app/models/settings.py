from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Integer, Boolean, JSON, CheckConstraint, Text
from datetime import datetime
import uuid

from app.models.ad_objects import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class CachedLogonPolicy(Base):
    __tablename__ = "cached_logon_policies"

    policy_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    policy_name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    policy_config: Mapped[dict] = mapped_column(JSON, nullable=False, default=lambda: {
        "enterprise_laptop": 100,
        "enterprise_desktop": 10,
        "byod": 0,
        "kiosk": 0,
    })
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class EntraHybridJoinConfig(Base):
    __tablename__ = "entra_hybrid_join_configs"

    config_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    status: Mapped[str] = mapped_column(String(32), default="not_configured", index=True)
    total_devices: Mapped[int] = mapped_column(Integer, default=0)
    registered: Mapped[int] = mapped_column(Integer, default=0)
    pending: Mapped[int] = mapped_column(Integer, default=0)
    failed: Mapped[int] = mapped_column(Integer, default=0)
    message: Mapped[str] = mapped_column(String(512), default="Entra Hybrid Join requires Phase2+")
    entra_connect_server: Mapped[str | None] = mapped_column(String(512))
    sync_scope: Mapped[str | None] = mapped_column(String(256))
    device_registration_policy: Mapped[str | None] = mapped_column(String(256))
    last_sync_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("status IN ('not_configured','configuring','configured','error')", name="ck_ehjc_status"),
    )


class DcIsolationPolicy(Base):
    __tablename__ = "dc_isolation_policies"

    policy_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    isolation_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    rules: Mapped[dict | None] = mapped_column(JSON, default=list)
    message: Mapped[str] = mapped_column(String(512), default="DC isolation policy requires firewall/ACL configuration")
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class LdapDirectoryConfig(Base):
    __tablename__ = "ldap_directory_configs"

    config_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    config_name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    server_url: Mapped[str] = mapped_column(String(512), nullable=False)
    base_dn: Mapped[str] = mapped_column(String(512), nullable=False)
    bind_dn: Mapped[str | None] = mapped_column(String(512))
    bind_password_encrypted: Mapped[str | None] = mapped_column(Text)
    search_filter: Mapped[str | None] = mapped_column(String(512))
    connection_test_status: Mapped[str] = mapped_column(String(32), default="not_tested")
    connection_test_error: Mapped[str | None] = mapped_column(String(512))
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("connection_test_status IN ('success','failed','not_tested')", name="ck_ldc_test"),
    )


class ExternalIntegrationConfig(Base):
    __tablename__ = "external_integration_configs"

    integration_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    integration_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    integration_name: Mapped[str] = mapped_column(String(128), nullable=False)
    server_url: Mapped[str | None] = mapped_column(String(512))
    api_key_encrypted: Mapped[str | None] = mapped_column(Text)
    connection_status: Mapped[str] = mapped_column(String(32), default="not_tested")
    connection_test_error: Mapped[str | None] = mapped_column(String(512))
    extra_config: Mapped[dict | None] = mapped_column(JSON)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("integration_type IN ('zabbix','veeam','sdwan','entra_id','print_cluster')", name="ck_eic_type"),
        CheckConstraint("connection_status IN ('connected','error','not_tested')", name="ck_eic_status"),
    )