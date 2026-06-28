import logging
from typing import Any

from app.interfaces.i_mail_provider import IMailProvider
from app.core.config import settings

logger = logging.getLogger(__name__)


class ExchangeAdapter(IMailProvider):
    async def send_mail(self, from_address: str, to_addresses: list[str], subject: str, body: str, is_html: bool = False) -> bool:
        logger.info("Exchange send_mail: from=%s, to=%s, subject=%s", from_address, to_addresses, subject)
        try:
            from exchangelib import Account, Message, Mailbox, HTMLBody, Configuration, Credentials

            credentials = Credentials(username=settings.EXCHANGE_USERNAME, password=settings.EXCHANGE_PASSWORD)
            config = Configuration(server=settings.EXCHANGE_SERVER, credentials=credentials)
            account = Account(primary_smtp_address=from_address, config=config, autodiscover=False)

            msg = Message(
                account=account,
                subject=subject,
                body=HTMLBody(body) if is_html else body,
                to_recipients=[Mailbox(email_address=addr) for addr in to_addresses],
            )
            msg.send()
            return True
        except Exception as e:
            logger.error("Exchange send_mail failed: %s", str(e))
            return False

    async def search_contacts(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        logger.info("Exchange search_contacts: query=%s, limit=%d", query, limit)
        from sqlalchemy import select, or_
        from app.models.ad_objects import AdUser
        from app.core.database import async_session_factory
        async with async_session_factory() as session:
            q = select(AdUser).where(AdUser.is_deleted == False, AdUser.is_enabled == True)
            if query and query != "*":
                pattern = f"%{query}%"
                q = q.where(or_(AdUser.username.ilike(pattern), AdUser.display_name.ilike(pattern), AdUser.email.ilike(pattern), AdUser.department.ilike(pattern)))
            q = q.limit(limit)
            result = await session.execute(q)
            users = result.scalars().all()
            return [{"dn": u.dn or "", "display_name": u.display_name or u.username, "email": u.email or "", "department": u.department or "", "title": u.title or "", "phone": u.telephone or "", "site_code": u.site_code or ""} for u in users]

    async def get_freebusy(self, email: str, date_from: str, date_to: str) -> list[dict[str, Any]]:
        logger.info("Exchange get_freebusy: email=%s, from=%s, to=%s", email, date_from, date_to)
        return []