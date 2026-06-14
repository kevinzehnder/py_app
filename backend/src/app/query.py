from typing import Annotated

from fastapi import Depends, Query
from pydantic import BaseModel, field_validator

from app.pyobjectid import PyObjectId


class RangeQueryModel(BaseModel):
    """Pagination query params for MongoDB."""

    page: int = 0
    perPage: int = 10

    def skipper(self) -> int:
        if self.page > 0:
            return (self.page - 1) * self.perPage
        return 0


class SortQueryModel(BaseModel):
    """Sort params for MongoDB."""

    field: str = "_id"
    order: int = 1

    @field_validator("order")
    @classmethod
    def check_order(cls, v: int) -> int:
        if v not in (1, -1):
            raise ValueError("sort value must be 1 or -1")
        return v

    def get_pipeline(self) -> dict:
        sort_field = "_id" if self.field == "id" else self.field
        return {"$sort": {sort_field: self.order}}


class FilterQueryModel(BaseModel):
    """Base filter model for MongoDB _id filtering."""

    id: list[PyObjectId] | PyObjectId | None = None

    def get_pipeline(self) -> list[dict]:
        if not self.id:
            return []

        if isinstance(self.id, list):
            obj_ids = [PyObjectId(id) for id in self.id]
            return [{"$match": {"_id": {"$in": obj_ids}}}]

        return [{"$match": {"_id": PyObjectId(self.id)}}]

    def get_ids(self) -> list[PyObjectId]:
        if not self.id:
            return []

        if isinstance(self.id, list):
            return [PyObjectId(id) for id in self.id]

        return [PyObjectId(self.id)]


async def parse_range_query(
    range: str = Query(default='{"page": 0, "perPage": 10}'),
) -> RangeQueryModel:
    return RangeQueryModel.model_validate_json(range)


async def parse_sort_query(
    sort: str = Query(default='{"field": "_id", "order": 1}'),
) -> SortQueryModel:
    return SortQueryModel.model_validate_json(sort)


async def parse_filter_query(
    filter: str = Query(default="{}"),
) -> FilterQueryModel:
    return FilterQueryModel.model_validate_json(filter)


RangeQuery = Annotated[RangeQueryModel, Depends(parse_range_query)]
SortQuery = Annotated[SortQueryModel, Depends(parse_sort_query)]
FilterQuery = Annotated[FilterQueryModel, Depends(parse_filter_query)]
