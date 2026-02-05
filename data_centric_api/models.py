from datetime import date
from pydantic import BaseModel
    


class User(BaseModel):
    id: int
    username: str
    email_address: str
    password: str
    profile_img: str | None = None
    folder_ids: list[int] = []  # M:M relationship with Folder


class Folder(BaseModel):
    id: int
    name: str
    color: str | None = None
    position_index: int
    user_ids: list[int] = []  # M:M relationship with User


class List(BaseModel):
    id: int
    name: str
    position: int
    folder_id: int  # 1:M relationship (belongs to one Folder)


class Task(BaseModel):
    id: int
    name: str
    created_at: date | None = None
    due_date: date | None = None
    done: bool = False
    position: int
    favorite: bool = False
    list_id: int  # 1:M relationship (belongs to one List)
    location: str | None = None  # Optional location for transport lookup

class TransportResponse(BaseModel):
    name: str
    transport: list[str]
    