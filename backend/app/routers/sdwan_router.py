from fastapi import APIRouter, Request

from app.schemas.response import ApiResponse

router = APIRouter(prefix="/v1/enterprise/sdwan", tags=["SD-WAN"])


@router.get("/links")
async def list_links(request: Request):
    from app.core.deps import get_sdwan_integration_service
    svc = get_sdwan_integration_service(request)
    result = await svc.list_links()
    return ApiResponse(data=result)


@router.get("/qos")
async def get_qos_policies(request: Request):
    from app.core.deps import get_sdwan_integration_service
    svc = get_sdwan_integration_service(request)
    result = await svc.get_qos_policies()
    return ApiResponse(data=result)


@router.get("/impact-analysis")
async def get_impact_analysis(request: Request):
    from app.core.deps import get_sdwan_integration_service
    svc = get_sdwan_integration_service(request)
    result = await svc.get_impact_analysis()
    return ApiResponse(data=result)