import logging
from typing import Any

from app.interfaces.i_entra_id_provider import IEntraIdProvider

logger = logging.getLogger(__name__)


class EntraIdAdapter(IEntraIdProvider):
    def __init__(self):
        self._graph_client = None

    async def authenticate(self, username: str, password: str) -> dict[str, Any]:
        return {"status": "not_configured", "message": "Entra ID not configured. Configure in Phase 2."}

    async def query_sync_status(self) -> dict[str, Any]:
        return {"status": "not_configured", "message": "Entra ID Connect not configured"}

    async def query_conditional_access(self) -> list[dict[str, Any]]:
        return []

    async def query_exchange_migration(self) -> dict[str, Any]:
        return {"status": "not_configured"}

    async def query_intune_compliance(self) -> dict[str, Any]:
        return {"status": "not_configured", "message": "Intune not configured. Configure in Phase 3."}