import json
import logging
from typing import Any, Callable

import redis.asyncio as aioredis

from app.interfaces.i_cache_provider import ICacheProvider
from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisCacheAdapter(ICacheProvider):
    def __init__(self):
        self._client: aioredis.Redis | None = None

    async def _get_client(self) -> aioredis.Redis:
        if self._client is None:
            self._client = aioredis.from_url(
                settings.REDIS_URL,
                password=settings.REDIS_PASSWORD,
                decode_responses=True,
            )
        return self._client

    async def get(self, key: str) -> str | None:
        client = await self._get_client()
        return await client.get(key)

    async def set(self, key: str, value: str, ttl: int | None = None) -> bool:
        client = await self._get_client()
        if ttl:
            await client.setex(key, ttl, value)
        else:
            await client.set(key, value)
        return True

    async def delete(self, key: str) -> bool:
        client = await self._get_client()
        await client.delete(key)
        return True

    async def get_hash(self, name: str, key: str) -> str | None:
        client = await self._get_client()
        return await client.hget(name, key)

    async def set_hash(self, name: str, key: str, value: str) -> bool:
        client = await self._get_client()
        await client.hset(name, key, value)
        return True

    async def publish(self, channel: str, message: str) -> int:
        client = await self._get_client()
        return await client.publish(channel, message)

    async def subscribe(self, channel: str, callback: Callable) -> None:
        client = await self._get_client()
        pubsub = client.pubsub()
        await pubsub.subscribe(channel)
        async for message in pubsub.listen():
            if message["type"] == "message":
                data = json.loads(message["data"])
                await callback(data)

    async def mark_dc_down(self, dc_hostname: str, ttl: int = 300) -> bool:
        client = await self._get_client()
        await client.setex(f"dc_health:{dc_hostname}", ttl, "down")
        return True

    async def get_dc_health(self, dc_hostname: str) -> dict[str, Any] | None:
        client = await self._get_client()
        status = await client.get(f"dc_health:{dc_hostname}")
        if status:
            return {"hostname": dc_hostname, "status": status}
        return None