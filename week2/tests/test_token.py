import logging

import pytest
from nestpy.common import InstanceInitiator

_logger = logging.getLogger(__name__)


@pytest.mark.token
class TestToken:
    def test_register_undecorated_class(
        self,
        instance_initiator: InstanceInitiator,
    ):
        class UndecoratedClass:
            pass

        with pytest.raises(ValueError):
            instance_initiator.register_cls(UndecoratedClass)

    def test_register_2classes(
        self,
        instance_initiator: InstanceInitiator,
        test_service1_cls: type,
        test_service2_cls: type,
    ):
        instance_initiator.register_cls(test_service2_cls)
        assert instance_initiator._instance_manager.get_wrapper(test_service1_cls)
        assert instance_initiator._instance_manager.get_wrapper(test_service2_cls)

    def test_register_3classes(
        self,
        instance_initiator: InstanceInitiator,
        test_service1_cls: type,
        test_service2_cls: type,
        test_service3_cls: type,
    ):
        instance_initiator.register_cls(test_service3_cls)
        assert instance_initiator._instance_manager.get_wrapper(test_service1_cls)
        assert instance_initiator._instance_manager.get_wrapper(test_service2_cls)
        assert instance_initiator._instance_manager.get_wrapper(test_service3_cls)

    def test_register_and_init_2classes(
        self,
        instance_initiator: InstanceInitiator,
        test_service1_cls: type,
        test_service2_cls: type,
    ):
        instance_initiator.register_cls(test_service2_cls)
        assert instance_initiator._instance_manager.get_wrapper(test_service1_cls)
        assert instance_initiator._instance_manager.get_wrapper(test_service2_cls)

        assert isinstance(
            instance_initiator.get_or_init_instance(test_service2_cls),
            test_service2_cls,
        )
        assert isinstance(
            instance_initiator.get_or_init_instance(test_service1_cls),
            test_service1_cls,
        )

    def test_register_and_init_3classes(
        self,
        instance_initiator: InstanceInitiator,
        test_service1_cls: type,
        test_service2_cls: type,
        test_service3_cls: type,
    ):
        instance_initiator.register_cls(test_service3_cls)
        assert instance_initiator._instance_manager.get_wrapper(test_service1_cls)
        assert instance_initiator._instance_manager.get_wrapper(test_service2_cls)
        assert instance_initiator._instance_manager.get_wrapper(test_service3_cls)

        assert isinstance(
            instance_initiator.get_or_init_instance(test_service3_cls),
            test_service3_cls,
        )
        assert isinstance(
            instance_initiator.get_or_init_instance(test_service2_cls),
            test_service2_cls,
        )
        assert isinstance(
            instance_initiator.get_or_init_instance(test_service1_cls),
            test_service1_cls,
        )

    def test_register_module(
        self,
        instance_initiator: InstanceInitiator,
        test_module_cls: type,
        test_service1_cls: type,
        test_controller_cls: type,
    ):
        instance_initiator.register_cls(test_module_cls)
        assert instance_initiator._instance_manager.get_wrapper(test_service1_cls)
        assert instance_initiator._instance_manager.get_wrapper(test_controller_cls)
        assert instance_initiator._instance_manager.get_wrapper(test_module_cls)

        assert isinstance(
            instance_initiator.get_or_init_instance(test_module_cls),
            test_module_cls,
        )
        assert isinstance(
            instance_initiator.get_or_init_instance(test_controller_cls),
            test_controller_cls,
        )
        assert isinstance(
            instance_initiator.get_or_init_instance(test_service1_cls),
            test_service1_cls,
        )
