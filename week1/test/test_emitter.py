import asyncio
import logging

import pytest

from week1.emitter import ClickEvent, Event, EventEmitter

_logger = logging.getLogger(__name__)


@pytest.mark.event_emitter
class TestEventEmitter:
    def test_on(self, emitter: EventEmitter):
        flag_a = False
        event_a = None

        @emitter.on("test_event")
        def _a(event: Event):
            nonlocal flag_a
            nonlocal event_a
            flag_a = True if not flag_a else False
            event_a = event

        assert len(emitter.listeners["test_event"]) == 1

        kwargs = {"a": 1, "b": 2}
        emitter.emit("test_event", **kwargs)
        assert flag_a is True
        assert event_a == {"name": "test_event", **kwargs}

    def test_filter(self, emitter: EventEmitter):
        flag_a = False
        flag_b = False

        @emitter.on("click")
        def _a(event: ClickEvent):
            nonlocal flag_a
            flag_a = True if not flag_a else False

        @emitter.on("click", filter=lambda event: event["name"] == "random")
        def _b(event: ClickEvent):
            nonlocal flag_b
            flag_b = True if not flag_b else False

        assert len(emitter.listeners["click"]) == 2
        emitter.emit("click")
        assert flag_a is True
        assert flag_b is False

    def test_async_on(self, emitter: EventEmitter):
        flag_a = False

        @emitter.on("test_event")
        async def _a(event: Event):
            nonlocal flag_a
            await asyncio.sleep(1)
            flag_a = True if not flag_a else False

        assert len(emitter.listeners["test_event"]) == 1
        emitter.emit("test_event")
        assert flag_a is True

    def test_once(self, emitter: EventEmitter):
        flag_a = False
        flag_b = False

        @emitter.once("test_event")
        def _a(event: Event):
            nonlocal flag_a
            flag_a = True if not flag_a else False

        @emitter.on("test_event")
        def _b(event: Event):
            nonlocal flag_b
            flag_b = True if not flag_b else False

        assert len(emitter.listeners["test_event"]) == 2
        emitter.emit("test_event")
        assert flag_a is True
        assert flag_b is True
        assert len(emitter.listeners["test_event"]) == 1
        emitter.emit("test_event")
        assert flag_a is True
        assert flag_b is False

    def test_remove_listener(self, emitter: EventEmitter):
        flag_a = False
        flag_b = False

        @emitter.on("test_event")
        def _a(event: Event):
            nonlocal flag_a
            flag_a = True if not flag_a else False

        @emitter.on("test_event")
        def _b(event: Event):
            nonlocal flag_b
            flag_b = True if not flag_b else False

        assert len(emitter.listeners["test_event"]) == 2
        emitter.emit("test_event")
        assert flag_a is True
        assert flag_b is True
        emitter.remove_listener("test_event", _a)
        assert len(emitter.listeners["test_event"]) == 1
        emitter.emit("test_event")
        assert flag_a is True
        assert flag_b is False

    def test_remove_all_listeners(self, emitter: EventEmitter):
        flag_a = False
        flag_b = False

        @emitter.on("test_event")
        def _a(event: Event):
            nonlocal flag_a
            flag_a = True if not flag_a else False

        @emitter.on("test_event")
        def _b(event: Event):
            nonlocal flag_b
            flag_b = True if not flag_b else False

        assert len(emitter.listeners["test_event"]) == 2
        emitter.emit("test_event")
        assert flag_a is True
        assert flag_b is True
        emitter.remove_all_listeners("test_event")
        assert len(emitter.listeners["test_event"]) == 0
        emitter.emit("test_event")
        assert flag_a is True
        assert flag_b is True
