from abc import ABC
from inspect import _empty, signature
from typing import Any, Literal, Union

from pydantic import BaseModel

from .constants import API_INFO_ATTR
from .types import Class, MethodFunction


class ParameterInfo(BaseModel):
    name: str
    type: Class
    default: Any | _empty
    required: bool

    class Config:
        arbitrary_types_allowed = True


class APIInfo(BaseModel):
    path: str
    request_method: Literal["GET", "POST"]
    func_name: str
    path_param_info_dict: dict[str, ParameterInfo] = {}
    query_param_info_dict: dict[str, ParameterInfo] = {}
    body_param_info_dict: dict[str, ParameterInfo] = {}


def get_api_info(func: MethodFunction) -> APIInfo:
    return getattr(func, API_INFO_ATTR)


class Method(ABC):
    def __init__(self, path: str = ""):
        self.path = path.strip("/")

    def __call__(self, func):
        """
        should not be typed because of typing erases type annotation of decorated class
        but please ignore for [reportUntypedClassDecorator](https://github.com/microsoft/pyright/blob/main/docs/configuration.md#reportUntypedClassDecorator) warning...
        """
        sig = signature(func)
        func_params = sig.parameters

        if (request_method_name := self.__class__.__name__.upper()) not in [
            "GET",
            "POST",
        ]:
            raise NotImplementedError("only get and post are supported")

        api_info = APIInfo(
            path=self.path, request_method=request_method_name, func_name=func.__name__
        )

        for var_name, param in func_params.items():
            if var_name == "self":
                continue

            annotation = param.annotation
            if annotation == _empty:
                raise ValueError(
                    f"missing annotation for {var_name} in {func.__name__}"
                )
            if annotation.__origin__ == Union:
                # for optional
                annotation = annotation.__args__[0]

            param_info = ParameterInfo(
                name=var_name,
                type=annotation.__args__[0],
                default=param.default,
                required=param.default == _empty,
            )

            # TODO how to check generic type?
            if "Body" in str(annotation):
                api_info.body_param_info_dict[var_name] = param_info
            elif "Param" in str(annotation):
                api_info.path_param_info_dict[var_name] = param_info
            elif "Query" in str(annotation):
                api_info.query_param_info_dict[var_name] = param_info
            else:
                raise ValueError(f"invalid annotation {param.annotation}")

        setattr(func, API_INFO_ATTR, api_info)
        return func


class Get(Method):
    pass


class Post(Method):
    pass
