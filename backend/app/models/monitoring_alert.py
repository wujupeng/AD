from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Text, Integer, JSON, ARRAY, Boolean, CheckConstraint, Index
from datetime import datetime

from app.models.ad_objects import Base


class MonitoringAlert(Base):
    __tablename__ = "monitoring_alerts"

    alert_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    source_system: Mapped[str] = mapped_column(String(64), nullable=False)
    severity: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    affected_objects: Mapped[str | None] = mapped_column(ARRAY(String(256)))
    trigger_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    acknowledged: Mapped[bool] = mapped_column(Boolean, default=False)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    notification_channels: Mapped[str | None] = mapped_column(ARRAY(String(64)))

    __table_args__ = (
        Index("ix_alert_ack_unresolved", "acknowledged", postgresql_where=~resolved),
    )


class BackupJob(Base):
    __tablename__ = "backup_jobs"

    backup_job_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    job_name: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)
    backup_type: Mapped[str] = mapped_column(String(64), nullable=False)
    last_execution_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_execution_status: Mapped[str] = mapped_column(String(32), default="unknown")
    retention_policy: Mapped[str] = mapped_column(String(32), default="30d")
    offsite_replication: Mapped[str] = mapped_column(String(32), default="none")
    recovery_points: Mapped[dict | None] = mapped_column(JSON)


class AlertNotificationConfig(Base):
    __tablename__ = "alert_notification_configs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    severity: Mapped[str] = mapped_column(String(32), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    recipient_groups: Mapped[str | None] = mapped_column(ARRAY(String(256)))
    channels: Mapped[str] = mapped_column(ARRAY(String(64)), nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    __table_args__ = (
        Index("ix_alert_notif_sev_cat", "severity", "category", unique=True),
    )