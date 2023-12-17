from typing import Any, TypedDict

from .token import MODULE_TOKEN_PREFIX, AddingTokenDecorator


class ModuleConfig(TypedDict):
    controller: type[Any]
    provider: type[Any]


class Module(AddingTokenDecorator):
    token_prefix = MODULE_TOKEN_PREFIX

    def __init__(self, config: ModuleConfig):
        self.config = config
