import logging
import uuid
from datetime import datetime, timezone, timedelta
from typing import Any

from app.interfaces.i_secure_print_provider import ISecurePrintProvider, ICardMappingProvider, IPrintAuditProvider
from app.interfaces.i_ldap_provider import ILdapProvider
from app.interfaces.i_cache_provider import ICacheProvider
from app.interfaces.i_audit_provider import IAuditProvider
from app.repositories.secure_print_repository import SecurePrintJobRepository, CardMappingRepository, MfpPrinterRepository, PrintAuditRepository

logger = logging.getLogger(__name__)


class SecurePrintService:
    def __init__(
        self,
        secure_print_provider: ISecurePrintProvider,
        card_mapping_provider: ICardMappingProvider,
        print_audit_provider: IPrintAuditProvider,
        ldap_provider: ILdapProvider,
        cache_provider: ICacheProvider,
        audit_provider: IAuditProvider,
        job_repo: SecurePrintJobRepository,
        card_repo: CardMappingRepository,
        mfp_repo: MfpPrinterRepository,
        audit_repo: PrintAuditRepository,
    ):
        self._sp = secure_print_provider
        self._card = card_mapping_provider
        self._print_audit = print_audit_provider
        self._ldap = ldap_provider
        self._cache = cache_provider
        self._audit = audit_provider
        self._job_repo = job_repo
        self._card_repo = card_repo
        self._mfp_repo = mfp_repo
        self._audit_repo = audit_repo

    async def submit_job(self, owner_account: str, owner_sid: str | None, document_name: str | None, pages: int, copies: int, color_mode: str, duplex: bool, client_ip: str | None, client_site: str | None) -> dict[str, Any]:
        job_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(hours=24)
        job_data = {
            "job_id": job_id, "owner_account": owner_account, "owner_sid": owner_sid,
            "document_name": document_name, "pages": pages, "copies": copies,
            "color_mode": color_mode, "duplex": duplex, "job_status": "queued",
            "submitted_at": now, "expires_at": expires_at,
            "client_ip": client_ip, "client_site": client_site,
        }
        job = await self._job_repo.create_job(job_data)
        await self._audit_repo.record_operation({
            "audit_id": str(uuid.uuid4()), "operation_type": "submit", "job_id": job_id,
            "user_account": owner_account, "user_sid": owner_sid,
            "page_count": pages * copies, "color_mode": color_mode, "duplex": duplex,
            "site": client_site, "occurred_at": now,
        })
        return {"job_id": job_id, "status": "queued", "expires_at": str(expires_at)}

    async def card_authenticate(self, card_id: str, printer_name: str) -> dict[str, Any]:
        mapping = await self._card_repo.resolve_card(card_id)
        if not mapping:
            return {"success": False, "error": "CARD_NOT_REGISTERED"}
        if not mapping.is_active:
            return {"success": False, "error": "CARD_DEACTIVATED"}
        ad_account = mapping.ad_account
        try:
            user_attrs = await self._ldap.get_user_attributes(f"CN={ad_account.split('@')[0] if '@' in ad_account else ad_account},CN=Users,DC=company,DC=local")
            uac = user_attrs.get("userAccountControl", [512])
            if isinstance(uac, list):
                uac = uac[0] if uac else 512
            if uac & 0x0002:
                return {"success": False, "error": "ACCOUNT_DISABLED"}
        except Exception:
            return {"success": False, "error": "AD_UNREACHABLE"}
        jobs = await self._job_repo.list_jobs(owner_account=ad_account, job_status="queued")
        return {"success": True, "ad_account": ad_account, "pending_jobs": [{"job_id": j.job_id, "document_name": j.document_name, "pages": j.pages, "color_mode": j.color_mode, "submitted_at": str(j.submitted_at)} for j in jobs]}

    async def release_job(self, job_id: str, ad_account: str, printer_name: str) -> dict[str, Any]:
        job = await self._job_repo.get_job(job_id)
        if not job:
            return {"success": False, "error": "JOB_NOT_FOUND"}
        if job.job_status != "queued":
            return {"success": False, "error": "JOB_NOT_QUEUED"}
        if job.owner_account != ad_account:
            return {"success": False, "error": "JOB_NOT_OWNED"}
        printer = await self._mfp_repo.get_printer(printer_name)
        site = printer.site if printer else None
        await self._job_repo.update_job_status(job_id, "released", released_by=ad_account, released_printer=printer_name, released_site=site)
        await self._sp.release_job(job_id, printer_name)
        await self._audit_repo.record_operation({
            "audit_id": str(uuid.uuid4()), "operation_type": "release", "job_id": job_id,
            "user_account": ad_account, "printer_name": printer_name, "site": site,
            "page_count": job.pages * job.copies, "color_mode": job.color_mode, "duplex": job.duplex,
            "occurred_at": datetime.now(timezone.utc),
        })
        return {"success": True, "job_id": job_id, "printer_name": printer_name}

    async def cancel_job(self, job_id: str, ad_account: str) -> dict[str, Any]:
        job = await self._job_repo.get_job(job_id)
        if not job:
            return {"success": False, "error": "JOB_NOT_FOUND"}
        if job.owner_account != ad_account:
            return {"success": False, "error": "JOB_NOT_OWNED"}
        await self._job_repo.update_job_status(job_id, "cancelled")
        return {"success": True, "job_id": job_id}

    async def list_jobs(self, owner_account: str | None = None, job_status: str | None = None) -> list[dict[str, Any]]:
        jobs = await self._job_repo.list_jobs(owner_account, job_status)
        return [{"job_id": j.job_id, "owner_account": j.owner_account, "document_name": j.document_name, "pages": j.pages, "job_status": j.job_status, "submitted_at": str(j.submitted_at), "expires_at": str(j.expires_at)} for j in jobs]

    async def cleanup_expired_jobs(self) -> int:
        expired = await self._job_repo.list_expired_jobs()
        for job in expired:
            await self._job_repo.update_job_status(job.job_id, "expired")
        return len(expired)

    async def disable_account_jobs(self, ad_account: str) -> int:
        return await self._job_repo.delete_jobs_by_owner(ad_account)

    async def list_mfp_printers(self, site: str | None = None) -> list[dict[str, Any]]:
        printers = await self._mfp_repo.list_printers(site)
        return [{"printer_name": p.printer_name, "site": p.site, "ip_address": p.ip_address, "printer_brand": p.printer_brand, "auth_protocols": p.auth_protocols, "card_reader_type": p.card_reader_type, "is_active": p.is_active} for p in printers]

    async def list_card_mappings(self) -> list[dict[str, Any]]:
        mappings = await self._card_repo.list_mappings()
        return [{"card_id": m.card_id, "card_type": m.card_type, "ad_account": m.ad_account, "is_active": m.is_active, "last_used_at": str(m.last_used_at) if m.last_used_at else None} for m in mappings]

    async def create_card_mapping(self, card_id: str, card_type: str, ad_account: str) -> dict[str, Any]:
        mapping = await self._card_repo.create_mapping({"card_id": card_id, "card_type": card_type, "ad_account": ad_account})
        return {"card_id": mapping.card_id, "ad_account": mapping.ad_account, "status": "created"}

    async def batch_import_card_mappings(self, mappings: list[dict[str, Any]]) -> dict[str, Any]:
        count = await self._card_repo.batch_create(mappings)
        return {"imported": count, "total": len(mappings)}

    async def get_print_statistics(self, user_account: str | None = None, site: str | None = None, date_from: str | None = None, date_to: str | None = None) -> dict[str, Any]:
        return await self._audit_repo.query_statistics(user_account, site, date_from, date_to)

    async def get_cluster_status(self) -> dict[str, Any]:
        return await self._sp.query_cluster_status()

    async def mfp_heartbeat(self, printer_name: str) -> bool:
        return await self._mfp_repo.update_heartbeat(printer_name)