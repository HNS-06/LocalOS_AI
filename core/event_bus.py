import asyncio
import logging
from typing import Callable, Dict, List, Any
from dataclasses import dataclass, field
import time

logger = logging.getLogger("LocalOS.EventBus")

@dataclass
class Event:
    topic: str
    data: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)

class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[Event], Any]]] = {}
        self._async_subscribers: Dict[str, List[Callable[[Event], Any]]] = {}

    def subscribe(self, topic: str, callback: Callable[[Event], Any]):
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        self._subscribers[topic].append(callback)

    def subscribe_async(self, topic: str, callback: Callable[[Event], Any]):
        if topic not in self._async_subscribers:
            self._async_subscribers[topic] = []
        self._async_subscribers[topic].append(callback)

    def publish(self, topic: str, data: Dict[str, Any]):
        event = Event(topic=topic, data=data)
        
        # Synchronous subscribers
        if topic in self._subscribers:
            for cb in self._subscribers[topic]:
                try:
                    cb(event)
                except Exception as e:
                    logger.error(f"Error in sync subscriber for topic {topic}: {e}")
                    
        # Async subscribers
        if topic in self._async_subscribers:
            for cb in self._async_subscribers[topic]:
                try:
                    if asyncio.iscoroutinefunction(cb):
                        asyncio.create_task(cb(event))
                    else:
                        cb(event)
                except Exception as e:
                    logger.error(f"Error in async subscriber for topic {topic}: {e}")

event_bus = EventBus()
