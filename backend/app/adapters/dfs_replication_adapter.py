import logging
from typing import Any

from app.interfaces.i_dfs_replication_provider import IDfsReplicationProvider

logger = logging.getLogger(__name__)


class DfsReplicationAdapter(IDfsReplicationProvider):
    def __init__(self):
        self._cluster_status: dict[str, Any] = {"status": "unknown"}

    async def query_namespace_structure(self, namespace_path: str) -> dict[str, Any]:
        return {"namespace_path": namespace_path, "folders": [], "status": "not_implemented", "message": "DFS Namespace requires WMI/PowerShell Remoting"}

    async def query_replication_status(self, link_id: str | None = None) -> list[dict[str, Any]]:
        return []

    async def query_conflict_files(self, resolved: bool | None = None) -> list[dict[str, Any]]:
        return []

    async def query_cluster_status(self) -> dict[str, Any]:
        return self._cluster_status