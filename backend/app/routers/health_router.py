from fastapi import APIRouter, Request, Query

from app.schemas.response import ApiResponse

router = APIRouter(tags=["Health"])

_monitor_service: any = None


@router.get("/health")
async def health_check(request: Request):
    from app.core.config import settings
    return ApiResponse(data={
        "status": "healthy",
        "version": settings.APP_VERSION,
        "components": {
            "database": "unknown",
            "redis": "unknown",
            "ad": "unknown",
            "exchange": "unknown",
            "print_service": "unknown",
        },
    })


@router.get("/health/metrics")
async def health_metrics(request: Request):
    return ApiResponse(data={
        "auth_success_rate": 0.0,
        "auth_latency_ms": 0.0,
        "active_sessions": 0,
    })


@router.get("/health/detail")
async def health_detail(request: Request):
    if not _monitor_service:
        return ApiResponse(data={"status": "unavailable", "message": "Monitor service not initialized"})
    data = await _monitor_service.get_health_detail()
    return ApiResponse(data=data)


@router.get("/health/postgresql/slow-queries")
async def postgresql_slow_queries(request: Request, hours: int = Query(24, ge=1), min_duration_ms: int = Query(1000, ge=1), limit: int = Query(20, ge=1, le=100)):
    if not _monitor_service:
        return ApiResponse(data=[])
    data = await _monitor_service.get_slow_queries(hours=hours, min_duration_ms=min_duration_ms, limit=limit)
    return ApiResponse(data=data)


@router.get("/health/postgresql/table-sizes")
async def postgresql_table_sizes(request: Request, limit: int = Query(10, ge=1, le=50)):
    if not _monitor_service:
        return ApiResponse(data=[])
    data = await _monitor_service.get_table_sizes(limit=limit)
    return ApiResponse(data=data)