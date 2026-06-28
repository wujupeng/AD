import logging
import os
import time
from typing import Any

import asyncpg
import httpx


from app.core.config import settings
from app.adapters.redis_cache_adapter import RedisCacheAdapter

logger = logging.getLogger(__name__)

_start_time = time.time()
_request_latencies: list[float] = []

_avg_latency_window: list[float] = []


def record_request_latency(duration_ms: float):
    _avg_latency_window.append(duration_ms)
    if len(_avg_latency_window) > 1000:
        _avg_latency_window.pop(0)


def get_avg_latency_ms() -> float:
    if not _avg_latency_window:
        return 0.0
    return sum(_avg_latency_window) / len(_avg_latency_window)


def get_total_requests() -> int:
    return len(_avg_latency_window)


class SystemMonitorAdapter:
    def __init__(self, cache: RedisCacheAdapter):
        self._cache = cache
        self._pg_pool: asyncpg.Pool | None = None

    async def _get_pg_pool(self) -> asyncpg.Pool:
        if self._pg_pool is None:
            dsn = settings.DATABASE_URL.replace("+asyncpg", "")
            self._pg_pool = await asyncpg.create_pool(dsn, min_size=1, max_size=3)
        return self._pg_pool

    async def close(self):
        if self._pg_pool:
            await self._pg_pool.close()
            self._pg_pool = None

    async def collect_ad_status(self) -> dict[str, Any]:
        try:
            from app.adapters.ldap_adapter import LdapAdapter
            ldap = LdapAdapter()
            connected = await ldap.health_check()
            if not connected:
                return {"status": "offline", "dc_host": "", "fsmo_roles": [], "replication_status": "unavailable", "last_check_time": datetime_utcnow()}
            return {
                "status": "healthy",
                "dc_host": settings.AD_DC_LIST[0] if settings.AD_DC_LIST else "",
                "fsmo_roles": ["PDC", "RID", "Infrastructure", "Schema", "DomainNaming"],
                "replication_status": "normal",
                "replication_delay_seconds": 0,
                "last_check_time": datetime_utcnow(),
            }
        except Exception as e:
            logger.warning(f"AD status collection failed: {e}")
            return {"status": "offline", "dc_host": "", "fsmo_roles": [], "replication_status": "unavailable", "last_check_time": datetime_utcnow()}

    async def collect_postgresql_status(self) -> dict[str, Any]:
        try:
            pool = await self._get_pg_pool()
            async with pool.acquire() as conn:
                active = await conn.fetchval("SELECT count(*) FROM pg_stat_activity WHERE state = 'active'")
                total = await conn.fetchval("SHOW superuser_reserved_connections")
                max_conn = await conn.fetchval("SHOW max_connections")
                max_conn_int = int(max_conn) if max_conn else 100
                usage_pct = round(active / max_conn_int * 100, 1) if max_conn_int > 0 else 0

                slow_queries = []
                try:
                    rows = await conn.fetch(
                        "SELECT query, mean_exec_time, calls FROM pg_stat_statements WHERE mean_exec_time > 1000 ORDER BY mean_exec_time DESC LIMIT 10"
                    )
                    slow_queries = [{"query_text": r["query"][:200], "duration_ms": round(r["mean_exec_time"], 1), "calls": r["calls"]} for r in rows]
                except Exception:
                    pass

                table_sizes = []
                try:
                    rows = await conn.fetch(
                        "SELECT relname as table_name, pg_relation_size(relid) as size_bytes, n_live_tup as row_count FROM pg_stat_user_tables ORDER BY pg_relation_size(relid) DESC LIMIT 10"
                    )
                    table_sizes = [{"table_name": r["table_name"], "size_mb": round(r["size_bytes"] / 1024 / 1024, 2), "row_count": r["row_count"] or 0} for r in rows]
                except Exception:
                    pass

                return {
                    "status": "healthy",
                    "active_connections": active,
                    "max_connections": max_conn_int,
                    "connection_usage_percent": usage_pct,
                    "slow_queries_count": len(slow_queries),
                    "slow_queries": slow_queries,
                    "table_sizes": table_sizes,
                    "last_check_time": datetime_utcnow(),
                }
        except Exception as e:
            logger.warning(f"PostgreSQL status collection failed: {e}")
            return {"status": "error", "active_connections": 0, "max_connections": 0, "connection_usage_percent": 0, "slow_queries": [], "table_sizes": [], "last_check_time": datetime_utcnow()}

    async def collect_redis_status(self) -> dict[str, Any]:
        try:
            client = await self._cache._get_client()
            info_mem = await client.info("memory")
            info_stats = await client.info("stats")
            dbsize = await client.dbsize()

            used_memory_mb = round(info_mem.get("used_memory", 0) / 1024 / 1024, 2)
            max_memory = info_mem.get("maxmemory", 0)
            max_memory_mb = round(max_memory / 1024 / 1024, 2) if max_memory > 0 else 0
            mem_pct = round(used_memory_mb / max_memory_mb * 100, 1) if max_memory_mb > 0 else 0

            hits = info_stats.get("keyspace_hits", 0)
            misses = info_stats.get("keyspace_misses", 0)
            total_access = hits + misses
            hit_rate = round(hits / total_access * 100, 1) if total_access > 0 else 0

            return {
                "status": "healthy",
                "used_memory_mb": used_memory_mb,
                "max_memory_mb": max_memory_mb,
                "memory_usage_percent": mem_pct,
                "hit_rate_percent": hit_rate,
                "total_keys": dbsize,
                "expired_keys": info_stats.get("expired_keys", 0),
                "evicted_keys": info_stats.get("evicted_keys", 0),
                "last_check_time": datetime_utcnow(),
            }
        except Exception as e:
            logger.warning(f"Redis status collection failed: {e}")
            return {"status": "error", "used_memory_mb": 0, "max_memory_mb": 0, "memory_usage_percent": 0, "hit_rate_percent": 0, "total_keys": 0, "expired_keys": 0, "evicted_keys": 0, "last_check_time": datetime_utcnow()}

    async def collect_nginx_status(self) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=5.0, verify=False) as client:
                resp = await client.get(settings.NGINX_STUB_STATUS_URL)
                text = resp.text
                lines = text.strip().split("\n")
                active_conn = int(lines[0].split(":")[1].strip())
                reading, writing, waiting = 0, 0, 0
                for line in lines:
                    if "Reading" in line:
                        parts = line.split()
                        reading = int(parts[1])
                        writing = int(parts[3])
                        waiting = int(parts[5])
                total_requests = 0
                for line in lines:
                    if line.strip().isdigit():
                        total_requests = int(line.strip())

                return {
                    "status": "healthy",
                    "active_connections": active_conn,
                    "reading": reading,
                    "writing": writing,
                    "waiting": waiting,
                    "total_requests": total_requests,
                    "requests_per_second": 0,
                    "last_check_time": datetime_utcnow(),
                }
        except Exception as e:
            logger.warning(f"Nginx status collection failed: {e}")
            return {"status": "unavailable", "active_connections": 0, "reading": 0, "writing": 0, "waiting": 0, "total_requests": 0, "requests_per_second": 0, "last_check_time": datetime_utcnow()}

    async def collect_backend_service_status(self) -> dict[str, Any]:
        try:
            cpu_pct = 0.0
            mem_rss_mb = 0.0
            try:
                pid = os.getpid()
                with open(f"/proc/{pid}/stat", "r") as f:
                    stat = f.read().split()
                    utime = int(stat[13])
                    stime = int(stat[14])
                    total_ticks = utime + stime
                with open("/proc/stat", "r") as f:
                    cpu_line = f.readline().split()
                    total_cpu = sum(int(x) for x in cpu_line[1:])
                with open(f"/proc/{pid}/status", "r") as f:
                    for line in f:
                        if line.startswith("VmRSS:"):
                            mem_rss_mb = int(line.split()[1]) / 1024
                            break
                cpu_pct = round(total_ticks / max(total_cpu, 1) * 100, 1)
            except Exception:
                pass

            uptime_seconds = int(time.time() - _start_time)

            return {
                "status": "healthy",
                "cpu_usage_percent": cpu_pct,
                "memory_rss_mb": round(mem_rss_mb, 2),
                "avg_request_latency_ms": round(get_avg_latency_ms(), 2),
                "total_requests": get_total_requests(),
                "active_requests": 0,
                "uptime_seconds": uptime_seconds,
                "last_check_time": datetime_utcnow(),
            }
        except Exception as e:
            logger.warning(f"Backend service status collection failed: {e}")
            return {"status": "error", "cpu_usage_percent": 0, "memory_rss_mb": 0, "avg_request_latency_ms": 0, "total_requests": 0, "active_requests": 0, "uptime_seconds": 0, "last_check_time": datetime_utcnow()}


def datetime_utcnow() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()