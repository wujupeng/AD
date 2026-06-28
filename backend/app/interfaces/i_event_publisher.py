from abc import ABC, abstractmethod
from typing import Any, Callable


class IEventPublisher(ABC):
    @abstractmethod
    async def publish(self, topic: str, payload: dict[str, Any]) -> bool:
        ...

    @abstractmethod
    async def subscribe(self, topic: str, callback: Callable[[dict[str, Any]], Any]) -> None:
        ...