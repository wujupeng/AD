from fastapi import APIRouter, Request

from app.schemas.response import ApiResponse

router = APIRouter(prefix="/v1/enterprise/hybrid", tags=["Hybrid Identity"])


@router.get("/phase")
async def get_current_phase(request: Request):
    from app.core.deps import get_hybrid_identity_service
    svc = get_hybrid_identity_service(request)
    result = await svc.get_current_phase()
    return ApiResponse(data=result)


@router.put("/phase")
async def update_phase(request: Request):
    body = await request.json()
    from app.core.deps import get_hybrid_identity_service
    svc = get_hybrid_identity_service(request)
    result = await svc.update_phase(body["new_phase"])
    return ApiResponse(data=result)


@router.get("/entra-sync")
async def get_entra_sync_status(request: Request):
    from app.core.deps import get_hybrid_identity_service
    svc = get_hybrid_identity_service(request)
    result = await svc.get_entra_sync_status()
    return ApiResponse(data=result)


@router.get("/conditional-access")
async def get_conditional_access(request: Request):
    from app.core.deps import get_hybrid_identity_service
    svc = get_hybrid_identity_service(request)
    result = await svc.get_conditional_access()
    return ApiResponse(data=result)


@router.get("/exchange-migration")
async def get_exchange_migration(request: Request):
    from app.core.deps import get_hybrid_identity_service
    svc = get_hybrid_identity_service(request)
    result = await svc.get_exchange_migration()
    return ApiResponse(data=result)


@router.get("/intune-compliance")
async def get_intune_compliance(request: Request):
    from app.core.deps import get_hybrid_identity_service
    svc = get_hybrid_identity_service(request)
    result = await svc.get_intune_compliance()
    return ApiResponse(data=result)