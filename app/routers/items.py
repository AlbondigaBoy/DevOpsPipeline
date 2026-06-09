from fastapi import APIRouter, HTTPException, status

from app.models import Item, ItemCreate, ItemUpdate

router = APIRouter(prefix="/items", tags=["items"])
# In-memory database simulation

items_db: dict[int, Item] = {}
_id_counter = 0

def _get_next_id() -> int:
    global _id_counter
    _id_counter += 1
    return _id_counter

@router.get("/", response_model=list[Item])
async def list_items():
    """Get all items."""
    return list(items_db.values())

@router.get("/{item_id}", response_model=Item)
async def get_item(item_id: int):
    """Get a specific item by ID."""
    if item_id not in items_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found",
        )
    return items_db[item_id]

@router.post("/", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate):
    """Create a new item."""
    new_id = _get_next_id()
    db_item = Item(id=new_id, **item.model_dump())
    items_db[new_id] = db_item
    return db_item

@router.put("/{item_id}", response_model=Item)
async def update_item(item_id: int, item: ItemUpdate):
    """Update an existing item."""
    if item_id not in items_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found",
        )
    stored_item = items_db[item_id]
    update_data = item.model_dump(exclude_unset=True)
    updated_item = stored_item.model_copy(update=update_data)
    items_db[item_id] = updated_item
    return updated_item

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int):
    """Delete an item."""
    if item_id not in items_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found",
        )
    del items_db[item_id]