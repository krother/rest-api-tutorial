
Structuring a Larger API
========================

.. topic:: Goal

   In this chapter, you structure your API using the BCE (Boundary-Control-Entity) pattern to create a maintainable, testable codebase.

As your API grows, keeping all code in a single file becomes unmanageable.
The **BCE Pattern** (also known as ECB or Hexagonal Architecture) separates your code into three layers:

.. mermaid::

   flowchart LR
       subgraph Boundary
           A[API Routes]
           B[CLI]
       end
       subgraph Control
           C[Services]
       end
       subgraph Entity
           D[Repository]
           E[Models]
       end

       A --> C
       B --> C
       C --> D
       C --> E

- **Boundary**: Entry points to your application (API routes, CLI, web interface)
- **Control**: Business logic and orchestration (services)
- **Entity**: Data models and persistence (repositories, database models)

The key principle is that **dependencies point inward**: Boundaries depend on Control, Control depends on Entity.
Entity knows nothing about the outer layers.


Exercise 1: Create a Clean Project Structure
--------------------------------------------

Set up a proper Python package structure for your todo-list API:

.. code-block:: text

   todo_api/
   ├── pyproject.toml
   ├── README.md
   ├── src/
   │   └── todo_api/
   │       ├── __init__.py
   │       ├── main.py
   │       ├── models.py
   │       ├── repository.py
   │       └── services.py
   └── tests/
       ├── __init__.py
       └── test_services.py

Initialize the project with ``uv``:

.. code-block:: bash

   mkdir todo_api && cd todo_api
   uv init

Update ``pyproject.toml`` to include FastAPI:

.. code-block:: toml

   [project]
   name = "todo-api"
   version = "0.1.0"
   dependencies = [
       "fastapi",
       "duckdb",
   ]

   [project.optional-dependencies]
   dev = ["pytest", "httpx"]

Create the folder structure:

.. code-block:: bash

   mkdir -p src/todo_api tests
   touch src/todo_api/__init__.py
   touch tests/__init__.py


Exercise 2: Define the Entity Layer
-----------------------------------

The Entity layer contains your data models and repository.
Create ``src/todo_api/models.py``:

.. code-block:: python

   from datetime import datetime
   from pydantic import BaseModel


   class Task(BaseModel):
       id: int
       title: str
       completed: bool = False
       created_at: datetime


   class TaskCreate(BaseModel):
       title: str


   class TaskUpdate(BaseModel):
       title: str | None = None
       completed: bool | None = None

Move the repository from chapter 06 to ``src/todo_api/repository.py``:

.. code-block:: python

   import duckdb
   from .models import Task


   class TaskRepository:

       def __init__(self, db_path: str = ":memory:"):
           self.con = duckdb.connect(db_path)
           self._create_table()

       def _create_table(self):
           self.con.execute("""
               CREATE TABLE IF NOT EXISTS tasks (
                   id INTEGER PRIMARY KEY,
                   title VARCHAR,
                   completed BOOLEAN,
                   created_at TIMESTAMP
               )
           """)

       def add(self, task: Task) -> Task:
           self.con.execute(
               "INSERT INTO tasks VALUES (?, ?, ?, ?)",
               [task.id, task.title, task.completed, task.created_at]
           )
           return task

       def get(self, task_id: int) -> Task | None:
           result = self.con.execute(
               "SELECT * FROM tasks WHERE id = ?", [task_id]
           ).fetchone()
           if result is None:
               return None
           return Task(
               id=result[0], title=result[1],
               completed=result[2], created_at=result[3]
           )

       def get_all(self) -> list[Task]:
           result = self.con.execute("SELECT * FROM tasks").fetchall()
           return [
               Task(id=r[0], title=r[1], completed=r[2], created_at=r[3])
               for r in result
           ]

       def delete(self, task_id: int) -> bool:
           result = self.con.execute(
               "DELETE FROM tasks WHERE id = ? RETURNING id", [task_id]
           ).fetchone()
           return result is not None

       def next_id(self) -> int:
           result = self.con.execute(
               "SELECT COALESCE(MAX(id), 0) + 1 FROM tasks"
           ).fetchone()
           return result[0]


Exercise 3: Create the Control Layer
------------------------------------

The Control layer contains your business logic.
Create ``src/todo_api/services.py``:

.. code-block:: python

   from datetime import datetime
   from .models import Task, TaskCreate, TaskUpdate
   from .repository import TaskRepository


   class TaskService:

       def __init__(self, repository: TaskRepository):
           self.repo = repository

       def create_task(self, data: TaskCreate) -> Task:
           task = Task(
               id=self.repo.next_id(),
               title=data.title,
               completed=False,
               created_at=datetime.now()
           )
           return self.repo.add(task)

       def get_task(self, task_id: int) -> Task | None:
           return self.repo.get(task_id)

       def list_tasks(self, completed: bool | None = None) -> list[Task]:
           tasks = self.repo.get_all()
           if completed is not None:
               tasks = [t for t in tasks if t.completed == completed]
           return tasks

       def delete_task(self, task_id: int) -> bool:
           return self.repo.delete(task_id)

The service layer:

- Contains business logic (filtering, validation)
- Does not know about HTTP or FastAPI
- Can be tested independently


Exercise 4: Create the Boundary Layer
-------------------------------------

The Boundary layer contains your API routes.
Create ``src/todo_api/main.py``:

.. code-block:: python

   from fastapi import FastAPI, HTTPException
   from .models import Task, TaskCreate
   from .repository import TaskRepository
   from .services import TaskService

   app = FastAPI(title="Todo API")

   # Initialize dependencies
   repo = TaskRepository("tasks.db")
   service = TaskService(repo)


   @app.post("/tasks/", status_code=201)
   def create_task(data: TaskCreate) -> Task:
       return service.create_task(data)


   @app.get("/tasks/{task_id}")
   def get_task(task_id: int) -> Task:
       task = service.get_task(task_id)
       if task is None:
           raise HTTPException(status_code=404, detail="Task not found")
       return task


   @app.get("/tasks/")
   def list_tasks(completed: bool | None = None) -> list[Task]:
       return service.list_tasks(completed)


   @app.delete("/tasks/{task_id}", status_code=204)
   def delete_task(task_id: int):
       if not service.delete_task(task_id):
           raise HTTPException(status_code=404, detail="Task not found")

The boundary layer:

- Is thin and focused on HTTP concerns
- Converts HTTP errors to proper status codes
- Delegates all logic to the service layer


Exercise 5: Data Transfer Objects
---------------------------------

Sometimes your database model differs from your API model.
For example, the database might store additional audit fields:

.. code-block:: python

   # Database model (internal)
   class TaskDB(BaseModel):
       id: int
       title: str
       completed: bool
       created_at: datetime
       updated_at: datetime
       created_by: str

   # API model (external)
   class TaskResponse(BaseModel):
       id: int
       title: str
       completed: bool

Create mapping functions to convert between them:

.. code-block:: python

   def to_response(db_task: TaskDB) -> TaskResponse:
       return TaskResponse(
           id=db_task.id,
           title=db_task.title,
           completed=db_task.completed
       )

   def to_response_list(db_tasks: list[TaskDB]) -> list[TaskResponse]:
       return [to_response(t) for t in db_tasks]

This separation allows you to:

- Hide internal fields from the API
- Change the database schema without breaking the API
- Add computed fields to the response


Exercise 6: Organize Tests
--------------------------

Test files should mirror your source structure:

.. code-block:: text

   src/todo_api/
   ├── models.py
   ├── repository.py
   └── services.py

   tests/
   ├── test_models.py
   ├── test_repository.py
   └── test_services.py

Create ``tests/test_services.py``:

.. code-block:: python

   import pytest
   from todo_api.models import TaskCreate
   from todo_api.repository import TaskRepository
   from todo_api.services import TaskService


   @pytest.fixture
   def service():
       """Create a service with an in-memory database."""
       repo = TaskRepository(":memory:")
       return TaskService(repo)


   def test_create_task(service):
       data = TaskCreate(title="Buy groceries")
       task = service.create_task(data)

       assert task.id == 1
       assert task.title == "Buy groceries"
       assert task.completed is False


   def test_list_tasks_filter_completed(service):
       service.create_task(TaskCreate(title="Task 1"))
       task2 = service.create_task(TaskCreate(title="Task 2"))

       # Mark task2 as completed (through repo for simplicity)
       service.repo.con.execute(
           "UPDATE tasks SET completed = true WHERE id = ?", [task2.id]
       )

       completed = service.list_tasks(completed=True)
       assert len(completed) == 1
       assert completed[0].title == "Task 2"

Run the tests:

.. code-block:: bash

   uv run pytest tests/ -v


Exercise 7: API Integration Tests
---------------------------------

Test the full API using FastAPI's test client.
Create ``tests/test_api.py``:

.. code-block:: python

   import pytest
   from fastapi.testclient import TestClient
   from todo_api.main import app, repo, service
   from todo_api.repository import TaskRepository
   from todo_api.services import TaskService


   @pytest.fixture
   def client():
       """Create a test client with a fresh database."""
       # Override with in-memory database for tests
       test_repo = TaskRepository(":memory:")
       test_service = TaskService(test_repo)

       # This is simplified; in production use FastAPI dependency overrides
       import todo_api.main as main_module
       main_module.repo = test_repo
       main_module.service = test_service

       return TestClient(app)


   def test_create_and_get_task(client):
       # Create a task
       response = client.post("/tasks/", json={"title": "Test task"})
       assert response.status_code == 201
       task = response.json()
       assert task["title"] == "Test task"

       # Retrieve it
       response = client.get(f"/tasks/{task['id']}")
       assert response.status_code == 200
       assert response.json()["title"] == "Test task"


   def test_get_nonexistent_task(client):
       response = client.get("/tasks/999")
       assert response.status_code == 404


Reflection Questions
++++++++++++++++++++

- What are the advantages of the BCE pattern?
- How does separating layers make testing easier?
- What belongs in the service layer vs. the repository layer?
- How would you add a new feature (e.g., task priorities) across all layers?

.. seealso::

   - `Clean Architecture by Robert C. Martin <https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html>`__
   - `Hexagonal Architecture <https://alistair.cockburn.us/hexagonal-architecture/>`__
   - `FastAPI Dependency Injection <https://fastapi.tiangolo.com/tutorial/dependencies/>`__
