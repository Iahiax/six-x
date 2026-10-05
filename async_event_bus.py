import asyncio
import logging
from typing import Callable, Dict, List, Any

logger = logging.getLogger("AsyncEventBus")

class Event:
    def __init__(self, event_type: str, data: Dict[str, Any]):
        self.event_type = event_type
        self.data = data
        self.timestamp = asyncio.get_event_loop().time()

class AsyncEventBus:
    """
    ناقل الأحداث غير المتزامن عالي السرعة
    """
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, callback: Callable):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    async def publish(self, event: Event):
        if event.event_type in self._subscribers:
            tasks = [asyncio.create_task(callback(event.data)) for callback in self._subscribers[event.event_type]]
            await asyncio.gather(*tasks, return_exceptions=True)
