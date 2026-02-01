
The Repository Pattern
======================

.. topic:: Goal

   In this chapter, you connect a database to your API and structure the code using the Repository Pattern.

When building a data-centric API, you need to persist data beyond the lifetime of a single request.
The **Repository Pattern** separates data access logic from business logic, making your code more maintainable and testable.

.. mermaid::

   flowchart LR
       A[API Endpoint] --> B[Repository]
       B --> C[Database]
       B --> D[JSON File]
       B --> E[In-Memory]

The repository acts as a middleman between your API and the data storage.
This allows you to swap out the storage backend without changing your API code.

Pydantic Serialization
++++++++++++++++++++++

Pydantic models can be easily converted to and from JSON, which is useful for file-based storage and debugging.

.. code-block:: python

   from pydantic import BaseModel

   class Task(BaseModel):
       id: int
       title: str
       completed: bool = False

   task = Task(id=1, title="Buy groceries")

   # Convert to JSON string
   json_str = task.model_dump_json()

   # Convert to dictionary
   data = task.model_dump()

   # Parse from dictionary
   task2 = Task.model_validate(data)

   # Parse from JSON string
   task3 = Task.model_validate_json(json_str)


Exercise 1: Dump Tasks to JSON
------------------------------

Create a function that saves a list of tasks to a JSON file.
Use the ``Task`` model from chapter 05:

.. code-block:: python

   import json
   from pydantic import BaseModel
   from datetime import datetime

   class Task(BaseModel):
       id: int
       title: str
       completed: bool = False
       created_at: datetime


   def save_tasks(tasks: list[Task], filename: str):
       data = [task.model_dump(mode="json") for task in tasks]
       with open(filename, "w") as f:
           json.dump(data, f, indent=2)

Test the function:

.. code-block:: python

   tasks = [
       Task(id=1, title="Buy groceries", created_at=datetime.now()),
       Task(id=2, title="Walk the dog", created_at=datetime.now()),
   ]
   save_tasks(tasks, "tasks.json")

.. hint::

   The ``mode="json"`` argument ensures that ``datetime`` objects are serialized as ISO strings.


Exercise 2: Load Tasks from JSON
--------------------------------

Create a function that loads tasks from a JSON file:

.. code-block:: python

   def load_tasks(filename: str) -> list[Task]:
       with open(filename, "r") as f:
           data = json.load(f)
       return [Task.model_validate(item) for item in data]

Test the round-trip:

.. code-block:: python

   loaded = load_tasks("tasks.json")
   print(loaded)


Exercise 3: Store Tasks in DuckDB
---------------------------------

DuckDB is an embedded analytical database that requires no server setup.
Install it:

.. code-block:: bash

   uv add duckdb

Create a connection and store tasks:

.. code-block:: python

   import duckdb

   # Create an in-memory database
   con = duckdb.connect()

   # Create a table
   con.execute("""
       CREATE TABLE tasks (
           id INTEGER PRIMARY KEY,
           title VARCHAR,
           completed BOOLEAN,
           created_at TIMESTAMP
       )
   """)

   # Insert a task
   task = Task(id=1, title="Buy groceries", completed=False, created_at=datetime.now())
   con.execute(
       "INSERT INTO tasks VALUES (?, ?, ?, ?)",
       [task.id, task.title, task.completed, task.created_at]
   )

.. note::

   For persistent storage, use ``duckdb.connect("tasks.db")`` instead.


Exercise 4: Read Tasks from DuckDB
----------------------------------

Query tasks from the database and convert them back to Pydantic models:

.. code-block:: python

   def get_all_tasks(con: duckdb.DuckDBPyConnection) -> list[Task]:
       result = con.execute("SELECT * FROM tasks").fetchall()
       return [
           Task(id=row[0], title=row[1], completed=row[2], created_at=row[3])
           for row in result
       ]


   def get_task_by_id(con: duckdb.DuckDBPyConnection, task_id: int) -> Task | None:
       result = con.execute(
           "SELECT * FROM tasks WHERE id = ?", [task_id]
       ).fetchone()
       if result is None:
           return None
       return Task(id=result[0], title=result[1], completed=result[2], created_at=result[3])

Test the queries:

.. code-block:: python

   tasks = get_all_tasks(con)
   print(tasks)

   task = get_task_by_id(con, 1)
   print(task)


Exercise 5: Implement a Repository Class
----------------------------------------

Move the database code into a dedicated repository class:

.. code-block:: python

   # repository.py
   import duckdb
   from models import Task


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

       def update(self, task: Task) -> Task:
           self.con.execute(
               "UPDATE tasks SET title=?, completed=? WHERE id=?",
               [task.title, task.completed, task.id]
           )
           return task

       def delete(self, task_id: int) -> bool:
           result = self.con.execute(
               "DELETE FROM tasks WHERE id = ? RETURNING id", [task_id]
           ).fetchone()
           return result is not None


Exercise 6: Use the Repository in FastAPI
-----------------------------------------

Connect the repository to your API endpoints:

.. code-block:: python

   # app.py
   from fastapi import FastAPI, HTTPException
   from repository import TaskRepository
   from models import Task, TaskCreate

   app = FastAPI()
   repo = TaskRepository("tasks.db")


   @app.post("/tasks/", status_code=201)
   def create_task(data: TaskCreate) -> Task:
       task_id = len(repo.get_all()) + 1
       task = Task(
           id=task_id,
           title=data.title,
           created_at=datetime.now()
       )
       return repo.add(task)


   @app.get("/tasks/{task_id}")
   def get_task(task_id: int) -> Task:
       task = repo.get(task_id)
       if task is None:
           raise HTTPException(status_code=404, detail="Task not found")
       return task


   @app.get("/tasks/")
   def list_tasks() -> list[Task]:
       return repo.get_all()


   @app.delete("/tasks/{task_id}", status_code=204)
   def delete_task(task_id: int):
       if not repo.delete(task_id):
           raise HTTPException(status_code=404, detail="Task not found")

Test that tasks persist across server restarts.


Exercise 7: Discussion - Schema Migrations
------------------------------------------

When your data model changes (e.g., adding a ``due_date`` field), existing data in the database may become incompatible.

Discuss in your group:

- What happens if you add a new required column to the database?
- How would you handle existing rows that don't have the new field?
- What strategies exist for migrating data schemas?

.. hint::

   Tools like `Alembic <https://alembic.sqlalchemy.org/>`__ or `yoyo-migrations <https://ollycope.com/software/yoyo/latest/>`__ help manage database migrations in Python.


Reflection Questions
++++++++++++++++++++

- What are the advantages of the Repository Pattern?
- How does the pattern make testing easier?
- When would you choose JSON files over a database?
- What would change if you switched from DuckDB to PostgreSQL?

.. seealso::

   - `Repository Pattern explanation <https://martinfowler.com/eaaCatalog/repository.html>`__
   - `SQLModel - Pydantic + SQLAlchemy <https://sqlmodel.tiangolo.com/>`__
   - `DuckDB Python API <https://duckdb.org/docs/api/python/overview>`__
