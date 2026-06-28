import asyncio
import json
import logging
from typing import Any
from datetime import datetime, timezone

from app.adapters.system_monitor_adapter import SystemMonitorAdapter
from app.adapters.redis_cache_adapter import RedisCacheAdapter

logger = logging.getLogger(__name__)

_CACHE_KEY = "sysmon:health_detail"
_CACHE_TTL = 10


class SystemMonitorService:
    def __init__(self, monitor_adapter: SystemMonitorAdapter, cache: RedisCacheAdapter):
        self._monitor = monitor_adapter
        self._cache = cache

    async def get_health_detail(self) -> dict[str, Any]:
        try:
            cached = await self._cache.get(_CACHE_KEY)
            if cached:
                return json.loads(cached)
        except Exception:
            pass

        results = await asyncio.gather(
            self._monitor.collect_ad_status(),
            self._monitor.collect_postgresql_status(),
            self._monitor.collect_redis_status(),
            self._monitor.collect_nginx_status(),
            self._monitor.collect_backend_service_status(),
            return_exceptions=True,
        )

        components: dict[str, Any] = {}
        component_names = ["ad_domain_controller", "postgresql", "redis", "nginx", "backend_service"]
        for name, result in zip(component_names, results):
            if isinstance(result, Exception):
                components[name] = {"status": "error", "error": str(result)}
            else:
                components[name] = result

        overall = "healthy"
        pg_status = components.get("postgresql", {}).get("status", "error")
        redis_status = components.get("redis", {}).get("status", "error")
        if pg_status in ("error",) or redis_status in ("error",):
            overall = "unhealthy"
        elif any(v.get("status") in ("error", "offline", "unavailable") for v in components.values()):
            overall = "degraded"

        response = {
            "status": overall,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "components": components,
        }

        try:
            await self._cache.set(_CACHE_KEY, json.dumps(response, default=str), ttl=_CACHE_TTL)
        except Exception:
            pass

        return response

    async def get_slow_queries(self, hours: int = 24, min_duration_ms: int = 1000, limit: int = 20) -> list[dict[str, Any]]:
        detail = await self.get_health_detail()
        pg = detail.get("components", {}).get("postgresql", {})
        queries = pg.get("slow_queries", [])
        return [q for q in queries if q.get("duration_ms", 0) >= min_duration_ms][:limit]

    async def get_table_sizes(self, limit: int = 10) -> list[dict[str, Any]]:
        detail = await self.get_health_detail()
        pg = detail.get("components", {}).get("postgresql", {})
        return pg.get("table_sizes", [])[:limit]