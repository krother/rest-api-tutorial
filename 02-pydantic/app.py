from typing import Union
from pydantic import BaseModel

from fastapi import FastAPI

app = FastAPI()


class ItemRequest(BaseModel):
    name: str
    quantity: int = 0


class ItemResponse(BaseModel):
    success: bool
    message: str


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.post("/order/")
def order_items(req: ItemRequest) -> ItemResponse:
    result = ItemResponse(
        message=f"successful delivery of {req.quantity} items of type {req.name}",
        success=True, 
    )
    return result
