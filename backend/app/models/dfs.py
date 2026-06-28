from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, BigInteger, Text
from datetime import datetime

from app.models.ad_objects import Base


class DfsAccessLog(Base):
    __tablename__ = "dfs_access_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_sid: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(128), nullable=False)
    dfs_path: Mapped[str] = mapped_column(String(1024), nullable=False, index=True)
    resolved_target: Mapped[str | None] = mapped_column(String(512))
    operation: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    result: Mapped[str] = mapped_column(String(16), nullable=False)
    site_code: Mapped[str | None] = mapped_column(String(64), index=True)
    client_ip: Mapped[str | None] = mapped_column(String(64))
    file_size: Mapped[int | None] = mapped_column(BigInteger)
    error_message: Mapped[str | None] = mapped_column(Text)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)