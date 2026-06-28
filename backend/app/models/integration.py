from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Text, Boolean, JSON
from datetime import datetime

from app.models.ad_objects import Base


class IntegrationConfig(Base):
    __tablename__ = "integration_configs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sp_name: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)
    sp_type: Mapped[str] = mapped_column(String(32), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(512), nullable=False)
    acs_url: Mapped[str | None] = mapped_column(String(512))
    slo_url: Mapped[str | None] = mapped_column(String(512))
    client_id: Mapped[str | None] = mapped_column(String(256))
    client_secret_encrypted: Mapped[str | None] = mapped_column(Text)
    redirect_uris: Mapped[str | None] = mapped_column(Text)
    certificate: Mapped[str | None] = mapped_column(Text)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    extra_config: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class AttributeMapping(Base):
    __tablename__ = "attribute_mappings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sp_name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    ad_attribute: Mapped[str] = mapped_column(String(128), nullable=False)
    claim_name: Mapped[str] = mapped_column(String(128), nullable=False)
    claim_format: Mapped[str | None] = mapped_column(String(32))
    is_required: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class RoleMapping(Base):
    __tablename__ = "role_mappings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sp_name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    ad_group_dn: Mapped[str] = mapped_column(String(512), nullable=False)
    app_role: Mapped[str] = mapped_column(String(128), nullable=False)
    priority: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)