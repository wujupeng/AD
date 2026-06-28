import logging
from typing import Any

from app.interfaces.i_mail_provider import IMailProvider
from app.interfaces.i_cache_provider import ICacheProvider
from app.interfaces.i_audit_provider import IAuditProvider

logger = logging.getLogger(__name__)


class MailService:
    def __init__(
        self,
        mail_provider: IMailProvider,
        cache_provider: ICacheProvider,
        audit_provider: IAuditProvider,
    ):
        self._mail = mail_provider
        self._cache = cache_provider
        self._audit = audit_provider

    async def send_mail(self, from_address: str, to_addresses: list[str], subject: str, body: str, is_html: bool = False) -> dict[str, Any]:
        success = await self._mail.send_mail(from_address, to_addresses, subject, body, is_html)
        return {"success": success}

    async def search_contacts(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        cache_key = f"gal:search:{query}"
        cached = await self._cache.get(cache_key)
        if cached:
            import json
            return json.loads(cached)

        results = await self._mail.search_contacts(query, limit)
        if results:
            await self._cache.set(cache_key, __import__("json").dumps(results), ttl=3600)
        return results

    async def get_freebusy(self, email: str, date_from: str, date_to: str) -> list[dict[str, Any]]:
        return await self._mail.get_freebusy(email, date_from, date_to)