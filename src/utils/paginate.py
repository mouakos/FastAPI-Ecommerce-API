from typing import Generic, TypeVar, List

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    page: int
    size: int
    pages: int
    items: List[T]
