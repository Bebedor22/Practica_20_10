from math import ceil
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    limit: int
    total_pages: int = Field(alias="totalPages")
    has_next: bool = Field(alias="hasNext")
    has_prev: bool = Field(alias="hasPrev")

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def create(
        cls, *, items: list[T], total: int, page: int, limit: int
    ) -> "Page[T]":
        total_pages = ceil(total / limit) if limit else 0
        return cls(
            items=items,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
            has_next=page * limit < total,
            has_prev=page > 1,
        )
