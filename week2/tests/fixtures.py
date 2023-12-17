import pytest

from week2.nestpy.common import Injectable, InstanceInitiator


@pytest.fixture(scope="function")
def instance_initiator():
    return InstanceInitiator()


@pytest.fixture(scope="function")
def test_service1_cls():
    @Injectable()
    class TestService1:
        def __init__(self):
            pass

    return TestService1


@pytest.fixture(scope="function")
def test_service2_cls(test_service1_cls: type):
    @Injectable()
    class TestService2:
        def __init__(self, service: test_service1_cls):
            pass

    return TestService2


@pytest.fixture(scope="function")
def test_service3_cls(test_service2_cls: type, test_service1_cls: type):
    @Injectable()
    class TestService3:
        def __init__(self, service1: test_service1_cls, service2: test_service2_cls):
            pass

    return TestService3
