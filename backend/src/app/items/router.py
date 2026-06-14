import fastapi
from fastapi import Depends, HTTPException
from pymongo.errors import DuplicateKeyError

from app.auth.dependencies import get_current_user
from app.items.schemas import Item, ItemBase
from app.pyobjectid import PyObjectId
from app.query import FilterQuery, RangeQuery, SortQuery

router = fastapi.APIRouter(
    prefix="/api/items",
    tags=["items"],
    responses={404: {"description": "item not found"}},
    dependencies=[Depends(get_current_user)],
)


@router.get("/", response_description="list of items")
def get_items(
    response: fastapi.Response,
    range: RangeQuery,
    filter: FilterQuery,
    sort: SortQuery,
) -> list[Item]:
    items, total = Item.get_all(range=range, filter=filter, sort=sort)
    response.headers["X-Total-Count"] = str(total)
    return items


@router.get("/{id}", response_description="item by id")
def get_item_by_id(id: PyObjectId) -> Item:
    return Item.get_by_id(id)


@router.post("/", status_code=201, response_description="created item")
def create_item(new_item: ItemBase) -> Item:
    try:
        return Item.create(new_item)
    except DuplicateKeyError as e:
        raise HTTPException(400, "item already exists") from e


@router.put("/{id}", response_description="updated item")
def update_item(id: PyObjectId, updated_item: ItemBase) -> Item:
    return Item.update(objectid=id, data=updated_item)


@router.delete("/{id}", response_description="deleted item")
def delete_item(id: PyObjectId) -> Item:
    return Item.delete(id)
