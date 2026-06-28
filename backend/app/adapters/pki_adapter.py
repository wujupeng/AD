import logging
from typing import Any

from app.interfaces.i_pki_provider import IPkiProvider

logger = logging.getLogger(__name__)


class PkiAdapter(IPkiProvider):
    def __init__(self):
        self._ca_status: dict[str, Any] = {"status": "unknown"}

    async def create_template(self, template_data: dict[str, Any]) -> dict[str, Any]:
        return {"status": "not_implemented", "message": "PKI template management requires AD CS DCOM interface"}

    async def issue_certificate(self, template_name: str, subject: str, requester_sid: str) -> dict[str, Any]:
        return {"status": "not_implemented", "message": "Certificate issuance requires AD CS DCOM interface"}

    async def revoke_certificate(self, serial_number: str, reason: str) -> dict[str, Any]:
        return {"status": "not_implemented", "message": "Certificate revocation requires AD CS DCOM interface"}

    async def renew_certificate(self, serial_number: str) -> dict[str, Any]:
        return {"status": "not_implemented", "message": "Certificate renewal requires AD CS DCOM interface"}

    async def query_expiring_certificates(self, days: int = 30) -> list[dict[str, Any]]:
        return []

    async def query_scep_policies(self) -> list[dict[str, Any]]:
        return []

    async def create_scep_policy(self, policy_data: dict[str, Any]) -> dict[str, Any]:
        return {"status": "not_implemented", "message": "SCEP policy management requires NDES interface"}

    async def query_root_ca_status(self) -> dict[str, Any]:
        return self._ca_status