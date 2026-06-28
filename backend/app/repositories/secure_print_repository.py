from typing import Any
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from app.models.secure_print import SecurePrintJob, CardAccountMapping, MfpPrinter, PrintAuditRecord


class SecurePrintJobRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def list_jobs(self, owner_account: str | None = None, job_status: str | None = None) -> list[SecurePrintJob]:
        query = select(SecurePrintJob).order_by(SecurePrintJob.submitted_at.desc())
        if owner_account:
            query = query.where(SecurePrintJob.owner_account == owner_account)
        if job_status:
            query = query.where(SecurePrintJob.job_status == job_status)
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def get_job(self, job_id: str) -> SecurePrintJob | None:
        return await self._session.get(SecurePrintJob, job_id)

    async def create_job(self, data: dict[str, Any]) -> SecurePrintJob:
        job = SecurePrintJob(**data)
        self._session.add(job)
        await self._session.flush()
        return job

    async def update_job_status(self, job_id: str, status: str, released_by: str | None = None, released_printer: str | None = None, released_site: str | None = None) -> bool:
        values = {"job_status": status}
        if status == "released":
            values["released_at"] = datetime.now(timezone.utc)
            values["released_by"] = released_by
            values["released_printer"] = released_printer
            values["released_site"] = released_site
        result = await self._session.execute(update(SecurePrintJob).where(SecurePrintJob.job_id == job_id).values(**values))
        return result.rowcount > 0

    async def list_expired_jobs(self) -> list[SecurePrintJob]:
        now = datetime.now(timezone.utc)
        result = await self._session.execute(select(SecurePrintJob).where(SecurePrintJob.job_status == "queued", SecurePrintJob.expires_at <= now))
        return list(result.scalars().all())

    async def delete_jobs_by_owner(self, owner_account: str) -> int:
        from sqlalchemy import delete
        result = await self._session.execute(delete(SecurePrintJob).where(SecurePrintJob.owner_account == owner_account, SecurePrintJob.job_status == "queued"))
        return result.rowcount


class CardMappingRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def resolve_card(self, card_id: str) -> CardAccountMapping | None:
        result = await self._session.execute(select(CardAccountMapping).where(CardAccountMapping.card_id == card_id, CardAccountMapping.is_active == True))
        return result.scalar_one_or_none()

    async def list_mappings(self) -> list[CardAccountMapping]:
        result = await self._session.execute(select(CardAccountMapping))
        return list(result.scalars().all())

    async def create_mapping(self, data: dict[str, Any]) -> CardAccountMapping:
        mapping = CardAccountMapping(**data)
        self._session.add(mapping)
        await self._session.flush()
        return mapping

    async def deactivate_mapping(self, card_id: str) -> bool:
        result = await self._session.execute(update(CardAccountMapping).where(CardAccountMapping.card_id == card_id).values(is_active=False))
        return result.rowcount > 0

    async def batch_create(self, mappings: list[dict[str, Any]]) -> int:
        count = 0
        for m in mappings:
            existing = await self.resolve_card(m.get("card_id", ""))
            if not existing:
                mapping = CardAccountMapping(**m)
                self._session.add(mapping)
                count += 1
        await self._session.flush()
        return count


class MfpPrinterRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def list_printers(self, site: str | None = None) -> list[MfpPrinter]:
        query = select(MfpPrinter).where(MfpPrinter.is_active == True)
        if site:
            query = query.where(MfpPrinter.site == site)
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def get_printer(self, printer_name: str) -> MfpPrinter | None:
        return await self._session.get(MfpPrinter, printer_name)

    async def create_printer(self, data: dict[str, Any]) -> MfpPrinter:
        printer = MfpPrinter(**data)
        self._session.add(printer)
        await self._session.flush()
        return printer

    async def update_heartbeat(self, printer_name: str) -> bool:
        result = await self._session.execute(update(MfpPrinter).where(MfpPrinter.printer_name == printer_name).values(last_heartbeat=datetime.now(timezone.utc)))
        return result.rowcount > 0


class PrintAuditRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def record_operation(self, data: dict[str, Any]) -> PrintAuditRecord:
        record = PrintAuditRecord(**data)
        self._session.add(record)
        await self._session.flush()
        return record

    async def query_statistics(self, user_account: str | None = None, site: str | None = None, date_from: str | None = None, date_to: str | None = None) -> dict[str, Any]:
        query = select(PrintAuditRecord)
        if user_account:
            query = query.where(PrintAuditRecord.user_account == user_account)
        if site:
            query = query.where(PrintAuditRecord.site == site)
        result = await self._session.execute(query.order_by(PrintAuditRecord.occurred_at.desc()).limit(1000))
        records = list(result.scalars().all())
        total_pages = sum(r.page_count or 0 for r in records)
        return {"total_operations": len(records), "total_pages": total_pages, "records": [{"audit_id": r.audit_id, "operation_type": r.operation_type, "user_account": r.user_account, "printer_name": r.printer_name, "site": r.site, "page_count": r.page_count, "occurred_at": str(r.occurred_at)} for r in records]}