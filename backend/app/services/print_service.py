import logging
from typing import Any

from app.interfaces.i_print_provider import IPrintProvider
from app.interfaces.i_audit_provider import IAuditProvider
from app.services.permission_service import PermissionService
from app.repositories.print_task_repository import PrintTaskRepository

logger = logging.getLogger(__name__)


class PrintService:
    def __init__(
        self,
        print_provider: IPrintProvider,
        audit_provider: IAuditProvider,
        permission_service: PermissionService,
        print_task_repo: PrintTaskRepository,
    ):
        self._print = print_provider
        self._audit = audit_provider
        self._permission = permission_service
        self._print_repo = print_task_repo

    async def list_printers(self, site_code: str | None = None) -> list[dict[str, Any]]:
        return await self._print.list_printers(site_code)

    async def submit_task(self, user_sid: str, username: str, printer_name: str, document_path: str, pages: int = 1, site_code: str | None = None) -> dict[str, Any]:
        from datetime import datetime as dt
        month = dt.now().strftime("%Y-%m")
        quota = await self._print.check_quota(user_sid, month)
        if quota.get("remaining", 0) < pages:
            return {"success": False, "error": "PRINT_QUOTA_EXCEEDED"}

        task_id = await self._print.submit_task(printer_name, document_path)

        await self._print_repo.create_task({
            "task_id": task_id,
            "user_sid": user_sid,
            "username": username,
            "printer_name": printer_name,
            "printer_site": site_code,
            "document_name": document_path,
            "pages": pages,
            "status": "pending",
        })

        await self._print_repo.increment_quota(user_sid, month, pages)

        return {"success": True, "task_id": task_id}

    async def get_task_status(self, task_id: str) -> dict[str, Any]:
        return await self._print.get_task_status(task_id)

    async def get_quota(self, user_sid: str, month: str) -> dict[str, Any]:
        return await self._print.check_quota(user_sid, month)