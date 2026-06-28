from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Integer, Text, BigInteger, Boolean, Index, CheckConstraint
from datetime import datetime

from app.models.ad_objects import Base


class PrintTask(Base):
    __tablename__ = "print_tasks"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    task_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    user_sid: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(128), nullable=False)
    printer_name: Mapped[str] = mapped_column(String(256), nullable=False)
    printer_site: Mapped[str | None] = mapped_column(String(64), index=True)
    document_name: Mapped[str | None] = mapped_column(String(512))
    pages: Mapped[int] = mapped_column(Integer, default=0)
    copies: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(32), default="pending", index=True)
    error_message: Mapped[str | None] = mapped_column(Text)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class PrintQuota(Base):
    __tablename__ = "print_quotas"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_sid: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    month: Mapped[str] = mapped_column(String(7), nullable=False, index=True)
    pages_used: Mapped[int] = mapped_column(Integer, default=0)
    pages_limit: Mapped[int] = mapped_column(Integer, default=500)
    site_code: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_print_quotas_user_month", "user_sid", "month"),
    )


class Printer(Base):
    __tablename__ = "printers"

    printer_name: Mapped[str] = mapped_column(String(256), primary_key=True)
    site: Mapped[str] = mapped_column(String(64), index=True)
    printer_type: Mapped[str] = mapped_column(String(32), default="mfp")
    server_name: Mapped[str | None] = mapped_column(String(256))
    ad_object_dn: Mapped[str | None] = mapped_column(String(512))
    gpo_deployed: Mapped[bool] = mapped_column(Boolean, default=False)
    gpo_name: Mapped[str | None] = mapped_column(String(256))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)