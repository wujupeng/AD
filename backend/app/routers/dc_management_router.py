from fastapi import APIRouter, Request

from app.schemas.response import ApiResponse

router = APIRouter(prefix="/v1/enterprise/dc", tags=["DC Management"])


@router.get("")
async def list_dcs(request: Request):
    from app.core.deps import get_dc_management_service
    svc = get_dc_management_service(request)
    result = await svc.list_dcs()
    return ApiResponse(data=result)


@router.get("/replication-topology")
async def get_replication_topology(request: Request):
    from app.core.deps import get_dc_management_service
    svc = get_dc_management_service(request)
    result = await svc.get_replication_topology()
    return ApiResponse(data=result)


@router.get("/fsmo-roles")
async def get_fsmo_roles(request: Request):
    from app.core.deps import get_dc_management_service
    svc = get_dc_management_service(request)
    result = await svc.get_fsmo_roles()
    return ApiResponse(data=result)


@router.post("/fsmo-transfer")
async def transfer_fsmo_role(request: Request):
    body = await request.json()
    from app.core.deps import get_dc_management_service
    svc = get_dc_management_service(request)
    result = await svc.transfer_fsmo_role(body["role"], body["target_dc"])
    return ApiResponse(data=result)


@router.get("/config-baseline/{dc_hostname}")
async def get_config_baseline(request: Request, dc_hostname: str):
    from app.core.deps import get_dc_management_service
    svc = get_dc_management_service(request)
    result = await svc.get_config_baseline(dc_hostname)
    return ApiResponse(data=result)


@router.get("/config-drift/{dc_hostname}")
async def check_config_drift(request: Request, dc_hostname: str):
    from app.core.deps import get_dc_management_service
    svc = get_dc_management_service(request)
    result = await svc.check_config_drift(dc_hostname)
    return ApiResponse(data=result)


@router.get("/{dc_hostname}")
async def get_dc(request: Request, dc_hostname: str):
    from app.core.deps import get_dc_management_service
    svc = get_dc_management_service(request)
    result = await svc.get_dc(dc_hostname)
    if not result:
        return ApiResponse(code=404, message="DC not found", data=None)
    return ApiResponse(data=result)
