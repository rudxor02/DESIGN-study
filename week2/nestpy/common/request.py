from typing import Generic, TypeVar

T = TypeVar("T")


class Query(Generic[T]):
    pass


class Param(Generic[T]):
    pass


class Body(Generic[T]):
    pass
