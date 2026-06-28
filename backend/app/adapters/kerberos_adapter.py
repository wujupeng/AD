import logging
from typing import Any

from app.interfaces.i_kerberos_provider import IKerberosProvider

logger = logging.getLogger(__name__)


class KerberosAdapter(IKerberosProvider):
    async def validate_ticket(self, ticket: bytes, service_principal: str) -> dict[str, Any]:
        try:
            import gssapi

            name = gssapi.Name(service_principal, name_type=gssapi.NameType.kerberos_principal)
            server_creds = gssapi.Credentials(name=name, usage="accept")
            ctx = gssapi.SecurityContext(creds=server_creds)

            dec_ticket = ctx.step(ticket)
            if not ctx.complete:
                return {"valid": False, "error": "AUTH_TICKET_INVALID"}

            principal = str(ctx.initiator_name)
            return {
                "valid": True,
                "principal": principal,
                "auth_time": ctx.auth_time if hasattr(ctx, "auth_time") else None,
            }
        except Exception as e:
            logger.error("Kerberos ticket validation failed: %s", str(e))
            return {"valid": False, "error": "AUTH_TICKET_INVALID"}

    async def extract_principal(self, ticket: bytes) -> str:
        result = await self.validate_ticket(ticket, "")
        return result.get("principal", "")