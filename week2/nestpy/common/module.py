from typing import TypedDict

from .constants import MODULE_CONTROLLER_ATTR, MODULE_PROVIDER_ATTR, MODULE_TOKEN_PREFIX
from .token import AddingTokenDecorator
from .types import Class


class ModuleConfig(TypedDict):
    controller: Class
    provider: Class


class Module(AddingTokenDecorator):
    token_prefix = MODULE_TOKEN_PREFIX

    def __init__(self, config: ModuleConfig):
        self.config = config

    def __call__(self, cls):
        cls = super().__call__(cls)
        setattr(cls, MODULE_CONTROLLER_ATTR, self.config["controller"])
        setattr(cls, MODULE_PROVIDER_ATTR, self.config["provider"])
        return cls
