import json
import logging
from typing import Any, Callable

from app.interfaces.i_cache_provider import ICacheProvider

logger = logging.getLogger(__name__)

EVENT_TOPICS = {
    "OU_CREATED": "org.ou.created",
    "OU_UPDATED": "org.ou.updated",
    "OU_DELETED": "org.ou.deleted",
    "USER_CREATED": "org.user.created",
    "USER_UPDATED": "org.user.updated",
    "USER_DELETED": "org.user.deleted",
    "GROUP_UPDATED": "org.group.updated",
    "SESSION_TERMINATED": "auth.session.terminated",
    "PERMISSION_CHANGED": "permission.changed",
}


class EventBusService:
    def __init__(self, cache_provider: ICacheProvider):
        self._cache = cache_provider
        self._subscribers: dict[str, list[Callable]] = {}

    async def publish(self, event_type: str, payload: dict[str, Any]) -> bool:
        topic = EVENT_TOPICS.get(event_type, f"custom.{event_type.lower()}")
        message = json.dumps({"event_type": event_type, "payload": payload})
        count = await self._cache.publish(topic, message)

        if topic in self._subscribers:
            for callback in self._subscribers[topic]:
                try:
                    await callback(payload)
                except Exception as e:
                    logger.error("Event callback error for %s: %s", topic, str(e))

        return count > 0

    async def subscribe(self, event_type: str, callback: Callable[[dict[str, Any]], Any]) -> None:
        topic = EVENT_TOPICS.get(event_type, f"custom.{event_type.lower()}")
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        self._subscribers[topic].append(callback)