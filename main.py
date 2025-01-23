from typing import Union
from fastapi import fastapi

app=fastapi()

@app.get("/")
def  basic():
    return "Hello World"

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}