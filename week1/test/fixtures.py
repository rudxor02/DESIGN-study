import pytest

from week1.emitter import EventEmitter


@pytest.fixture(scope="function")
def emitter():
    return EventEmitter()
