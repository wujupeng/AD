from fastapi import APIRouter, HTTPException, Query
from typing import Any

router = APIRouter(prefix="/v1/enterprise/identity", tags=["Identity Center"])

_service: Any = None


def _get_service() -> Any:
    return _service


@router.post("/onboarding")
async def trigger_onboarding(data: dict[str, Any]):
    svc = _get_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    return {"code": 0, "message": "success", "data": await svc.trigger_onboarding(data)}


@router.get("/onboarding")
async def list_onboarding(limit: int = Query(50, ge=1, le=200)):
    svc = _get_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    return {"code": 0, "message": "success", "data": await svc.list_onboarding(limit=limit)}


@router.get("/onboarding/{request_id}")
async def get_onboarding_status(request_id: str):
    svc = _get_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    result = await svc.get_onboarding_status(request_id)
    if not result:
        raise HTTPException(status_code=404, detail="Request not found")
    return {"code": 0, "message": "success", "data": result}


@router.post("/onboarding/{request_id}/execute")
async def execute_onboarding(request_id: str):
    svc = _get_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    result = await svc.execute_onboarding(request_id)
    return {"code": 0, "message": "success", "data": result}


@router.post("/offboarding")
async def trigger_offboarding(data: dict[str, Any]):
    svc = _get_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    return {"code": 0, "message": "success", "data": await svc.trigger_offboarding(data)}


@router.get("/offboarding")
async def list_offboarding(limit: int = Query(50, ge=1, le=200)):
    svc = _get_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    return {"code": 0, "message": "success", "data": await svc.list_offboarding(limit=limit)}


@router.get("/offboarding/{request_id}")
async def get_offboarding_status(request_id: str):
    svc = _get_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    result = await svc.get_offboarding_status(request_id)
    if not result:
        raise HTTPException(status_code=404, detail="Request not found")
    return {"code": 0, "message": "success", "data": result}


@router.post("/offboarding/{request_id}/execute")
async def execute_offboarding(request_id: str):
    svc = _get_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    result = await svc.execute_offboarding(request_id)
    return {"code": 0, "message": "success", "data": result}


@router.post("/transfer")
async def trigger_transfer(data: dict[str, Any]):
    svc = _get_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    return {"code": 0, "message": "success", "data": await svc.trigger_transfer(data)}


@router.get("/transfer")
async def list_transfer(limit: int = Query(50, ge=1, le=200)):
    svc = _get_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    return {"code": 0, "message": "success", "data": await svc.list_transfer(limit=limit)}


@router.get("/transfer/{request_id}")
async def get_transfer_status(request_id: str):
    svc = _get_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    result = await svc.get_transfer_status(request_id)
    if not result:
        raise HTTPException(status_code=404, detail="Request not found")
    return {"code": 0, "message": "success", "data": result}


@router.get("/lifecycle/{ad_account}")
async def get_lifecycle_report(ad_account: str):
    svc = _get_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    return {"code": 0, "message": "success", "data": await svc.get_lifecycle_report(ad_account)}


@router.get("/lifecycle-events")
async def get_lifecycle_events(limit: int = Query(100, ge=1, le=1000)):
    svc = _get_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    return {"code": 0, "message": "success", "data": await svc.get_lifecycle_events(limit=limit)}


@router.post("/card-auth")
async def card_auth(data: dict[str, Any]):
    svc = _get_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    card_id = data.get("card_id", "")
    target_system = data.get("target_system", "")
    return {"code": 0, "message": "success", "data": await svc.card_auth(card_id, target_system)}


@router.get("/source-policy")
async def get_identity_source_policy():
    svc = _get_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    return {"code": 0, "message": "success", "data": await svc.get_identity_source_policy()}


@router.put("/source-policy")
async def configure_identity_source_policy(data: dict[str, Any]):
    svc = _get_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    policy_id = data.get("policy_id")
    if not policy_id:
        raise HTTPException(status_code=400, detail="policy_id is required")
    kwargs = {k: v for k, v in data.items() if k not in ("policy_id",)}
    return {"code": 0, "message": "success", "data": await svc.configure_identity_source_policy(policy_id, **kwargs)}


@router.get("/entra-extension")
async def get_entra_extension_status():
    svc = _get_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    return {"code": 0, "message": "success", "data": await svc.get_entra_extension_status()}


@router.get("/print-convergence")
async def get_print_convergence():
    svc = _get_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    return {"code": 0, "message": "success", "data": await svc.get_print_convergence()}


@router.get("/print-cost-audit")
async def get_print_cost_audit(limit: int = Query(100, ge=1, le=1000)):
    svc = _get_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    return {"code": 0, "message": "success", "data": await svc.get_print_cost_audit(limit=limit)}


@router.post("/print-cost-report")
async def generate_print_cost_report(data: dict[str, Any]):
    svc = _get_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    return {"code": 0, "message": "success", "data": await svc.generate_print_cost_report(data)}


@router.get("/saml-oidc-apps")
async def get_saml_oidc_apps():
    svc = _get_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    return {"code": 0, "message": "success", "data": await svc.get_saml_oidc_apps()}


@router.post("/saml-oidc-apps")
async def register_saml_oidc_app(data: dict[str, Any]):
    svc = _get_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    return {"code": 0, "message": "success", "data": await svc.register_saml_oidc_app(data)}


@router.put("/saml-oidc-apps/{app_id}")
async def update_saml_oidc_app(app_id: str, data: dict[str, Any]):
    svc = _get_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    kwargs = {k: v for k, v in data.items() if k != "app_id"}
    return {"code": 0, "message": "success", "data": await svc.update_saml_oidc_app(app_id, **kwargs)}


@router.delete("/saml-oidc-apps/{app_id}")
async def delete_saml_oidc_app(app_id: str):
    svc = _get_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    return {"code": 0, "message": "success", "data": await svc.delete_saml_oidc_app(app_id)}


@router.get("/wifi-8021x-policies")
async def get_wifi_policies():
    svc = _get_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    return {"code": 0, "message": "success", "data": await svc.get_wifi_policies()}


@router.post("/wifi-8021x-policies")
async def create_wifi_policy(data: dict[str, Any]):
    svc = _get_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    return {"code": 0, "message": "success", "data": await svc.create_wifi_policy(data)}


@router.put("/wifi-8021x-policies/{policy_id}")
async def update_wifi_policy(policy_id: str, data: dict[str, Any]):
    svc = _get_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    kwargs = {k: v for k, v in data.items() if k != "policy_id"}
    return {"code": 0, "message": "success", "data": await svc.update_wifi_policy(policy_id, **kwargs)}


@router.get("/autopilot-profiles")
async def get_autopilot_profiles():
    svc = _get_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    return {"code": 0, "message": "success", "data": await svc.get_autopilot_profiles()}


@router.post("/autopilot-profiles")
async def create_autopilot_profile(data: dict[str, Any]):
    svc = _get_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    return {"code": 0, "message": "success", "data": await svc.create_autopilot_profile(data)}


@router.put("/autopilot-profiles/{profile_id}")
async def update_autopilot_profile(profile_id: str, data: dict[str, Any]):
    svc = _get_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    kwargs = {k: v for k, v in data.items() if k != "profile_id"}
    return {"code": 0, "message": "success", "data": await svc.update_autopilot_profile(profile_id, **kwargs)}


@router.get("/conditional-access-rules")
async def get_conditional_access_rules():
    svc = _get_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    return {"code": 0, "message": "success", "data": await svc.get_conditional_access_rules()}


@router.post("/conditional-access-rules")
async def create_conditional_access_rule(data: dict[str, Any]):
    svc = _get_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    return {"code": 0, "message": "success", "data": await svc.create_conditional_access_rule(data)}


@router.put("/conditional-access-rules/{rule_id}")
async def update_conditional_access_rule(rule_id: str, data: dict[str, Any]):
    svc = _get_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    kwargs = {k: v for k, v in data.items() if k != "rule_id"}
    return {"code": 0, "message": "success", "data": await svc.update_conditional_access_rule(rule_id, **kwargs)}


@router.get("/audit/lifecycle")
async def get_lifecycle_audit(limit: int = Query(100, ge=1, le=1000)):
    svc = _get_service()
    if not svc:
        raise HTTPException(status_code=503, detail="Service not available")
    return {"code": 0, "message": "success", "data": await svc.get_lifecycle_audit(limit=limit)}