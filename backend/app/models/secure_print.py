from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Integer, Boolean, Text, ForeignKey, CheckConstraint, Index
from datetime import datetime

from app.models.ad_objects import Base


class SecurePrintJob(Base):
    __tablename__ = "secure_print_jobs"

    job_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    owner_account: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    owner_sid: Mapped[str | None] = mapped_column(String(128), index=True)
    document_name: Mapped[str | None] = mapped_column(String(512))
    pages: Mapped[int] = mapped_column(Integer, default=0)
    copies: Mapped[int] = mapped_column(Integer, default=1)
    color_mode: Mapped[str] = mapped_column(String(16), default="color")
    duplex: Mapped[bool] = mapped_column(Boolean, default=True)
    job_status: Mapped[str] = mapped_column(String(32), default="queued", index=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    released_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    released_by: Mapped[str | None] = mapped_column(String(128))
    released_printer: Mapped[str | None] = mapped_column(String(256))
    released_site: Mapped[str | None] = mapped_column(String(64))
    print_cluster_job_id: Mapped[str | None] = mapped_column(String(128))
    client_ip: Mapped[str | None] = mapped_column(String(64))
    client_site: Mapped[str | None] = mapped_column(String(64))


class CardAccountMapping(Base):
    __tablename__ = "card_account_mappings"

    card_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    card_type: Mapped[str] = mapped_column(String(32), default="mifare")
    ad_account: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ix_card_active", "is_active", postgresql_where=True),
    )


class MfpPrinter(Base):
    __tablename__ = "mfp_printers"

    printer_name: Mapped[str] = mapped_column(String(256), primary_key=True)
    site: Mapped[str] = mapped_column(String(64), index=True)
    ip_address: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    printer_brand: Mapped[str] = mapped_column(String(64), default="generic")
    auth_protocols: Mapped[str | None] = mapped_column(String(256))
    card_reader_type: Mapped[str | None] = mapped_column(String(64))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    last_heartbeat: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class PrintAuditRecord(Base):
    __tablename__ = "print_audit_records"

    audit_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    operation_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    job_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("secure_print_jobs.job_id"), index=True)
    user_account: Mapped[str | None] = mapped_column(String(128), index=True)
    user_sid: Mapped[str | None] = mapped_column(String(128))
    printer_name: Mapped[str | None] = mapped_column(String(256))
    site: Mapped[str | None] = mapped_column(String(64), index=True)
    page_count: Mapped[int] = mapped_column(Integer, default=0)
    color_mode: Mapped[str | None] = mapped_column(String(16))
    duplex: Mapped[bool | None] = mapped_column(Boolean)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    details: Mapped[str | None] = mapped_column(Text)