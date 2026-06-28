from fastapi import APIRouter, Depends, HTTPException
from typing import Any

router = APIRouter(prefix="/v1/enterprise/remote-access", tags=["Remote Access"])

_remote_access_service: Any = None


def get_remote_access_service() -> Any:
    return _remote_access_service


@router.get("/cached-cred-policy")
async def get_cached_cred_policy():
    svc = get_remote_access_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    return {"code": 0, "message": "success", "data": await svc.get_cached_cred_policy()}


@router.put("/cached-cred-policy")
async def configure_cached_cred_policy(config: dict[str, Any]):
    svc = get_remote_access_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    result = await svc.configure_cached_cred_policy(config)
    return {"code": 0, "message": "success", "data": result}


@router.get("/conditional-access")
async def get_conditional_access():
    svc = get_remote_access_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    return {"code": 0, "message": "success", "data": await svc.get_conditional_access_policies()}


@router.get("/hybrid-join-status")
async def get_hybrid_join_status():
    svc = get_remote_access_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    return {"code": 0, "message": "success", "data": await svc.get_hybrid_join_status()}


@router.post("/hybrid-join/configure")
async def configure_hybrid_join(config: dict[str, Any]):
    svc = get_remote_access_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    result = await svc.configure_hybrid_join(config)
    return {"code": 0, "message": "success", "data": result}


@router.get("/device-classification")
async def get_device_classification():
    svc = get_remote_access_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    return {"code": 0, "message": "success", "data": await svc.get_device_classifications()}


@router.put("/device-classification")
async def update_device_classification(payload: dict[str, Any]):
    svc = get_remote_access_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    device_class = payload.get("device_class")
    if not device_class:
        raise HTTPException(status_code=400, detail="device_class is required")
    kwargs = {k: v for k, v in payload.items() if k != "device_class"}
    result = await svc.update_device_classification(device_class, **kwargs)
    return {"code": 0, "message": "success", "data": result}


@router.get("/dc-isolation")
async def get_dc_isolation():
    svc = get_remote_access_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    return {"code": 0, "message": "success", "data": await svc.get_dc_isolation_policy()}


@router.put("/dc-isolation")
async def configure_dc_isolation(policy: dict[str, Any]):
    svc = get_remote_access_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    result = await svc.configure_dc_isolation(policy)
    return {"code": 0, "message": "success", "data": result}


@router.post("/password-sync")
async def trigger_password_sync(payload: dict[str, Any]):
    svc = get_remote_access_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    user_account = payload.get("user_account")
    if not user_account:
        raise HTTPException(status_code=400, detail="user_account is required")
    result = await svc.trigger_password_sync(user_account)
    return {"code": 0, "message": "success", "data": result}


@router.post("/gpo-remote-update")
async def trigger_gpo_update(payload: dict[str, Any]):
    svc = get_remote_access_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    target_ou = payload.get("target_ou", "")
    computer_list = payload.get("computer_list", [])
    result = await svc.trigger_gpo_update(target_ou, computer_list)
    return {"code": 0, "message": "success", "data": result}


@router.get("/bitlocker-remote")
async def get_bitlocker_remote():
    svc = get_remote_access_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    return {"code": 0, "message": "success", "data": await svc.get_bitlocker_remote_status()}


@router.post("/bitlocker-remote/enable")
async def enable_bitlocker_remotely(payload: dict[str, Any]):
    svc = get_remote_access_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    computer_name = payload.get("computer_name")
    if not computer_name:
        raise HTTPException(status_code=400, detail="computer_name is required")
    result = await svc.enable_bitlocker_remotely(computer_name)
    return {"code": 0, "message": "success", "data": result}


@router.post("/bitlocker-remote/rotate-key")
async def rotate_bitlocker_key(payload: dict[str, Any]):
    svc = get_remote_access_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    computer_name = payload.get("computer_name")
    if not computer_name:
        raise HTTPException(status_code=400, detail="computer_name is required")
    result = await svc.rotate_bitlocker_key(computer_name)
    return {"code": 0, "message": "success", "data": result}


@router.get("/defender-status")
async def get_defender_status():
    svc = get_remote_access_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    return {"code": 0, "message": "success", "data": await svc.get_defender_status()}


@router.get("/intune-compliance-detail")
async def get_intune_compliance_detail():
    svc = get_remote_access_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    return {"code": 0, "message": "success", "data": await svc.get_intune_compliance_detail()}


@router.get("/sso-status")
async def get_sso_status():
    svc = get_remote_access_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    return {"code": 0, "message": "success", "data": await svc.get_sso_status()}