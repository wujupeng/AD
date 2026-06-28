from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from app.schemas.response import ApiResponse

router = APIRouter(tags=["Integration"])


class SpConfigCreate(BaseModel):
    sp_name: str
    sp_type: str
    entity_id: str
    acs_url: str | None = None
    slo_url: str | None = None
    client_id: str | None = None
    redirect_uris: str | None = None


@router.get("/saml/metadata")
async def saml_metadata(request: Request):
    from app.core.deps import get_saml_service
    service = await get_saml_service(request)
    metadata = await service.get_metadata()
    return ApiResponse(data={"metadata": metadata})


@router.post("/saml/sso")
async def saml_sso(request: Request):
    from app.core.deps import get_saml_service
    service = await get_saml_service(request)
    body = await request.body()
    return ApiResponse(data={"message": "SAML SSO endpoint"})


@router.post("/saml/slo")
async def saml_slo(request: Request):
    from app.core.deps import get_saml_service
    service = await get_saml_service(request)
    return ApiResponse(data={"message": "SAML SLO endpoint"})


@router.get("/oidc/.well-known/openid-configuration")
async def oidc_discovery(request: Request):
    from app.core.deps import get_oidc_service
    service = await get_oidc_service(request)
    base_url = str(request.base_url).rstrip("/")
    discovery = await service.get_discovery(base_url)
    return discovery


@router.get("/oidc/authorize")
async def oidc_authorize(request: Request):
    from app.core.deps import get_oidc_service
    service = await get_oidc_service(request)
    client_id = request.query_params.get("client_id", "")
    redirect_uri = request.query_params.get("redirect_uri", "")
    scope = request.query_params.get("scope", "openid")
    state = request.query_params.get("state", "")
    result = await service.authorize(client_id, redirect_uri, scope, state)
    return ApiResponse(data=result)


@router.post("/oidc/token")
async def oidc_token(request: Request):
    from app.core.deps import get_oidc_service
    service = await get_oidc_service(request)
    form = await request.form()
    result = await service.exchange_code(
        code=form.get("code", ""),
        client_id=form.get("client_id", ""),
        client_secret=form.get("client_secret", ""),
        redirect_uri=form.get("redirect_uri", ""),
    )
    return result


@router.get("/oidc/userinfo")
async def oidc_userinfo(request: Request):
    from app.core.deps import get_oidc_service
    service = await get_oidc_service(request)
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else ""
    result = await service.get_userinfo(token)
    return result


@router.get("/oidc/jwks")
async def oidc_jwks(request: Request):
    from app.core.deps import get_oidc_service
    service = await get_oidc_service(request)
    return await service.get_jwks()


@router.get("/integration/sp-configs")
async def list_sp_configs(request: Request):
    from app.core.deps import get_integration_repo
    repo = await get_integration_repo(request)
    configs = await repo.list_sp_configs()
    return ApiResponse(data=[{"sp_name": c.sp_name, "sp_type": c.sp_type, "entity_id": c.entity_id, "is_enabled": c.is_enabled} for c in configs])


@router.post("/integration/sp-configs")
async def create_sp_config(request: Request, body: SpConfigCreate):
    from app.core.deps import get_integration_repo
    repo = await get_integration_repo(request)
    config = await repo.create_sp_config(body.model_dump())
    return ApiResponse(data={"sp_name": config.sp_name})


@router.get("/integration/sp-configs/{sp_name}")
async def get_sp_config(request: Request, sp_name: str):
    from app.core.deps import get_integration_repo
    repo = await get_integration_repo(request)
    config = await repo.get_sp_config(sp_name)
    if config:
        return ApiResponse(data={"sp_name": config.sp_name, "sp_type": config.sp_type, "entity_id": config.entity_id})
    return ApiResponse(code=404, message="SP config not found")