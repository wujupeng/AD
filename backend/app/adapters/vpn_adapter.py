from typing import Any
import httpx


class VpnAdapter:
    def __init__(self, gateway_urls: dict[str, str] | None = None, api_keys: dict[str, str] | None = None):
        self._gateway_urls = gateway_urls or {}
        self._api_keys = api_keys or {}
        self._timeout = httpx.Timeout(connect=5.0, read=10.0, write=10.0, pool=5.0)

    async def _request(self, gateway_name: str, path: str, method: str = "GET", json_data: dict | None = None) -> dict[str, Any]:
        url = self._gateway_urls.get(gateway_name)
        if not url:
            return {"status": "error", "message": f"Gateway {gateway_name} not configured"}
        headers = {}
        api_key = self._api_keys.get(gateway_name)
        if api_key:
            headers["X-API-Key"] = api_key
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.request(method, f"{url}{path}", headers=headers, json=json_data)
                return resp.json()
        except httpx.TimeoutException:
            return {"status": "degraded", "message": f"Gateway {gateway_name} timeout"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def query_gateway_status(self) -> list[dict[str, Any]]:
        results = []
        for gw_name in self._gateway_urls:
            resp = await self._request(gw_name, "/api/status")
            if resp.get("status") not in ("error", "degraded"):
                results.append({"gateway_name": gw_name, **resp})
            else:
                results.append({"gateway_name": gw_name, "health_status": "offline"})
        return results

    async def query_sessions(self, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        results = []
        for gw_name in self._gateway_urls:
            resp = await self._request(gw_name, "/api/sessions", json_data=filters)
            if isinstance(resp, dict) and "sessions" in resp:
                results.extend(resp["sessions"])
        return results

    async def query_device_tunnel_status(self, device_hostname: str) -> dict[str, Any]:
        for gw_name in self._gateway_urls:
            resp = await self._request(gw_name, f"/api/tunnels/device/{device_hostname}")
            if resp.get("status") not in ("error", "degraded"):
                return resp
        return {"status": "not_found", "message": "Device tunnel not found"}

    async def query_user_tunnel_status(self, user_account: str) -> dict[str, Any]:
        for gw_name in self._gateway_urls:
            resp = await self._request(gw_name, f"/api/tunnels/user/{user_account}")
            if resp.get("status") not in ("error", "degraded"):
                return resp
        return {"status": "not_found", "message": "User tunnel not found"}

    async def query_kerberos_recovery_status(self, user_account: str) -> dict[str, Any]:
        return {"status": "not_implemented", "message": "Kerberos recovery requires KDC integration"}

    async def query_audit_log(self, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        results = []
        for gw_name in self._gateway_urls:
            resp = await self._request(gw_name, "/api/audit-log", json_data=filters)
            if isinstance(resp, dict) and "logs" in resp:
                results.extend(resp["logs"])
        return results

    async def update_vpn_policy(self, policy_type: str, config: dict[str, Any]) -> dict[str, Any]:
        for gw_name in self._gateway_urls:
            resp = await self._request(gw_name, "/api/policies", method="PUT", json_data={"policy_type": policy_type, "config": config})
            return resp
        return {"status": "error", "message": "No gateway configured"}