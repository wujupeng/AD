from typing import Any


class DefenderAdapter:
    def __init__(self, tenant_id: str = "", client_id: str = "", client_secret: str = ""):
        self._tenant_id = tenant_id
        self._client_id = client_id
        self._client_secret = client_secret

    async def query_defender_status(self, device_hostname: str) -> dict[str, Any]:
        return {"status": "not_configured", "message": "Defender for Endpoint integration not configured", "device_hostname": device_hostname}

    async def query_device_onboarding(self) -> dict[str, Any]:
        return {"status": "not_configured", "total_devices": 0, "onboarded": 0, "not_onboarded": 0}

    async def query_threat_alerts(self, severity: str | None = None) -> list[dict[str, Any]]:
        return []

    async def query_device_risk_score(self, device_hostname: str) -> dict[str, Any]:
        return {"status": "not_configured", "device_hostname": device_hostname, "risk_level": "unknown"}

    async def query_signature_status(self) -> dict[str, Any]:
        return {"status": "not_configured", "up_to_date": 0, "outdated": 0}