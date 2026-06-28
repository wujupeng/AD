from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Integer, Float, ARRAY, JSON, CheckConstraint, Index
from datetime import datetime

from app.models.ad_objects import Base


class DfsReplicationLink(Base):
    __tablename__ = "dfs_replication_links"

    link_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    source_site: Mapped[str] = mapped_column(String(64), nullable=False)
    target_site: Mapped[str] = mapped_column(String(64), nullable=False)
    replicated_folders: Mapped[str | None] = mapped_column(ARRAY(String(256)))
    backlog_count: Mapped[int] = mapped_column(Integer, default=0)
    last_sync_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    sync_latency_seconds: Mapped[int | None] = mapped_column(Integer)
    bandwidth_usage_mbps: Mapped[float | None] = mapped_column(Float)
    link_status: Mapped[str] = mapped_column(String(32), default="unknown")

    __table_args__ = (
        Index("ix_dfsr_source_target", "source_site", "target_site", unique=True),
    )


class DfsConflictFile(Base):
    __tablename__ = "dfs_conflict_files"

    conflict_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    file_name: Mapped[str] = mapped_column(String(512), nullable=False)
    dfs_path: Mapped[str | None] = mapped_column(String(1024))
    source_site: Mapped[str] = mapped_column(String(64))
    target_site: Mapped[str] = mapped_column(String(64))
    conflict_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    resolution_status: Mapped[str] = mapped_column(String(32), default="pending", index=True)
    resolved_version_path: Mapped[str | None] = mapped_column(String(1024))
    conflict_version_path: Mapped[str | None] = mapped_column(String(1024))