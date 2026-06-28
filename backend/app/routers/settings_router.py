from fastapi import APIRouter, HTTPException
from typing import Any

router = APIRouter(prefix="/v1/enterprise/settings", tags=["Settings"])

_service: Any = None


def _get_service() -> Any:
    return _service


@router.get("/summary")
async def get_settings_summary():
    svc = _get_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    return {"code": 0, "message": "success", "data": await svc.get_settings_summary()}


@router.get("/cached-cred-policy")
async def get_cached_cred_policy():
    svc = _get_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    return {"code": 0, "message": "success", "data": await svc.get_cached_cred_policy()}


@router.put("/cached-cred-policy")
async def update_cached_cred_policy(data: dict[str, Any]):
    svc = _get_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    try:
        result = await svc.update_cached_cred_policy(
            policy_config=data.get("policy_config"),
            is_enabled=data.get("is_enabled"),
            version=data.get("version"),
        )
        return {"code": 0, "message": "success", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/hybrid-join")
async def get_hybrid_join_status():
    svc = _get_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    return {"code": 0, "message": "success", "data": await svc.get_hybrid_join_status()}


@router.post("/hybrid-join/configure")
async def configure_hybrid_join(data: dict[str, Any]):
    svc = _get_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    result = await svc.configure_hybrid_join(
        entra_connect_server=data.get("entra_connect_server"),
        sync_scope=data.get("sync_scope"),
        device_registration_policy=data.get("device_registration_policy"),
    )
    return {"code": 0, "message": "success", "data": result}


@router.get("/dc-isolation")
async def get_dc_isolation_policy():
    svc = _get_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    return {"code": 0, "message": "success", "data": await svc.get_dc_isolation_policy()}


@router.put("/dc-isolation")
async def update_dc_isolation_policy(data: dict[str, Any]):
    svc = _get_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    try:
        result = await svc.update_dc_isolation_policy(
            isolation_enabled=data.get("isolation_enabled"),
            rules=data.get("rules"),
            version=data.get("version"),
        )
        return {"code": 0, "message": "success", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/sites")
async def list_sites():
    svc = _get_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    return {"code": 0, "message": "success", "data": await svc.list_sites()}


@router.put("/sites/{site_code}")
async def update_site_config(site_code: str, data: dict[str, Any]):
    svc = _get_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    try:
        result = await svc.update_site_config(site_code, **data)
        return {"code": 0, "message": "success", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/integrations/ldap")
async def list_ldap_configs():
    svc = _get_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    return {"code": 0, "message": "success", "data": await svc.list_ldap_configs()}


@router.post("/integrations/ldap")
async def create_ldap_config(data: dict[str, Any]):
    svc = _get_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    result = await svc.create_ldap_config(**data)
    return {"code": 0, "message": "success", "data": result}


@router.delete("/integrations/ldap/{config_id}")
async def delete_ldap_config(config_id: str):
    svc = _get_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    await svc.delete_ldap_config(config_id)
    return {"code": 0, "message": "success", "data": {"deleted": True}}


@router.get("/integrations/external")
async def list_external_integrations(integration_type: str | None = None):
    svc = _get_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    return {"code": 0, "message": "success", "data": await svc.list_external_integrations(integration_type)}


@router.post("/integrations/external")
async def create_external_integration(data: dict[str, Any]):
    svc = _get_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    result = await svc.create_external_integration(**data)
    return {"code": 0, "message": "success", "data": result}


@router.delete("/integrations/external/{integration_id}")
async def delete_external_integration(integration_id: str):
    svc = _get_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    await svc.delete_external_integration(integration_id)
    return {"code": 0, "message": "success", "data": {"deleted": True}}