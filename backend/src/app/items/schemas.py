from pydantic import AliasChoices, Field

from app.database import get_collection
from app.pyobjectid import PyObjectId
from app.schemas import KyDocument, MongoModel


class ItemBase(MongoModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field("", max_length=1000)
    active: bool = True


class Item(KyDocument):
    id: PyObjectId = Field(..., validation_alias=AliasChoices("_id", "id"))
    name: str
    description: str = ""
    active: bool = True

    class KyConfig(KyDocument.KyConfig):
        collection = get_collection("items")
