from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Boolean, Integer, JSON, CheckConstraint
from datetime import datetime

from app.models.ad_objects import Base


class CloudPhaseConfig(Base):
    __tablename__ = "cloud_phase_configs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    current_phase: Mapped[str] = mapped_column(String(16), nullable=False, default="Phase1")
    phase_transition_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    entra_id_sync_status: Mapped[str | None] = mapped_column(String(32))
    intune_compliance_status: Mapped[str | None] = mapped_column(String(32))

    __table_args__ = (
        CheckConstraint("current_phase IN ('Phase1', 'Phase2', 'Phase3')", name="ck_cloud_phase"),
    )