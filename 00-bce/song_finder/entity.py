
from pydantic import BaseModel


class SongRequest(BaseModel):
    name: str

class SongResponse(BaseModel):

    song_id: int
    title: str
    artist: str
    year: int | None
