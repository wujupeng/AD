from fastapi import APIRouter, Request

from app.schemas.response import ApiResponse

router = APIRouter(prefix="/v1/enterprise/dfs", tags=["DFS Replication"])


@router.get("/namespace")
async def get_namespace(request: Request):
    from app.core.deps import get_dfs_replication_service
    svc = get_dfs_replication_service(request)
    result = await svc.get_namespace()
    return ApiResponse(data=result)


@router.get("/replication-status")
async def get_replication_status(request: Request):
    from app.core.deps import get_dfs_replication_service
    svc = get_dfs_replication_service(request)
    result = await svc.get_replication_status()
    return ApiResponse(data=result)


@router.get("/conflicts")
async def get_conflict_files(request: Request, resolution_status: str | None = None):
    from app.core.deps import get_dfs_replication_service
    svc = get_dfs_replication_service(request)
    result = await svc.get_conflict_files(resolution_status)
    return ApiResponse(data=result)


@router.get("/cluster-status")
async def get_cluster_status(request: Request):
    from app.core.deps import get_dfs_replication_service
    svc = get_dfs_replication_service(request)
    result = await svc.get_cluster_status()
    return ApiResponse(data=result)