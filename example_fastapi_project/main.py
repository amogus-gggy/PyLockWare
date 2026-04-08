"""
FastAPI Example Project for PyLockWare
Tests async endpoints, decorators, type hints, and various FastAPI patterns
"""
from typing import List, Optional, Dict, Any
from functools import wraps
import time

from fastapi import FastAPI, HTTPException, Query, Path, Body
from pydantic import BaseModel, Field

app = FastAPI(title="PyLockWare Test API")


# --- Models ---

class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)
    description: Optional[str] = None
    tags: List[str] = []


class ItemResponse(BaseModel):
    id: int
    name: str
    price: float
    description: Optional[str]
    tags: List[str]


# --- Decorators ---

def log_execution(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"{func.__name__} executed in {elapsed:.4f}s")
        return result
    return wrapper


def require_api_key(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Simulated API key check
        return await func(*args, **kwargs)
    return wrapper


# --- In-memory DB ---

db_items: Dict[int, ItemResponse] = {}
next_id: int = 1


# --- Endpoints ---

@app.get("/")
async def root():
    return {"message": "Welcome to PyLockWare Test API"}


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "items_count": len(db_items),
    }


@log_execution
@app.get("/items", response_model=List[ItemResponse])
async def list_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    tag: Optional[str] = Query(None),
):
    items = list(db_items.values())
    
    if tag:
        items = [item for item in items if tag in item.tags]
    
    return items[skip : skip + limit]


@log_execution
@require_api_key
@app.post("/items", response_model=ItemResponse, status_code=201)
async def create_item(item: ItemCreate):
    global next_id
    
    new_item = ItemResponse(
        id=next_id,
        name=item.name,
        price=item.price,
        description=item.description,
        tags=item.tags,
    )
    db_items[next_id] = new_item
    next_id += 1
    
    return new_item


@app.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: int = Path(..., ge=1),
):
    if item_id not in db_items:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_items[item_id]


@log_execution
@app.put("/items/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: int = Path(..., ge=1),
    item: ItemCreate = Body(...),
):
    if item_id not in db_items:
        raise HTTPException(status_code=404, detail="Item not found")
    
    updated = ItemResponse(
        id=item_id,
        name=item.name,
        price=item.price,
        description=item.description,
        tags=item.tags,
    )
    db_items[item_id] = updated
    return updated


@app.delete("/items/{item_id}", status_code=204)
async def delete_item(item_id: int = Path(..., ge=1)):
    if item_id not in db_items:
        raise HTTPException(status_code=404, detail="Item not found")
    del db_items[item_id]
    return None


@log_execution
@app.get("/search")
async def search_items(q: str = Query(..., min_length=1)):
    q_lower = q.lower()
    results = [
        item for item in db_items.values()
        if q_lower in item.name.lower() or (item.description and q_lower in item.description.lower())
    ]
    return results


# --- Async background task ---

async def _simulate_async_work(data: str) -> Dict[str, Any]:
    """Simulate async I/O work"""
    await asyncio.sleep(0.01)
    return {"processed": data, "length": len(data)}


@app.post("/process")
async def process_data(data: str = Body(..., embed=True)):
    result = await _simulate_async_work(data)
    return result


# --- Startup/Shutdown ---

@app.on_event("startup")
async def startup_event():
    print("API started")


import asyncio
