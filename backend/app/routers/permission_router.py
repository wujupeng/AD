from fastapi import APIRouter, Request

from app.schemas.response import ApiResponse

router = APIRouter(prefix="/permissions", tags=["Permissions"])


@router.get("/check")
async def check_permission(request: Request, user_sid: str, resource: str, action: str):
    from app.core.deps import get_permission_service
    service = await get_permission_service(request)
    result = await service.check_permission(user_sid, resource, action)
    return ApiResponse(data=result)


@router.get("/user-permissions")
async def get_user_permissions(request: Request, user_sid: str):
    from app.core.deps import get_permission_service
    service = await get_permission_service(request)
    result = await service.get_effective_permissions(user_sid)
    return ApiResponse(data=result)


@router.get("/effective-groups")
async def get_effective_groups(request: Request, user_sid: str):
    from app.core.deps import get_permission_service
    service = await get_permission_service(request)
    result = await service.resolve_groups(user_sid)
    return ApiResponse(data=result)