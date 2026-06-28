from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Integer, Text, JSON, ARRAY
from datetime import datetime

from app.models.ad_objects import Base


class SiteConfig(Base):
    __tablename__ = "site_configs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    site_code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    site_name: Mapped[str] = mapped_column(String(256), nullable=False)
    region: Mapped[str | None] = mapped_column(String(64), index=True)
    country: Mapped[str | None] = mapped_column(String(64))
    subnet_ranges: Mapped[str] = mapped_column(Text, nullable=False)
    dc_priority_list: Mapped[dict] = mapped_column(JSON, nullable=False)
    timezone: Mapped[str] = mapped_column(String(64), default="Asia/Shanghai")
    language: Mapped[str] = mapped_column(String(16), default="zh-CN")
    is_active: Mapped[bool] = mapped_column(default=True, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    dfs_servers: Mapped[str | None] = mapped_column(ARRAY(String(256)))
    print_servers: Mapped[str | None] = mapped_column(ARRAY(String(256)))
    vpn_gateway: Mapped[str | None] = mapped_column(String(128))
    site_display_name: Mapped[str | None] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)