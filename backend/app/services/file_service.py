import logging
from datetime import datetime, timezone
from typing import Any

from app.interfaces.i_file_provider import IFileProvider
from app.interfaces.i_audit_provider import IAuditProvider
from app.services.permission_service import PermissionService
from app.services.site_awareness_service import SiteAwarenessService
from app.repositories.dfs_access_repository import DfsAccessRepository

logger = logging.getLogger(__name__)


class FileService:
    def __init__(
        self,
        file_provider: IFileProvider,
        audit_provider: IAuditProvider,
        permission_service: PermissionService,
        site_awareness_service: SiteAwarenessService,
        dfs_access_repo: DfsAccessRepository,
    ):
        self._file = file_provider
        self._audit = audit_provider
        self._permission = permission_service
        self._site = site_awareness_service
        self._dfs_repo = dfs_access_repo

    async def list_directory(self, dfs_path: str, user_sid: str, site_code: str | None = None, client_ip: str | None = None) -> dict[str, Any]:
        resolved = await self._file.resolve_path(dfs_path, site_code)
        items = await self._file.list_directory(dfs_path, site_code)

        await self._dfs_repo.log_access({
            "user_sid": user_sid,
            "username": "",
            "dfs_path": dfs_path,
            "resolved_target": resolved,
            "operation": "list",
            "result": "success",
            "site_code": site_code,
            "client_ip": client_ip,
        })

        return {"path": dfs_path, "resolved_target": resolved, "items": items}

    async def download_file(self, dfs_path: str, user_sid: str, site_code: str | None = None, client_ip: str | None = None) -> dict[str, Any]:
        data = await self._file.download_file(dfs_path, site_code)
        return {"path": dfs_path, "data": data, "size": len(data)}

    async def upload_file(self, dfs_path: str, data: bytes, user_sid: str, site_code: str | None = None, client_ip: str | None = None) -> dict[str, Any]:
        success = await self._file.upload_file(dfs_path, data, site_code)

        await self._dfs_repo.log_access({
            "user_sid": user_sid,
            "username": "",
            "dfs_path": dfs_path,
            "operation": "upload",
            "result": "success" if success else "failure",
            "site_code": site_code,
            "client_ip": client_ip,
            "file_size": len(data),
        })

        return {"success": success}

    async def delete_file(self, dfs_path: str, user_sid: str, site_code: str | None = None, client_ip: str | None = None) -> dict[str, Any]:
        success = await self._file.delete_file(dfs_path, site_code)
        return {"success": success}