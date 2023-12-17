from typing import TypedDict

from .constants import INJECTABLE_TOKEN_PREFIX
from .token import AddingTokenDecorator


class InjectableConfig(TypedDict):
    pass


class Injectable(AddingTokenDecorator):
    token_prefix = INJECTABLE_TOKEN_PREFIX

    def __init__(self, config: InjectableConfig | None = None):
        return None
