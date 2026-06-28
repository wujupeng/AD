from fastapi import APIRouter, Request, Query
from pydantic import BaseModel

from app.schemas.response import ApiResponse

router = APIRouter(prefix="/audit", tags=["Audit"])


class ReportCreateRequest(BaseModel):
    report_type: str
    date_from: str
    date_to: str


@router.get("/logs")
async def query_audit_logs(
    request: Request,
    date_from: str | None = None,
    date_to: str | None = None,
    user_sid: str | None = None,
    event_type: str | None = None,
    site_code: str | None = None,
    result: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    from app.core.deps import get_audit_service
    service = await get_audit_service(request)
    data = await service.query_logs(
        filters={"date_from": date_from, "date_to": date_to, "user_sid": user_sid, "event_type": event_type, "site_code": site_code, "result": result},
        page=page,
        page_size=page_size,
    )
    return ApiResponse(data=data)


@router.post("/reports")
async def create_report(request: Request, body: ReportCreateRequest):
    from app.core.deps import get_audit_service
    service = await get_audit_service(request)
    report_id = await service.generate_report(body.report_type, body.date_from, body.date_to)
    return ApiResponse(data={"report_id": report_id, "status": "pending"})


@router.get("/reports/{report_id}")
async def get_report(request: Request, report_id: str):
    return ApiResponse(data={"report_id": report_id, "status": "pending"})


@router.get("/integrity-check")
async def check_integrity(request: Request, date_from: str | None = None, date_to: str | None = None):
    from app.core.deps import get_audit_service
    service = await get_audit_service(request)
    result = await service.check_integrity(date_from, date_to)
    return ApiResponse(data=result)