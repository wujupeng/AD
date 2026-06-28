import logging
from datetime import datetime, timezone
from typing import Any

from app.interfaces.i_pki_provider import IPkiProvider
from app.interfaces.i_cache_provider import ICacheProvider
from app.interfaces.i_audit_provider import IAuditProvider
from app.repositories.pki_repository import PkiRepository

logger = logging.getLogger(__name__)


class PkiManagementService:
    def __init__(
        self,
        pki_provider: IPkiProvider,
        cache_provider: ICacheProvider,
        audit_provider: IAuditProvider,
        pki_repo: PkiRepository,
    ):
        self._pki_provider = pki_provider
        self._cache = cache_provider
        self._audit = audit_provider
        self._pki_repo = pki_repo

    async def list_templates(self) -> list[dict[str, Any]]:
        templates = await self._pki_repo.list_templates()
        return [{"template_name": t.template_name, "usage_scenario": t.usage_scenario, "key_length": t.key_length, "validity_period_days": t.validity_period_days, "auto_enrollment": t.auto_enrollment, "description": t.description} for t in templates]

    async def create_template(self, data: dict[str, Any]) -> dict[str, Any]:
        template = await self._pki_repo.create_template(data)
        await self._audit.log_event({"event_type": "pki_operation", "action": "template_created", "resource": data.get("template_name"), "result": "success", "occurred_at": datetime.now(timezone.utc)})
        return {"template_name": template.template_name, "status": "created"}

    async def issue_certificate(self, template_name: str, subject: str, requester_sid: str) -> dict[str, Any]:
        result = await self._pki_provider.issue_certificate(template_name, subject, requester_sid)
        if result.get("status") != "not_implemented":
            await self._pki_repo.create_certificate({"certificate_id": result.get("certificate_id", ""), "template_name": template_name, "subject_name": subject, "serial_number": result.get("serial_number", ""), "not_before": datetime.now(timezone.utc), "not_after": result.get("not_after", datetime.now(timezone.utc)), "status": "active", "requester_sid": requester_sid, "auto_enrollment": False})
        await self._audit.log_event({"event_type": "pki_operation", "action": "cert_issued", "resource": f"{template_name}:{subject}", "user_sid": requester_sid, "result": "success", "occurred_at": datetime.now(timezone.utc)})
        return result

    async def revoke_certificate(self, serial_number: str, reason: str) -> dict[str, Any]:
        result = await self._pki_provider.revoke_certificate(serial_number, reason)
        await self._pki_repo.update_certificate_status(serial_number, "revoked", reason)
        await self._audit.log_event({"event_type": "pki_operation", "action": "cert_revoked", "resource": serial_number, "details": reason, "result": "success", "occurred_at": datetime.now(timezone.utc)})
        return result

    async def renew_certificate(self, serial_number: str) -> dict[str, Any]:
        result = await self._pki_provider.renew_certificate(serial_number)
        await self._audit.log_event({"event_type": "pki_operation", "action": "cert_renewed", "resource": serial_number, "result": "success", "occurred_at": datetime.now(timezone.utc)})
        return result

    async def list_expiring(self, days: int = 30) -> list[dict[str, Any]]:
        certs = await self._pki_repo.list_expiring(days)
        return [{"certificate_id": c.certificate_id, "subject_name": c.subject_name, "serial_number": c.serial_number, "not_after": str(c.not_after), "template_name": c.template_name} for c in certs]

    async def get_root_ca_status(self) -> dict[str, Any]:
        return await self._pki_provider.query_root_ca_status()