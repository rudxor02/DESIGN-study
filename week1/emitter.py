import asyncio
import logging
from typing import Any, Callable, Coroutine, TypedDict

from pydantic import BaseModel

_logger = logging.getLogger(__name__)


def _is_async(callback: Callable[..., Any]):
    return asyncio.iscoroutinefunction(callback)


class Event(TypedDict):
    name: str


class ClickEvent(Event):
    x: int
    y: int


class CallbackWrapper(BaseModel):
    callback: Callable[..., Coroutine[Any, Any, Any]]
    hash: int
    count: int = -1

    async def execute(self, event: Event):
        await self.callback(event)
        if self.count > 0:
            self.count -= 1

    @property
    def is_valid(self):
        return self.count != 0

    def __hash__(self):
        return hash(hash(self.callback) + self.count)


class EventEmitter(BaseModel):
    listeners: dict[str, set[CallbackWrapper]] = {}

    def _on_count(
        self,
        event_name: str,
        filter: Callable[[Event], bool] = lambda _: True,
        count: int = -1,
    ):
        if event_name not in self.listeners:
            self.listeners[event_name] = set()

        def wrapper(callback: Callable[..., Any]):
            if _is_async(callback):

                async def filter_callback(event: Event):
                    if filter(event):
                        await callback(event)

            else:

                async def filter_callback(event: Event):
                    if filter(event):
                        callback(event)

            self.listeners[event_name].add(
                CallbackWrapper(
                    callback=filter_callback, hash=hash(callback), count=count
                )
            )
            return callback

        return wrapper

    def on(self, event_name: str, filter: Callable[..., bool] = lambda _: True):
        return self._on_count(event_name, filter)

    def once(self, event_name: str, filter: Callable[..., bool] = lambda _: True):
        return self._on_count(event_name, filter, count=1)

    async def _aemit(self, event_name: str, **kwargs: Any) -> None:
        if event_name not in self.listeners.keys():
            _logger.warning(f"Event {event_name} has no listeners")
            return

        await asyncio.gather(
            *[
                callback_wrapper.execute(Event(name=event_name, **kwargs))
                for callback_wrapper in self.listeners[event_name]
            ]
        )

        self.listeners[event_name] = set(
            callback_wrapper
            for callback_wrapper in self.listeners[event_name]
            if callback_wrapper.is_valid
        )

    def emit(self, event_name: str, **kwargs: Any) -> None:
        asyncio.run(self._aemit(event_name, **kwargs))

    def remove_listener(self, event_name: str, callback: Callable[..., Any]) -> int:
        if event_name not in self.listeners.keys():
            raise ValueError(f"Event {event_name} has no listeners")

        callback_wrappers_to_remove = set(
            callback_wrapper
            for callback_wrapper in self.listeners[event_name]
            if callback_wrapper.hash == hash(callback)
        )

        self.listeners[event_name] = set(
            callback_wrapper
            for callback_wrapper in self.listeners[event_name]
            if callback_wrapper not in callback_wrappers_to_remove
        )

        return len(callback_wrappers_to_remove)

    def remove_all_listeners(self, event_name: str) -> int:
        if event_name not in self.listeners.keys():
            raise ValueError(f"Event {event_name} has no listeners")

        callback_wrappers_to_remove = self.listeners[event_name]

        self.listeners[event_name] = set()

        return len(callback_wrappers_to_remove)
