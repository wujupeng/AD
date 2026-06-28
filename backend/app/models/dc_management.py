from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Text, Boolean, Integer, BigInteger, JSON, Index, ARRAY, SmallInteger
from datetime import datetime

from app.models.ad_objects import Base


class DcRegistry(Base):
    __tablename__ = "dc_registries"

    dc_hostname: Mapped[str] = mapped_column(String(256), primary_key=True)
    dc_site: Mapped[str] = mapped_column(String(64), index=True)
    dc_ip_address: Mapped[str] = mapped_column(String(64), nullable=False)
    is_gc: Mapped[bool] = mapped_column(Boolean, default=True)
    is_dns_integrated: Mapped[bool] = mapped_column(Boolean, default=True)
    fsmo_roles: Mapped[str | None] = mapped_column(ARRAY(String(64)))
    health_status: Mapped[str] = mapped_column(String(32), default="unknown", index=True)
    os_version: Mapped[str | None] = mapped_column(String(128))
    config_baseline: Mapped[dict | None] = mapped_column(JSON)
    last_health_check: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class DcReplicationLink(Base):
    __tablename__ = "dc_replication_links"

    link_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    source_dc: Mapped[str] = mapped_column(String(256), nullable=False)
    target_dc: Mapped[str] = mapped_column(String(256), nullable=False)
    source_site: Mapped[str] = mapped_column(String(64))
    target_site: Mapped[str] = mapped_column(String(64))
    replication_delay_seconds: Mapped[int | None] = mapped_column(Integer)
    last_success_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    consecutive_failures: Mapped[int] = mapped_column(Integer, default=0)
    link_status: Mapped[str] = mapped_column(String(32), default="unknown")

    __table_args__ = (
        Index("ix_dc_repl_source_target", "source_dc", "target_dc", unique=True),
    )