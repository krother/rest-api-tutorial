

from fastapi import FastAPI, HTTPException

import json
import os


app = FastAPI()


@app.get("/hello")
def hello():
    return {"Hello": "World"}


@app.get("/songs/{query}")
def songs(query: str):

    # load song database
    path = os.path.split(__file__)[0]
    songdb = json.load(open(os.path.join(path, 'song_finder', 'songs.json')))

    # search song by id or title
    for song in songdb:
        if (
            str(song["song_id"]) == query or 
            query.lower() in song["title"].lower()
        ):
            return song
    
    raise HTTPException(status_code=404, detail=f"song {query} not found")
