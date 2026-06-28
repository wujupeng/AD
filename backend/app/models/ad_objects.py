from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, DateTime, Text, Boolean, Integer, BigInteger, JSON, Index
from datetime import datetime


class Base(DeclarativeBase):
    pass


class AdOu(Base):
    __tablename__ = "ad_ous"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    dn: Mapped[str] = mapped_column(String(512), unique=True, nullable=False, index=True)
    ou_name: Mapped[str] = mapped_column(String(256), nullable=False)
    parent_dn: Mapped[str | None] = mapped_column(String(512), index=True)
    site_code: Mapped[str | None] = mapped_column(String(64), index=True)
    description: Mapped[str | None] = mapped_column(Text)
    ad_guid: Mapped[str | None] = mapped_column(String(64), unique=True)
    usn_changed: Mapped[int] = mapped_column(BigInteger, default=0)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class AdUser(Base):
    __tablename__ = "ad_users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    sid: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    dn: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    display_name: Mapped[str | None] = mapped_column(String(256))
    email: Mapped[str | None] = mapped_column(String(256), index=True)
    telephone: Mapped[str | None] = mapped_column(String(64))
    department: Mapped[str | None] = mapped_column(String(256), index=True)
    title: Mapped[str | None] = mapped_column(String(256))
    office: Mapped[str | None] = mapped_column(String(256))
    company: Mapped[str | None] = mapped_column(String(256))
    ou_dn: Mapped[str | None] = mapped_column(String(512), index=True)
    site_code: Mapped[str | None] = mapped_column(String(64), index=True)
    user_account_control: Mapped[int] = mapped_column(Integer, default=512)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False)
    password_expired: Mapped[bool] = mapped_column(Boolean, default=False)
    last_logon: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ad_guid: Mapped[str | None] = mapped_column(String(64), unique=True)
    usn_changed: Mapped[int] = mapped_column(BigInteger, default=0)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class AdGroup(Base):
    __tablename__ = "ad_groups"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    dn: Mapped[str] = mapped_column(String(512), unique=True, nullable=False, index=True)
    group_name: Mapped[str] = mapped_column(String(256), nullable=False, index=True)
    group_type: Mapped[int] = mapped_column(Integer, default=2)
    scope: Mapped[str | None] = mapped_column(String(32))
    category: Mapped[str | None] = mapped_column(String(32))
    description: Mapped[str | None] = mapped_column(Text)
    ou_dn: Mapped[str | None] = mapped_column(String(512), index=True)
    ad_guid: Mapped[str | None] = mapped_column(String(64), unique=True)
    usn_changed: Mapped[int] = mapped_column(BigInteger, default=0)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class AdGroupMember(Base):
    __tablename__ = "ad_group_members"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    group_dn: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    member_dn: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    member_sid: Mapped[str | None] = mapped_column(String(128), index=True)
    member_type: Mapped[str] = mapped_column(String(16), default="user")
    synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ix_ad_group_members_group_member", "group_dn", "member_dn"),
    )