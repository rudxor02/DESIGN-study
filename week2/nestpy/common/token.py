import logging
from abc import ABC
from inspect import _empty, signature
from typing import Any

from pydantic import BaseModel

from .constants import (
    CONTROLLER_TOKEN_PREFIX,
    MODULE_CONTROLLER_ATTR,
    MODULE_PROVIDER_ATTR,
    TOKEN_ATTR,
)
from .types import Class, Instance, Token

_logger = logging.getLogger(__name__)


def pass_init(self, /, *args, **kwargs):
    pass


pass_init_sig = signature(pass_init)


def default_init(self):
    pass


class AddingTokenDecorator(ABC):
    """
    Abstract class of Adding token decorator
    """

    token_prefix: str

    def __init_subclass__(cls: Class) -> None:
        if getattr(cls, "token_prefix", None) is None:
            raise NotImplementedError(f"token prefix must be set for {cls.__name__}")

    def __call__(self, cls):
        """
        should not be typed because of typing erases type annotation of decorated class
        but please ignore for [reportUntypedClassDecorator](https://github.com/microsoft/pyright/blob/main/docs/configuration.md#reportUntypedClassDecorator) warning...
        """
        if signature(cls.__init__) == pass_init_sig:
            cls.__init__ = default_init
            _logger.warning(f"write explicit __init__ for {cls.__name__}")
        setattr(cls, TOKEN_ATTR, self.token_prefix + cls.__name__)
        return cls


class InstanceWrapper(BaseModel):
    cls: Class
    instance: Instance | None = None
    pending: bool = False

    @property
    def instance_registered(self):
        return self.instance is not None

    def register_instance(self, instance: Instance):
        if self.instance_registered:
            raise ValueError(f"{self} should be registered only once")
        if self.pending is False:
            raise ValueError(f"{self} has not been marked first")
        self.instance = instance
        self.pending = False

    def mark_pending(self):
        if self.pending is True:
            raise ValueError("Already marked... maybe circular reference occurred")
        self.pending = True


class InstanceManager:
    """
    DI context is global, not module separated.

    Considering one instance, these steps should be executed sequentially.

    1. register class
    2. mark pending to class
    3. register instance
    """

    def __init__(self):
        self._instances: dict[Token, InstanceWrapper] = {}

    def _get_token(self, cls: Class) -> Token:
        if (token := getattr(cls, TOKEN_ATTR, None)) is None:
            raise ValueError(f"token is not set for {cls.__name__}")
        return token

    def get_wrapper(self, cls: Class) -> InstanceWrapper:
        token = self._get_token(cls)
        if token not in self._instances.keys():
            raise ValueError(f"class {cls.__name__} should be registered first")
        return self._instances[token]

    def register_cls(self, cls: Class) -> None:
        token = self._get_token(cls)
        self._instances[token] = InstanceWrapper(cls=cls)

    def mark_pending(self, cls: Class) -> None:
        token = self._get_token(cls)
        if token not in self._instances.keys():
            raise ValueError(f"class {cls.__name__} should be registered first")
        wrapper = self._instances[token]
        wrapper.mark_pending()

    def register_instance(self, instance: Instance) -> None:
        token = self._get_token(instance.__class__)
        if token not in self._instances.keys():
            raise ValueError(
                f"class {instance.__class__.__name__} should be registered first"
            )
        wrapper = self._instances[token]
        wrapper.register_instance(instance)

    def get_controllers(self) -> list[Instance]:
        """
        Returns all controllers for routing
        """
        controller_instances: list[Instance] = []

        for token, wrapper in self._instances.items():
            if not token.startswith(CONTROLLER_TOKEN_PREFIX):
                continue
            if not wrapper.instance_registered:
                raise ValueError(f"{wrapper} instance has not been registered")
            controller_instances.append(wrapper.instance)

        return controller_instances


class InstanceInitiator:
    def __init__(self):
        self._instance_manager = InstanceManager()

    def register_cls(self, cls: Class):
        sig = signature(cls.__init__)

        for var_name, param in sig.parameters.items():
            if var_name == "self":
                continue

            if var_name in ["args", "kwargs"]:
                raise ValueError("args or kwargs signature not allowed")

            if (param_cls := param.annotation) == _empty:
                raise ValueError(
                    f"set annotation to {var_name} in  {cls.__name__} init function"
                )
            self.register_cls(param_cls)
        self._instance_manager.register_cls(cls)
        _logger.info(f"{cls.__name__} registered")

        # TODO checking module dependency: is this best?
        if hasattr(cls, MODULE_CONTROLLER_ATTR):
            self.register_cls(getattr(cls, MODULE_CONTROLLER_ATTR))

        if hasattr(cls, MODULE_PROVIDER_ATTR):
            self.register_cls(getattr(cls, MODULE_PROVIDER_ATTR))

    def get_or_init_instance(self, cls: Class) -> Instance:
        wrapper = self._instance_manager.get_wrapper(cls)
        if wrapper.instance_registered:
            return wrapper.instance
        instance = self._init_instance(cls)
        _logger.info(f"{cls.__name__} initialized")
        self._instance_manager.register_instance(instance)

        # TODO checking module dependency: is this best?
        if hasattr(cls, MODULE_CONTROLLER_ATTR):
            self.get_or_init_instance(getattr(cls, MODULE_CONTROLLER_ATTR))

        if hasattr(cls, MODULE_PROVIDER_ATTR):
            self.get_or_init_instance(getattr(cls, MODULE_PROVIDER_ATTR))

        return instance

    def _init_instance(self, cls: Class) -> Instance:
        sig = signature(cls.__init__)

        params: dict[str, Any] = {}
        self._instance_manager.mark_pending(cls)

        # _logger.info(cls)

        for var_name, param in sig.parameters.items():
            if var_name == "self":
                continue

            if var_name in ["args", "kwargs"]:
                raise ValueError("args or kwargs signature not allowed")

            if (param_cls := param.annotation) == _empty:
                raise ValueError(
                    f"set annotation to {var_name} in  {cls.__name__} init function"
                )

            param_instance = self.get_or_init_instance(param_cls)
            params[var_name] = param_instance

        return cls(**params)

    def get_controllers(self) -> list[Instance]:
        return self._instance_manager.get_controllers()
