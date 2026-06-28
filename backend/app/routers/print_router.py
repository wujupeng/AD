from fastapi import APIRouter, Request, Query
from pydantic import BaseModel

from app.schemas.response import ApiResponse

router = APIRouter(tags=["Print"])


class PrintTaskCreate(BaseModel):
    printer_name: str
    document_path: str
    pages: int = 1


@router.get("/printers")
async def list_printers(request: Request, site_code: str | None = None):
    from app.core.deps import get_print_service
    service = await get_print_service(request)
    printers = await service.list_printers(site_code)
    return ApiResponse(data=printers)


@router.post("/print-tasks")
async def submit_print_task(request: Request, body: PrintTaskCreate):
    from app.core.deps import get_print_service, get_current_user
    user = await get_current_user(request)
    service = await get_print_service(request)
    result = await service.submit_task(
        user_sid=user.get("sub", "") if user else "",
        username=user.get("username", "") if user else "",
        printer_name=body.printer_name,
        document_path=body.document_path,
        pages=body.pages,
    )
    return ApiResponse(data=result)


@router.get("/print-tasks/{task_id}")
async def get_print_task(request: Request, task_id: str):
    from app.core.deps import get_print_service
    service = await get_print_service(request)
    result = await service.get_task_status(task_id)
    return ApiResponse(data=result)


@router.get("/print-tasks")
async def list_print_tasks(request: Request, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100)):
    return ApiResponse(data={"items": [], "total": 0, "page": page, "page_size": page_size})


@router.get("/print-quota")
async def get_print_quota(request: Request, user_sid: str | None = None, month: str | None = None):
    from app.core.deps import get_print_service, get_current_user
    user = await get_current_user(request)
    service = await get_print_service(request)
    from datetime import datetime as dt
    result = await service.get_quota(user_sid or (user.get("sub", "") if user else ""), month or dt.now().strftime("%Y-%m"))
    return ApiResponse(data=result)