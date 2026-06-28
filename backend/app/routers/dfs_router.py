from fastapi import APIRouter, Request, Query

from app.schemas.response import ApiResponse

router = APIRouter(prefix="/dfs", tags=["DFS"])


@router.get("/mappings")
async def get_dfs_mappings(request: Request):
    from app.core.deps import _dfs
    shares = await _dfs.list_shares()
    return ApiResponse(data={"mappings": shares})


@router.get("/shares")
async def list_shares(request: Request, site_code: str | None = None):
    from app.core.deps import _dfs
    shares = await _dfs.list_shares(site_code)
    return ApiResponse(data=shares)


@router.get("/files")
async def list_files(request: Request, path: str = Query(...), site_code: str | None = None):
    from app.core.deps import get_file_service, get_current_user
    user = await get_current_user(request)
    service = await get_file_service(request)
    result = await service.list_directory(path, user.get("sub", "") if user else "", site_code)
    return ApiResponse(data=result)


@router.get("/files/download")
async def download_file(request: Request, path: str = Query(...), site_code: str | None = None):
    from app.core.deps import get_file_service, get_current_user
    user = await get_current_user(request)
    service = await get_file_service(request)
    result = await service.download_file(path, user.get("sub", "") if user else "", site_code)
    return ApiResponse(data=result)


@router.post("/files/upload")
async def upload_file(request: Request):
    from app.core.deps import get_file_service, get_current_user
    user = await get_current_user(request)
    service = await get_file_service(request)
    form = await request.form()
    return ApiResponse(data={"success": True})


@router.delete("/files")
async def delete_file(request: Request, path: str = Query(...), site_code: str | None = None):
    from app.core.deps import get_file_service, get_current_user
    user = await get_current_user(request)
    service = await get_file_service(request)
    result = await service.delete_file(path, user.get("sub", "") if user else "", site_code)
    return ApiResponse(data=result)