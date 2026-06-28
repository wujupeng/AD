import logging
from typing import Any

from app.interfaces.i_print_provider import IPrintProvider

logger = logging.getLogger(__name__)


class PrintAdapter(IPrintProvider):
    async def list_printers(self, site_code: str | None = None) -> list[dict[str, Any]]:
        logger.info("Print list_printers: site=%s", site_code)
        return []

    async def submit_task(self, printer_name: str, document_path: str, options: dict[str, Any] | None = None) -> str:
        import uuid
        task_id = str(uuid.uuid4())
        logger.info("Print submit_task: printer=%s, task=%s", printer_name, task_id)
        return task_id

    async def get_task_status(self, task_id: str) -> dict[str, Any]:
        logger.info("Print get_task_status: task=%s", task_id)
        return {"task_id": task_id, "status": "pending"}

    async def check_quota(self, user_sid: str, month: str) -> dict[str, Any]:
        logger.info("Print check_quota: user=%s, month=%s", user_sid, month)
        return {"pages_used": 0, "pages_limit": 500, "remaining": 500}