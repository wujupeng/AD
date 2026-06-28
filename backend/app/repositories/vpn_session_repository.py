from typing import Any
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.remote_access import VpnSession


class VpnSessionRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_active_by_user(self, user_account: str) -> list[VpnSession]:
        result = await self._session.execute(
            select(VpnSession).where(VpnSession.user_account == user_account, VpnSession.is_active == True).order_by(VpnSession.connection_time.desc())
        )
        return list(result.scalars().all())

    async def get_active_sessions(self, limit: int = 100, offset: int = 0) -> list[VpnSession]:
        result = await self._session.execute(
            select(VpnSession).where(VpnSession.is_active == True).order_by(VpnSession.connection_time.desc()).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def get_by_gateway(self, gateway_id: str) -> list[VpnSession]:
        result = await self._session.execute(
            select(VpnSession).where(VpnSession.connected_gateway_id == gateway_id).order_by(VpnSession.connection_time.desc())
        )
        return list(result.scalars().all())

    async def get_by_site(self, site: str) -> list[VpnSession]:
        result = await self._session.execute(select(VpnSession).where(VpnSession.user_site == site))
        return list(result.scalars().all())

    async def count_active(self) -> int:
        result = await self._session.execute(select(VpnSession).where(VpnSession.is_active == True))
        return len(list(result.scalars().all()))

    async def close_session(self, session_id: str) -> None:
        from datetime import datetime
        await self._session.execute(
            update(VpnSession).where(VpnSession.session_id == session_id).values(is_active=False, disconnection_time=datetime.utcnow())
        )
        await self._session.commit()

    async def create(self, session_data: dict[str, Any]) -> VpnSession:
        session = VpnSession(**session_data)
        self._session.add(session)
        await self._session.commit()
        return session