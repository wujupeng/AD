from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Text, Boolean, Integer, BigInteger, JSON, ARRAY, SmallInteger, CheckConstraint
from datetime import datetime

from app.models.ad_objects import Base


class TierDefinition(Base):
    __tablename__ = "tier_definitions"

    tier_level: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    tier_name: Mapped[str] = mapped_column(String(64), nullable=False)
    server_list: Mapped[str | None] = mapped_column(ARRAY(String(256)))
    admin_groups: Mapped[str | None] = mapped_column(ARRAY(String(256)))
    login_restriction: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (
        CheckConstraint("tier_level IN (0, 1, 2)", name="ck_tier_level"),
    )


class ComputerSecurityBaseline(Base):
    __tablename__ = "computer_security_baselines"

    computer_name: Mapped[str] = mapped_column(String(256), primary_key=True)
    site: Mapped[str | None] = mapped_column(String(64), index=True)
    laps_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    laps_password_expiry: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    credential_guard_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    bitlocker_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    bitlocker_recovery_key_stored: Mapped[bool] = mapped_column(Boolean, default=False)
    defender_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    smartscreen_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    applocker_policy_applied: Mapped[bool] = mapped_column(Boolean, default=False)
    wdac_policy_applied: Mapped[bool] = mapped_column(Boolean, default=False)
    compliance_status: Mapped[str] = mapped_column(String(32), default="unknown", index=True)