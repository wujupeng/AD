from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Integer, Boolean, ForeignKey, CheckConstraint, Index
from datetime import datetime

from app.models.ad_objects import Base


class PkiCertificateTemplate(Base):
    __tablename__ = "pki_certificate_templates"

    template_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    usage_scenario: Mapped[str] = mapped_column(String(64), nullable=False)
    template_oid: Mapped[str | None] = mapped_column(String(128))
    key_length: Mapped[int] = mapped_column(Integer, default=2048)
    validity_period_days: Mapped[int] = mapped_column(Integer, default=365)
    auto_enrollment: Mapped[bool] = mapped_column(Boolean, default=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    description: Mapped[str | None] = mapped_column(String(512))


class PkiCertificate(Base):
    __tablename__ = "pki_certificates"

    certificate_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    template_name: Mapped[str] = mapped_column(String(128), ForeignKey("pki_certificate_templates.template_name"), index=True)
    subject_name: Mapped[str] = mapped_column(String(512), nullable=False)
    issuer_name: Mapped[str] = mapped_column(String(512))
    serial_number: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    not_before: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    not_after: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    usage_scenario: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32), default="active", index=True)
    requester_sid: Mapped[str | None] = mapped_column(String(128), index=True)
    auto_enrollment: Mapped[bool] = mapped_column(Boolean, default=False)
    revocation_reason: Mapped[str | None] = mapped_column(String(128))
    thumbprint: Mapped[str | None] = mapped_column(String(128))


class PkiScepPolicy(Base):
    __tablename__ = "pki_scep_policies"

    policy_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    policy_name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    template_name: Mapped[str] = mapped_column(String(128), ForeignKey("pki_certificate_templates.template_name"))
    target_ou_dn: Mapped[str | None] = mapped_column(String(512))
    ndes_url: Mapped[str | None] = mapped_column(String(512))
    challenge_type: Mapped[str | None] = mapped_column(String(64))
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)