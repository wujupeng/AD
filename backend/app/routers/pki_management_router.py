from fastapi import APIRouter, Request

from app.schemas.response import ApiResponse

router = APIRouter(prefix="/v1/enterprise/pki", tags=["PKI Management"])


@router.get("/templates")
async def list_templates(request: Request):
    from app.core.deps import get_pki_management_service
    svc = get_pki_management_service(request)
    result = await svc.list_templates()
    return ApiResponse(data=result)


@router.post("/templates")
async def create_template(request: Request):
    body = await request.json()
    from app.core.deps import get_pki_management_service
    svc = get_pki_management_service(request)
    result = await svc.create_template(body)
    return ApiResponse(data=result)


@router.get("/certificates")
async def list_certificates(request: Request, template_name: str | None = None, status: str | None = None):
    from app.core.deps import get_pki_management_service
    svc = get_pki_management_service(request)
    result = await svc.list_expiring(365 * 10)
    return ApiResponse(data=result)


@router.post("/certificates/issue")
async def issue_certificate(request: Request):
    body = await request.json()
    from app.core.deps import get_pki_management_service
    svc = get_pki_management_service(request)
    result = await svc.issue_certificate(body["template_name"], body["subject"], body.get("requester_sid", ""))
    return ApiResponse(data=result)


@router.post("/certificates/{serial_number}/revoke")
async def revoke_certificate(request: Request, serial_number: str):
    body = await request.json()
    from app.core.deps import get_pki_management_service
    svc = get_pki_management_service(request)
    result = await svc.revoke_certificate(serial_number, body.get("reason", "unspecified"))
    return ApiResponse(data=result)


@router.post("/certificates/{serial_number}/renew")
async def renew_certificate(request: Request, serial_number: str):
    from app.core.deps import get_pki_management_service
    svc = get_pki_management_service(request)
    result = await svc.renew_certificate(serial_number)
    return ApiResponse(data=result)


@router.get("/expiring")
async def list_expiring(request: Request, days: int = 30):
    from app.core.deps import get_pki_management_service
    svc = get_pki_management_service(request)
    result = await svc.list_expiring(days)
    return ApiResponse(data=result)


@router.get("/root-ca-status")
async def get_root_ca_status(request: Request):
    from app.core.deps import get_pki_management_service
    svc = get_pki_management_service(request)
    result = await svc.get_root_ca_status()
    return ApiResponse(data=result)