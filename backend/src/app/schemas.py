"""Base schemas and ORM abstractions."""

from abc import ABC
from typing import Any, Self

from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, ValidationError
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError

from app.pyobjectid import PyObjectId
from app.query import FilterQuery, FilterQueryModel, RangeQuery, RangeQueryModel, SortQuery, SortQueryModel


class KyException(Exception):
    """Custom exception for database and application errors."""

    def __init__(self, message: str, code: int | None = None):
        super().__init__(message)
        self.message = message
        self.code = code

    def __str__(self) -> str:
        if self.code is not None:
            return f"KyException [{self.code}]: {self.message}: cause:[{repr(self.__cause__)}]"
        return f"KyException: {self.message}"

    def response(self) -> HTTPException:
        return HTTPException(
            status_code=self.code or 500,
            detail=self.message,
        )


class MongoModel(BaseModel):
    """Extended pydantic BaseModel with MongoDB helpers."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def to_mongo(self, **kwargs: Any) -> dict:
        """Serialize for MongoDB storage."""
        return self.model_dump(
            exclude_unset=True,
            by_alias=True,
        )


class KyDocument(MongoModel):
    """Base MongoDB document with CRUD operations."""

    class KyConfig(ABC):
        collection: Collection
        parent: str
        subarray: str

    @classmethod
    def get_collection(cls) -> Collection:
        return cls.KyConfig.collection

    @classmethod
    def get_by_id(cls, objectid: PyObjectId) -> Self:
        collection = cls.get_collection()
        try:
            found = collection.find_one({"_id": objectid})
        except Exception as e:
            raise KyException(message="database error", code=500) from e

        if found:
            return cls(**found)
        raise KyException("there's no document with that ID", 404)

    @classmethod
    def create(cls, data: MongoModel) -> Self:
        collection = cls.get_collection()
        try:
            created = collection.insert_one(data.to_mongo())
        except DuplicateKeyError:
            raise
        except Exception as e:
            raise KyException(message="database error", code=500) from e

        return cls.get_by_id(objectid=created.inserted_id)

    @classmethod
    def update(cls, objectid: PyObjectId, data: MongoModel) -> Self:
        collection = cls.get_collection()
        _ = cls.get_by_id(objectid=objectid)

        update_successful = collection.update_one(
            {"_id": objectid},
            {"$set": data.to_mongo()},
        )
        if update_successful.modified_count == 0:
            raise KyException("failed to update the document", 500)

        return cls.get_by_id(objectid=objectid)

    @classmethod
    def delete(cls, objectid: PyObjectId) -> Self:
        collection = cls.get_collection()
        found = cls.get_by_id(objectid=objectid)

        deletion_return = collection.delete_one({"_id": objectid})
        if deletion_return.deleted_count != 1:
            raise KyException("failed to delete the document", 500)

        return found

    @classmethod
    def delete_many(cls, filter: FilterQuery) -> list[Self]:
        collection = cls.get_collection()
        documents_to_delete, _ = cls.get_all(filter=filter)
        ids_to_delete = filter.get_ids()
        try:
            deletion_return = collection.delete_many({"_id": {"$in": ids_to_delete}})
            if deletion_return.acknowledged:
                return documents_to_delete
            raise KyException(message="database error, deletion not acknowledged", code=500)
        except Exception as e:
            raise KyException(message="database error", code=500) from e

    @classmethod
    def get_all(
        cls,
        range: RangeQuery | None = None,
        filter: FilterQuery | None = None,
        sort: SortQuery | None = None,
    ) -> tuple[list[Self], int]:
        collection = cls.get_collection()

        if range is None:
            range = RangeQueryModel()
        if filter is None:
            filter = FilterQueryModel()
        if sort is None:
            sort = SortQueryModel()

        pipeline: list[dict] = []

        if filterstage := filter.get_pipeline():
            pipeline.extend(filterstage)

        if sortstage := sort.get_pipeline():
            pipeline.append(sortstage)

        facet = {
            "$facet": {
                "data": [{"$skip": range.skipper()}, {"$limit": range.perPage}],
                "metadata": [{"$count": "totalCount"}],
            },
        }
        pipeline.append(facet)

        try:
            results = list(collection.aggregate(pipeline))
        except Exception as e:
            raise KyException("database error", 500) from e

        if not (data := results[0]["data"]):
            return [], 0

        total = results[0]["metadata"][0]["totalCount"]

        try:
            arr = [cls(**item) for item in data]
        except ValidationError as e:
            raise KyException("validation error: database must contain an invalid document", 500) from e

        return arr, total
