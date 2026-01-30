
import asyncio
from fastapi import FastAPI
import time

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/wait")
def read_item(secs: int):
    time.sleep(secs)
    return {"status": "ready", "seconds": secs}


@app.get("/wait_async")
async def read_item_async(secs: int):
    await asyncio.sleep(secs)
    return {"status": "ready", "seconds": secs}
