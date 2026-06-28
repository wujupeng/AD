from fastapi import APIRouter, Request, Query
from pydantic import BaseModel

from app.schemas.response import ApiResponse

router = APIRouter(tags=["Mail"])


class MailSendRequest(BaseModel):
    to_addresses: list[str]
    subject: str
    body: str
    is_html: bool = False


@router.get("/contacts")
async def search_contacts(request: Request, q: str = Query(...), limit: int = Query(20, ge=1, le=100)):
    from app.core.deps import get_mail_service
    service = await get_mail_service(request)
    results = await service.search_contacts(q, limit)
    return ApiResponse(data=results)


@router.post("/mail/send")
async def send_mail(request: Request, body: MailSendRequest):
    from app.core.deps import get_mail_service, get_current_user
    user = await get_current_user(request)
    service = await get_mail_service(request)
    from_address = user.get("email", "") if user else ""
    result = await service.send_mail(from_address, body.to_addresses, body.subject, body.body, body.is_html)
    return ApiResponse(data=result)


@router.get("/calendar/freebusy")
async def get_freebusy(request: Request, email: str = Query(...), date_from: str = Query(...), date_to: str = Query(...)):
    from app.core.deps import get_mail_service
    service = await get_mail_service(request)
    result = await service.get_freebusy(email, date_from, date_to)
    return ApiResponse(data=result)