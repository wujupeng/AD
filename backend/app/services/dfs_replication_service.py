import logging
from datetime import datetime, timezone
from typing import Any

from app.interfaces.i_dfs_replication_provider import IDfsReplicationProvider
from app.interfaces.i_cache_provider import ICacheProvider
from app.interfaces.i_audit_provider import IAuditProvider
from app.repositories.dfs_replication_repository import DfsReplicationRepository

logger = logging.getLogger(__name__)


class DfsReplicationService:
    def __init__(
        self,
        dfs_provider: IDfsReplicationProvider,
        cache_provider: ICacheProvider,
        audit_provider: IAuditProvider,
        dfs_repo: DfsReplicationRepository,
    ):
        self._dfs_provider = dfs_provider
        self._cache = cache_provider
        self._audit = audit_provider
        self._dfs_repo = dfs_repo

    async def get_namespace(self, namespace_path: str = "\\\\corp.company.com\\File") -> dict[str, Any]:
        return await self._dfs_provider.query_namespace_structure(namespace_path)

    async def get_replication_status(self) -> list[dict[str, Any]]:
        links = await self._dfs_repo.list_replication_links()
        return [{"link_id": l.link_id, "source_site": l.source_site, "target_site": l.target_site, "backlog_count": l.backlog_count, "sync_latency_seconds": l.sync_latency_seconds, "bandwidth_usage_mbps": l.bandwidth_usage_mbps, "link_status": l.link_status} for l in links]

    async def get_conflict_files(self, resolution_status: str | None = None) -> list[dict[str, Any]]:
        files = await self._dfs_repo.list_conflict_files(resolution_status)
        return [{"conflict_id": f.conflict_id, "file_name": f.file_name, "dfs_path": f.dfs_path, "source_site": f.source_site, "target_site": f.target_site, "conflict_time": str(f.conflict_time), "resolution_status": f.resolution_status} for f in files]

    async def resolve_conflict(self, conflict_id: str, resolved_version_path: str) -> bool:
        return await self._dfs_repo.update_conflict_resolution(conflict_id, "resolved", resolved_version_path)

    async def get_cluster_status(self) -> dict[str, Any]:
        return await self._dfs_provider.query_cluster_status()