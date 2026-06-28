from fastapi import APIRouter, Request

from app.schemas.response import ApiResponse

router = APIRouter(prefix="/v1/enterprise/secure-print", tags=["Secure Print / Follow-Me Printing"])


@router.get("/jobs")
async def list_jobs(request: Request, owner_account: str | None = None, job_status: str | None = None):
    from app.core.deps import get_secure_print_service
    svc = get_secure_print_service(request)
    result = await svc.list_jobs(owner_account, job_status)
    return ApiResponse(data=result)


@router.post("/jobs/submit")
async def submit_job(request: Request):
    body = await request.json()
    from app.core.deps import get_secure_print_service
    svc = get_secure_print_service(request)
    result = await svc.submit_job(
        owner_account=body["owner_account"], owner_sid=body.get("owner_sid"),
        document_name=body.get("document_name"), pages=body.get("pages", 0),
        copies=body.get("copies", 1), color_mode=body.get("color_mode", "color"),
        duplex=body.get("duplex", True), client_ip=body.get("client_ip"),
        client_site=body.get("client_site"),
    )
    return ApiResponse(data=result)


@router.post("/jobs/{job_id}/release")
async def release_job(request: Request, job_id: str):
    body = await request.json()
    from app.core.deps import get_secure_print_service
    svc = get_secure_print_service(request)
    result = await svc.release_job(job_id, body["ad_account"], body["printer_name"])
    return ApiResponse(data=result)


@router.post("/jobs/{job_id}/cancel")
async def cancel_job(request: Request, job_id: str):
    body = await request.json()
    from app.core.deps import get_secure_print_service
    svc = get_secure_print_service(request)
    result = await svc.cancel_job(job_id, body["ad_account"])
    return ApiResponse(data=result)


@router.get("/cluster-status")
async def get_cluster_status(request: Request):
    from app.core.deps import get_secure_print_service
    svc = get_secure_print_service(request)
    result = await svc.get_cluster_status()
    return ApiResponse(data=result)


@router.get("/mfp-printers")
async def list_mfp_printers(request: Request, site: str | None = None):
    from app.core.deps import get_secure_print_service
    svc = get_secure_print_service(request)
    result = await svc.list_mfp_printers(site)
    return ApiResponse(data=result)


@router.post("/mfp-printers")
async def register_mfp_printer(request: Request):
    body = await request.json()
    from app.core.deps import get_secure_print_service
    svc = get_secure_print_service(request)
    from app.repositories.secure_print_repository import MfpPrinterRepository
    from app.core.database import async_session_factory
    mfp_repo = MfpPrinterRepository(async_session_factory())
    printer = await mfp_repo.create_printer(body)
    return ApiResponse(data={"printer_name": printer.printer_name, "status": "registered"})


@router.get("/card-mappings")
async def list_card_mappings(request: Request):
    from app.core.deps import get_secure_print_service
    svc = get_secure_print_service(request)
    result = await svc.list_card_mappings()
    return ApiResponse(data=result)


@router.post("/card-mappings")
async def create_card_mapping(request: Request):
    body = await request.json()
    from app.core.deps import get_secure_print_service
    svc = get_secure_print_service(request)
    result = await svc.create_card_mapping(body["card_id"], body.get("card_type", "mifare"), body["ad_account"])
    return ApiResponse(data=result)


@router.post("/card-mappings/batch-import")
async def batch_import_card_mappings(request: Request):
    body = await request.json()
    from app.core.deps import get_secure_print_service
    svc = get_secure_print_service(request)
    result = await svc.batch_import_card_mappings(body["mappings"])
    return ApiResponse(data=result)


@router.get("/audit/statistics")
async def get_print_statistics(request: Request, user_account: str | None = None, site: str | None = None, date_from: str | None = None, date_to: str | None = None):
    from app.core.deps import get_secure_print_service
    svc = get_secure_print_service(request)
    result = await svc.get_print_statistics(user_account, site, date_from, date_to)
    return ApiResponse(data=result)


@router.post("/mfp/authenticate")
async def mfp_card_authenticate(request: Request):
    body = await request.json()
    from app.core.deps import get_secure_print_service
    svc = get_secure_print_service(request)
    result = await svc.card_authenticate(body["card_id"], body.get("printer_name", ""))
    return ApiResponse(data=result)


@router.get("/mfp/user-jobs")
async def mfp_user_jobs(request: Request, ad_account: str):
    from app.core.deps import get_secure_print_service
    svc = get_secure_print_service(request)
    result = await svc.list_jobs(owner_account=ad_account, job_status="queued")
    return ApiResponse(data=result)


@router.post("/mfp/release")
async def mfp_release_job(request: Request):
    body = await request.json()
    from app.core.deps import get_secure_print_service
    svc = get_secure_print_service(request)
    result = await svc.release_job(body["job_id"], body["ad_account"], body["printer_name"])
    return ApiResponse(data=result)


@router.post("/mfp/heartbeat")
async def mfp_heartbeat(request: Request):
    body = await request.json()
    from app.core.deps import get_secure_print_service
    svc = get_secure_print_service(request)
    result = await svc.mfp_heartbeat(body["printer_name"])
    return ApiResponse(data={"success": result})