from fastapi import APIRouter, Request

from app.schemas.response import ApiResponse

router = APIRouter(prefix="/v1/enterprise/monitoring", tags=["Monitoring & Alerts"])


@router.get("/alerts")
async def list_alerts(request: Request, severity: str | None = None, category: str | None = None, acknowledged: bool | None = None):
    from app.core.deps import get_monitoring_alert_service
    svc = get_monitoring_alert_service(request)
    result = await svc.list_alerts(severity, category, acknowledged)
    return ApiResponse(data=result)


@router.put("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(request: Request, alert_id: str):
    from app.core.deps import get_monitoring_alert_service
    svc = get_monitoring_alert_service(request)
    result = await svc.acknowledge_alert(alert_id)
    return ApiResponse(data={"acknowledged": result})


@router.get("/grafana-dashboards")
async def get_grafana_dashboards(request: Request):
    from app.core.deps import get_monitoring_alert_service
    svc = get_monitoring_alert_service(request)
    result = await svc.get_grafana_dashboards()
    return ApiResponse(data=result)


@router.get("/backup-status")
async def get_backup_status(request: Request):
    from app.core.deps import get_monitoring_alert_service
    svc = get_monitoring_alert_service(request)
    result = await svc.get_backup_status()
    return ApiResponse(data=result)


@router.get("/alert-config")
async def get_alert_notification_configs(request: Request):
    from app.core.deps import get_monitoring_alert_service
    svc = get_monitoring_alert_service(request)
    result = await svc.get_alert_notification_configs()
    return ApiResponse(data=result)