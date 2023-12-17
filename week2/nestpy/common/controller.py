from typing import TypedDict

from .constants import API_INFO_ATTR, API_INFO_LIST_ATTR, CONTROLLER_TOKEN_PREFIX
from .methods import APIInfo, get_api_info
from .token import AddingTokenDecorator
from .types import Class


class ControllerConfig(TypedDict):
    pass


def get_api_info_list(cls: Class) -> list[APIInfo]:
    return getattr(cls, API_INFO_LIST_ATTR)


class Controller(AddingTokenDecorator):
    token_prefix = CONTROLLER_TOKEN_PREFIX

    def __init__(self, path: str, config: ControllerConfig | None = None):
        self.path = path.strip("/")

    def __call__(self, cls):
        cls = super().__call__(cls)

        api_info_list: list[APIInfo] = []

        for method_name in dir(cls):
            method = getattr(cls, method_name)
            if hasattr(method, API_INFO_ATTR):
                api_info = get_api_info(method)
                api_info = api_info.copy(deep=True)
                api_info.path = f"{self.path}/{api_info.path}"
                api_info_list.append(api_info)

        setattr(cls, API_INFO_LIST_ATTR, api_info_list)
        return cls
