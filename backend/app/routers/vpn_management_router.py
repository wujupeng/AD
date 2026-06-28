from fastapi import APIRouter, HTTPException, Query
from typing import Any

router = APIRouter(prefix="/v1/enterprise/vpn", tags=["VPN Management"])

_remote_access_service: Any = None


def get_remote_access_service() -> Any:
    return _remote_access_service


@router.get("/gateways")
async def get_vpn_gateways():
    svc = get_remote_access_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    return {"code": 0, "message": "success", "data": await svc.get_vpn_gateways()}


@router.get("/gateways/{gateway_id}")
async def get_vpn_gateway_detail(gateway_id: str):
    svc = get_remote_access_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    result = await svc.get_vpn_gateway_detail(gateway_id)
    if not result:
        raise HTTPException(status_code=404, detail="Gateway not found")
    return {"code": 0, "message": "success", "data": result}


@router.get("/sessions")
async def get_vpn_sessions(limit: int = Query(100, ge=1, le=1000), offset: int = Query(0, ge=0)):
    svc = get_remote_access_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    return {"code": 0, "message": "success", "data": await svc.get_vpn_sessions(limit=limit, offset=offset)}


@router.get("/policies")
async def get_vpn_policies():
    svc = get_remote_access_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    return {"code": 0, "message": "success", "data": await svc.get_vpn_policies()}


@router.put("/policies")
async def update_vpn_policy(payload: dict[str, Any]):
    svc = get_remote_access_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    policy_id = payload.get("policy_id")
    config = payload.get("config", {})
    if not policy_id:
        raise HTTPException(status_code=400, detail="policy_id is required")
    result = await svc.update_vpn_policy(policy_id, config)
    return {"code": 0, "message": "success", "data": result}


@router.get("/device-tunnel-status")
async def get_device_tunnel_status(device_hostname: str = Query(...)):
    svc = get_remote_access_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    return {"code": 0, "message": "success", "data": await svc.get_tunnel_status("device", device_hostname)}


@router.get("/user-tunnel-status")
async def get_user_tunnel_status(user_account: str = Query(...)):
    svc = get_remote_access_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    return {"code": 0, "message": "success", "data": await svc.get_tunnel_status("user", user_account)}


@router.get("/kerberos-recovery")
async def get_kerberos_recovery_status(hours: int = Query(24, ge=1, le=168)):
    svc = get_remote_access_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    return {"code": 0, "message": "success", "data": await svc.get_kerberos_recovery_status(hours=hours)}


@router.get("/audit-log")
async def get_vpn_audit_log(hours: int = Query(24, ge=1, le=168), limit: int = Query(200, ge=1, le=1000)):
    svc = get_remote_access_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    return {"code": 0, "message": "success", "data": await svc.get_vpn_audit_log(hours=hours, limit=limit)}