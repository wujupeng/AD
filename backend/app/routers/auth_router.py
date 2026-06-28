from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from app.schemas.response import ApiResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class MfaVerifyRequest(BaseModel):
    mfa_token: str
    mfa_code: str


@router.post("/login")
async def login(request: Request, body: LoginRequest):
    from app.core.deps import get_auth_service
    service = await get_auth_service(request)
    client_ip = request.client.host if request.client else None
    site_code = request.headers.get("X-Site-Code")
    result = await service.authenticate_password(body.username, body.password, client_ip, site_code)
    if result.get("success"):
        return ApiResponse(data=result)
    return ApiResponse(code=401, message=result.get("error", "Login failed"), data=result)


@router.post("/kerberos-login")
async def kerberos_login(request: Request):
    from app.core.deps import get_auth_service
    service = await get_auth_service(request)
    ticket = await request.body()
    client_ip = request.client.host if request.client else None
    result = await service.authenticate_kerberos(ticket, "", client_ip)
    if result.get("success"):
        return ApiResponse(data=result)
    return ApiResponse(code=401, message=result.get("error", "Kerberos auth failed"), data=result)


@router.post("/token-refresh")
async def token_refresh(request: Request, body: TokenRefreshRequest):
    from app.core.deps import get_auth_service
    service = await get_auth_service(request)
    result = await service.refresh_token(body.refresh_token)
    if result.get("success"):
        return ApiResponse(data=result)
    return ApiResponse(code=401, message=result.get("error", "Token refresh failed"), data=result)


@router.post("/logout")
async def logout(request: Request):
    from app.core.deps import get_current_user
    user = await get_current_user(request)
    if user:
        from app.core.deps import get_auth_service
        service = await get_auth_service(request)
        await service.logout(user.get("sub", ""), user.get("token_id"))
    return ApiResponse(data={"logged_out": True})


@router.get("/me")
async def get_me(request: Request):
    from app.core.deps import get_current_user
    user = await get_current_user(request)
    if user:
        return ApiResponse(data=user)
    return ApiResponse(code=401, message="Not authenticated")


@router.post("/mfa-verify")
async def mfa_verify(request: Request, body: MfaVerifyRequest):
    from app.core.deps import get_auth_service
    service = await get_auth_service(request)
    result = await service.verify_mfa(body.mfa_token, body.mfa_code)
    return ApiResponse(data=result)