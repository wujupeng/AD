from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.print import PrintTask, PrintQuota


class PrintTaskRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_task(self, data: dict[str, Any]) -> PrintTask:
        task = PrintTask(**data)
        self._session.add(task)
        await self._session.flush()
        return task

    async def update_status(self, task_id: str, status: str, error_message: str | None = None) -> bool:
        values: dict[str, Any] = {"status": status}
        if status in ("completed", "failed", "cancelled"):
            values["completed_at"] = datetime.now(timezone.utc)
        if error_message:
            values["error_message"] = error_message
        result = await self._session.execute(
            update(PrintTask).where(PrintTask.task_id == task_id).values(**values)
        )
        return result.rowcount > 0

    async def list_by_user(self, user_sid: str, page: int = 1, page_size: int = 20) -> tuple[list[PrintTask], int]:
        from sqlalchemy import func
        count_result = await self._session.execute(
            select(func.count(PrintTask.id)).where(PrintTask.user_sid == user_sid)
        )
        total = count_result.scalar() or 0

        result = await self._session.execute(
            select(PrintTask)
            .where(PrintTask.user_sid == user_sid)
            .order_by(PrintTask.submitted_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        tasks = result.scalars().all()
        return list(tasks), total

    async def get_quota_usage(self, user_sid: str, month: str) -> PrintQuota | None:
        result = await self._session.execute(
            select(PrintQuota).where(PrintQuota.user_sid == user_sid, PrintQuota.month == month)
        )
        return result.scalar_one_or_none()

    async def increment_quota(self, user_sid: str, month: str, pages: int) -> PrintQuota:
        quota = await self.get_quota_usage(user_sid, month)
        if quota:
            quota.pages_used += pages
            quota.updated_at = datetime.now(timezone.utc)
            await self._session.flush()
            return quota
        else:
            quota = PrintQuota(user_sid=user_sid, month=month, pages_used=pages)
            self._session.add(quota)
            await self._session.flush()
            return quota