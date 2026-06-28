from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Float, JSON, CheckConstraint, Index
from datetime import datetime

from app.models.ad_objects import Base


class SdwanLink(Base):
    __tablename__ = "sdwan_links"

    link_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    source_site: Mapped[str] = mapped_column(String(64), nullable=False)
    target_site: Mapped[str] = mapped_column(String(64), nullable=False)
    bandwidth_mbps: Mapped[float | None] = mapped_column(Float)
    latency_ms: Mapped[float | None] = mapped_column(Float)
    packet_loss_percent: Mapped[float | None] = mapped_column(Float)
    link_status: Mapped[str] = mapped_column(String(32), default="unknown")
    qos_policies: Mapped[dict | None] = mapped_column(JSON)

    __table_args__ = (
        Index("ix_sdwan_source_target", "source_site", "target_site", unique=True),
    )