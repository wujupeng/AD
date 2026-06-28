from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.dfs_replication import DfsReplicationLink, DfsConflictFile


class DfsReplicationRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def list_replication_links(self) -> list[DfsReplicationLink]:
        result = await self._session.execute(select(DfsReplicationLink))
        return list(result.scalars().all())

    async def get_replication_link(self, link_id: str) -> DfsReplicationLink | None:
        return await self._session.get(DfsReplicationLink, link_id)

    async def upsert_replication_link(self, link_id: str, data: dict[str, Any]) -> DfsReplicationLink:
        existing = await self.get_replication_link(link_id)
        if existing:
            for key, value in data.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            await self._session.flush()
            return existing
        link = DfsReplicationLink(link_id=link_id, **data)
        self._session.add(link)
        await self._session.flush()
        return link

    async def list_conflict_files(self, resolution_status: str | None = None) -> list[DfsConflictFile]:
        query = select(DfsConflictFile).order_by(DfsConflictFile.conflict_time.desc())
        if resolution_status:
            query = query.where(DfsConflictFile.resolution_status == resolution_status)
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def get_conflict_file(self, conflict_id: str) -> DfsConflictFile | None:
        return await self._session.get(DfsConflictFile, conflict_id)

    async def update_conflict_resolution(self, conflict_id: str, resolution_status: str, resolved_version_path: str | None = None) -> bool:
        result = await self._session.execute(
            update(DfsConflictFile).where(DfsConflictFile.conflict_id == conflict_id).values(resolution_status=resolution_status, resolved_version_path=resolved_version_path)
        )
        return result.rowcount > 0