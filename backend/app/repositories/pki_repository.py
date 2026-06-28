from typing import Any
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.pki_management import PkiCertificateTemplate, PkiCertificate, PkiScepPolicy


class PkiRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def list_templates(self) -> list[PkiCertificateTemplate]:
        result = await self._session.execute(select(PkiCertificateTemplate).where(PkiCertificateTemplate.is_enabled == True))
        return list(result.scalars().all())

    async def get_template(self, template_name: str) -> PkiCertificateTemplate | None:
        return await self._session.get(PkiCertificateTemplate, template_name)

    async def create_template(self, data: dict[str, Any]) -> PkiCertificateTemplate:
        template = PkiCertificateTemplate(**data)
        self._session.add(template)
        await self._session.flush()
        return template

    async def update_template(self, template_name: str, data: dict[str, Any]) -> PkiCertificateTemplate | None:
        existing = await self.get_template(template_name)
        if existing:
            for key, value in data.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            await self._session.flush()
        return existing

    async def list_certificates(self, template_name: str | None = None, status: str | None = None, requester_sid: str | None = None) -> list[PkiCertificate]:
        query = select(PkiCertificate)
        if template_name:
            query = query.where(PkiCertificate.template_name == template_name)
        if status:
            query = query.where(PkiCertificate.status == status)
        if requester_sid:
            query = query.where(PkiCertificate.requester_sid == requester_sid)
        result = await self._session.execute(query.order_by(PkiCertificate.not_after))
        return list(result.scalars().all())

    async def get_certificate(self, certificate_id: str) -> PkiCertificate | None:
        return await self._session.get(PkiCertificate, certificate_id)

    async def get_certificate_by_serial(self, serial_number: str) -> PkiCertificate | None:
        result = await self._session.execute(select(PkiCertificate).where(PkiCertificate.serial_number == serial_number))
        return result.scalar_one_or_none()

    async def create_certificate(self, data: dict[str, Any]) -> PkiCertificate:
        cert = PkiCertificate(**data)
        self._session.add(cert)
        await self._session.flush()
        return cert

    async def update_certificate_status(self, serial_number: str, status: str, revocation_reason: str | None = None) -> bool:
        values = {"status": status}
        if revocation_reason:
            values["revocation_reason"] = revocation_reason
        result = await self._session.execute(update(PkiCertificate).where(PkiCertificate.serial_number == serial_number).values(**values))
        return result.rowcount > 0

    async def list_expiring(self, days: int = 30) -> list[PkiCertificate]:
        from sqlalchemy import func
        cutoff = datetime.now(timezone.utc) + __import__("datetime").timedelta(days=days)
        result = await self._session.execute(select(PkiCertificate).where(PkiCertificate.not_after <= cutoff, PkiCertificate.status == "active"))
        return list(result.scalars().all())

    async def list_scep_policies(self) -> list[PkiScepPolicy]:
        result = await self._session.execute(select(PkiScepPolicy).where(PkiScepPolicy.is_enabled == True))
        return list(result.scalars().all())

    async def create_scep_policy(self, data: dict[str, Any]) -> PkiScepPolicy:
        policy = PkiScepPolicy(**data)
        self._session.add(policy)
        await self._session.flush()
        return policy