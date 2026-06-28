from fastapi import APIRouter, Request

from app.schemas.response import ApiResponse

router = APIRouter(prefix="/v1/enterprise/tier", tags=["Tier Security"])


@router.get("/overview")
async def get_tier_overview(request: Request):
    from app.core.deps import get_tier_security_service
    svc = get_tier_security_service(request)
    result = await svc.get_tier_overview()
    return ApiResponse(data=result)


@router.get("/violations")
async def get_violations(request: Request, hours: int = 24):
    from app.core.deps import get_tier_security_service
    svc = get_tier_security_service(request)
    result = await svc.get_violations(hours)
    return ApiResponse(data=result)


@router.get("/laps/{computer_name}")
async def get_laps_password(request: Request, computer_name: str):
    from app.core.deps import get_tier_security_service
    svc = get_tier_security_service(request)
    result = await svc.get_laps_password(computer_name)
    return ApiResponse(data=result)


@router.get("/bitlocker/{computer_name}")
async def get_bitlocker_key(request: Request, computer_name: str):
    from app.core.deps import get_tier_security_service
    svc = get_tier_security_service(request)
    result = await svc.get_bitlocker_key(computer_name)
    return ApiResponse(data=result)


@router.get("/credential-guard")
async def get_credential_guard_status(request: Request, computer_name: str | None = None):
    from app.core.deps import get_tier_security_service
    svc = get_tier_security_service(request)
    result = await svc.get_credential_guard_status(computer_name)
    return ApiResponse(data=result)


@router.get("/applocker-wdac")
async def get_applocker_wdac_status(request: Request, computer_name: str | None = None):
    from app.core.deps import get_tier_security_service
    svc = get_tier_security_service(request)
    result = await svc.get_applocker_wdac_status(computer_name)
    return ApiResponse(data=result)


@router.get("/security-baseline")
async def get_security_baseline(request: Request, site: str | None = None):
    from app.core.deps import get_tier_security_service
    svc = get_tier_security_service(request)
    result = await svc.get_security_baseline(site)
    return ApiResponse(data=result)