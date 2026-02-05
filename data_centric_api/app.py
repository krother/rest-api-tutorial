from pathlib import Path

import json

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from models import User, Folder, List, Task, TransportResponse

app = FastAPI()

# Serve static files
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
def root():
    return FileResponse(static_dir / "index.html")

# In-memory storage
users: dict[int, User] = {}
folders: dict[int, Folder] = {}
lists: dict[int, List] = {}
tasks: dict[int, Task] = {}

# Auto-increment IDs
next_user_id = 1
next_folder_id = 1
next_list_id = 1
next_task_id = 1


# ============== User Endpoints ==============

@app.post("/users/")
def create_user(user: User) -> User:
    global next_user_id
    user.id = next_user_id
    users[user.id] = user
    next_user_id += 1
    return user


@app.get("/users/{user_id}/")
def get_user(user_id: int) -> User:
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    return users[user_id]


@app.get("/users/")
def get_users() -> list[User]:
    return list(users.values())


@app.patch("/users/{user_id}/")
def update_user(user_id: int, user_update: dict) -> User:
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    user = users[user_id]
    for key, value in user_update.items():
        if hasattr(user, key):
            setattr(user, key, value)
    return user


@app.put("/users/{user_id}/")
def replace_user(user_id: int, user: User) -> User:
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    user.id = user_id
    users[user_id] = user
    return user


@app.delete("/users/{user_id}/")
def delete_user(user_id: int) -> None:
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    del users[user_id]


# User -> Folders (M:M child relationship)
@app.post("/users/{user_id}/folders/")
def create_user_folder(user_id: int, folder: Folder) -> Folder:
    global next_folder_id
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    folder.id = next_folder_id
    folder.user_ids.append(user_id)
    folders[folder.id] = folder
    users[user_id].folder_ids.append(folder.id)
    next_folder_id += 1
    return folder


# ============== Folder Endpoints ==============

@app.post("/folders/")
def create_folder(folder: Folder) -> Folder:
    global next_folder_id
    folder.id = next_folder_id
    folders[folder.id] = folder
    next_folder_id += 1
    return folder


@app.get("/folders/{folder_id}/")
def get_folder(folder_id: int) -> Folder:
    if folder_id not in folders:
        raise HTTPException(status_code=404, detail="Folder not found")
    return folders[folder_id]


@app.get("/folders/")
def get_folders() -> list[Folder]:
    return list(folders.values())


@app.patch("/folders/{folder_id}/")
def update_folder(folder_id: int, folder_update: dict) -> Folder:
    if folder_id not in folders:
        raise HTTPException(status_code=404, detail="Folder not found")
    folder = folders[folder_id]
    for key, value in folder_update.items():
        if hasattr(folder, key):
            setattr(folder, key, value)
    return folder


@app.put("/folders/{folder_id}/")
def replace_folder(folder_id: int, folder: Folder) -> Folder:
    if folder_id not in folders:
        raise HTTPException(status_code=404, detail="Folder not found")
    folder.id = folder_id
    folders[folder_id] = folder
    return folder


@app.delete("/folders/{folder_id}/")
def delete_folder(folder_id: int) -> None:
    if folder_id not in folders:
        raise HTTPException(status_code=404, detail="Folder not found")
    del folders[folder_id]


# Folder -> Lists (1:M child relationship)
@app.post("/folders/{folder_id}/lists/")
def create_folder_list(folder_id: int, list_item: List) -> List:
    global next_list_id
    if folder_id not in folders:
        raise HTTPException(status_code=404, detail="Folder not found")
    list_item.id = next_list_id
    list_item.folder_id = folder_id
    lists[list_item.id] = list_item
    next_list_id += 1
    return list_item


# ============== List Endpoints ==============

@app.post("/lists/")
def create_list(list_item: List) -> List:
    global next_list_id
    list_item.id = next_list_id
    lists[list_item.id] = list_item
    next_list_id += 1
    return list_item


@app.get("/lists/{list_id}/")
def get_list(list_id: int) -> List:
    if list_id not in lists:
        raise HTTPException(status_code=404, detail="List not found")
    return lists[list_id]


@app.get("/lists/")
def get_lists() -> list[List]:
    return list(lists.values())


@app.patch("/lists/{list_id}/")
def update_list(list_id: int, list_update: dict) -> List:
    if list_id not in lists:
        raise HTTPException(status_code=404, detail="List not found")
    list_item = lists[list_id]
    for key, value in list_update.items():
        if hasattr(list_item, key):
            setattr(list_item, key, value)
    return list_item


@app.put("/lists/{list_id}/")
def replace_list(list_id: int, list_item: List) -> List:
    if list_id not in lists:
        raise HTTPException(status_code=404, detail="List not found")
    list_item.id = list_id
    lists[list_id] = list_item
    return list_item


@app.delete("/lists/{list_id}/")
def delete_list(list_id: int) -> None:
    if list_id not in lists:
        raise HTTPException(status_code=404, detail="List not found")
    del lists[list_id]


# List -> Tasks (1:M child relationship)
@app.post("/lists/{list_id}/tasks/")
def create_list_task(list_id: int, task: Task) -> Task:
    global next_task_id
    if list_id not in lists:
        raise HTTPException(status_code=404, detail="List not found")
    task.id = next_task_id
    task.list_id = list_id
    tasks[task.id] = task
    next_task_id += 1
    return task


# ============== Task Endpoints ==============

@app.post("/tasks/")
def create_task(task: Task) -> Task:
    global next_task_id
    task.id = next_task_id
    tasks[task.id] = task
    next_task_id += 1
    return task


@app.get("/tasks/{task_id}/")
def get_task(task_id: int) -> Task:
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]


@app.get("/tasks/")
def get_tasks() -> list[Task]:
    return list(tasks.values())


@app.patch("/tasks/{task_id}/")
def update_task(task_id: int, task_update: dict) -> Task:
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    task = tasks[task_id]
    for key, value in task_update.items():
        if hasattr(task, key):
            setattr(task, key, value)
    return task


@app.put("/tasks/{task_id}/")
def replace_task(task_id: int, task: Task) -> Task:
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    task.id = task_id
    tasks[task_id] = task
    return task


@app.delete("/tasks/{task_id}/")
def delete_task(task_id: int) -> None:
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    del tasks[task_id]


# ============== Dump to JSON ==============

@app.post("/dump/")
def dump_to_json():
    """Dump all data to a JSON file."""
    data = {
        "users": [u.model_dump() for u in users.values()],
        "folders": [f.model_dump() for f in folders.values()],
        "lists": [l.model_dump() for l in lists.values()],
        "tasks": [t.model_dump() for t in tasks.values()],
    }
    dump_path = Path(__file__).parent / "dump.json"
    dump_path.write_text(json.dumps(data, indent=2, default=str))
    return {"message": f"Data dumped to {dump_path.name}", "path": str(dump_path)}


# ============== Transport Endpoints (BVG API) ==============

@app.get("/transport/search")
def search_transport(query: str)-> TransportResponse:
    """Search for a stop/station in Berlin and return available transport types."""
    response = httpx.get(
        "https://v6.bvg.transport.rest/locations",
        params={"query": query, "results": 1}
    )
    results = response.json()
    if not results:
        raise HTTPException(status_code=404, detail="No stops found")
    stop = results[0]
    products = stop.get("products", {})
    transport = [mode for mode, available in products.items() if available]
    return {"name": stop.get("name", query), "transport": transport}


