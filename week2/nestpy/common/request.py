from typing import Generic, TypeVar

T = TypeVar("T")


class RequestArgument(Generic[T]):
    def __init__(self, data: T):
        self.data = data


class Query(RequestArgument[T]):
    pass


class Param(RequestArgument[T]):
    pass


class Body(RequestArgument[T]):
    pass
