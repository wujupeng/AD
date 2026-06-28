import logging
from datetime import datetime, timezone
from typing import Any

from app.interfaces.i_entra_id_provider import IEntraIdProvider
from app.interfaces.i_cache_provider import ICacheProvider
from app.interfaces.i_audit_provider import IAuditProvider
from app.repositories.hybrid_identity_repository import HybridIdentityRepository

logger = logging.getLogger(__name__)


class HybridIdentityService:
    def __init__(
        self,
        entra_id_provider: IEntraIdProvider,
        cache_provider: ICacheProvider,
        audit_provider: IAuditProvider,
        hybrid_repo: HybridIdentityRepository,
    ):
        self._entra_id = entra_id_provider
        self._cache = cache_provider
        self._audit = audit_provider
        self._hybrid_repo = hybrid_repo

    async def get_current_phase(self) -> dict[str, Any]:
        config = await self._hybrid_repo.get_current_phase()
        if not config:
            return {"current_phase": "Phase1", "entra_id_sync_status": "not_configured", "intune_compliance_status": "not_configured"}
        return {"id": config.id, "current_phase": config.current_phase, "phase_transition_date": str(config.phase_transition_date) if config.phase_transition_date else None, "entra_id_sync_status": config.entra_id_sync_status, "intune_compliance_status": config.intune_compliance_status}

    async def update_phase(self, new_phase: str) -> dict[str, Any]:
        config = await self._hybrid_repo.get_current_phase()
        if not config:
            return {"error": "No phase config found"}
        if new_phase not in ("Phase1", "Phase2", "Phase3"):
            return {"error": "Invalid phase. Must be Phase1, Phase2, or Phase3"}
        await self._hybrid_repo.update_phase(config.id, {"current_phase": new_phase, "phase_transition_date": datetime.now(timezone.utc)})
        await self._audit.log_event({"event_type": "hybrid_identity", "action": "phase_changed", "details": f"Phase changed to {new_phase}", "result": "success", "occurred_at": datetime.now(timezone.utc)})
        return {"current_phase": new_phase, "status": "updated"}

    async def get_entra_sync_status(self) -> dict[str, Any]:
        config = await self._hybrid_repo.get_current_phase()
        if not config or config.current_phase == "Phase1":
            return {"status": "not_available", "message": "Hybrid identity requires Phase 2 or later"}
        return await self._entra_id.query_sync_status()

    async def get_conditional_access(self) -> list[dict[str, Any]]:
        config = await self._hybrid_repo.get_current_phase()
        if not config or config.current_phase == "Phase1":
            return []
        return await self._entra_id.query_conditional_access()

    async def get_exchange_migration(self) -> dict[str, Any]:
        config = await self._hybrid_repo.get_current_phase()
        if not config or config.current_phase == "Phase1":
            return {"status": "not_available"}
        return await self._entra_id.query_exchange_migration()

    async def get_intune_compliance(self) -> dict[str, Any]:
        config = await self._hybrid_repo.get_current_phase()
        if not config or config.current_phase != "Phase3":
            return {"status": "not_available", "message": "Intune requires Phase 3"}
        return await self._entra_id.query_intune_compliance()