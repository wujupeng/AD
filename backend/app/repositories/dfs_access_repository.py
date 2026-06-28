from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.dfs import DfsAccessLog


class DfsAccessRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def log_access(self, data: dict) -> DfsAccessLog:
        record = DfsAccessLog(**data, occurred_at=datetime.now(timezone.utc))
        self._session.add(record)
        await self._session.flush()
        return record

    async def query_by_user(self, user_sid: str, page: int = 1, page_size: int = 20) -> tuple[list[DfsAccessLog], int]:
        count_result = await self._session.execute(
            select(func.count(DfsAccessLog.id)).where(DfsAccessLog.user_sid == user_sid)
        )
        total = count_result.scalar() or 0

        result = await self._session.execute(
            select(DfsAccessLog)
            .where(DfsAccessLog.user_sid == user_sid)
            .order_by(DfsAccessLog.occurred_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        records = result.scalars().all()
        return list(records), total