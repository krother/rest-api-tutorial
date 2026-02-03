
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
----------------------

Pydantic models can be easily converted to and from JSON, which is useful for file-based storage and debugging.

.. code-block:: python

   from pydantic import BaseModel

   class Cat(BaseModel):
       id: int
       name: str
       color: str

   cat = Cat(id=1, name="Felix", color="orange")

   # convert to JSON string
   j = cat.model_dump_json()

   # convert to dictionary
   data = cat.model_dump()

   # parse from JSON string
   cat2 = Cat.model_validate_json(j)

   # parse from dictionary
   cat3 = Cat.model_validate(data)


Exercise 1: Dump todo-lists to JSON
-----------------------------------

Adapt the code above to implement two functions:

- write todo-list data to a JSON file.
- read todo-list data from a JSON file.


.. hint::

    To save an object with ``datetime`` attributes, use:

    .. code-block:: python
   
       j = myobject.model_dump(mode="json")

Test the function.


Exercise 2: Store Tasks in DuckDB
---------------------------------

DuckDB is a lightweight database engine that requires no server setup.
Install it with:

.. code-block:: bash

   uv add duckdb

Create a connection and store tasks. Adapt the code to your data model:

.. code-block:: python

   import duckdb

   # Create an in-memory database
   con = duckdb.connect()

   # Create a table
   con.execute("""
       CREATE TABLE tasks (
           id INTEGER PRIMARY KEY,
           ...
       )
   """)

   task = Task(id=1, title="Buy groceries", completed=False, created_at=datetime.now())
   con.execute(
       "INSERT INTO tasks VALUES (?, ?, ?, ?)",
       [task.id, task.title, task.completed, task.created_at]
   )

.. note::

   For persistent storage, use ``duckdb.connect("tasks.db")`` instead.


Exercise 3: Read Tasks from DuckDB
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
       ...
       
Test the queries.


Exercise 4: Implement a Repository Class
----------------------------------------

Move the database code into a dedicated repository class in a separate file ``repository.py``:

.. code-block:: python

   import duckdb


   class TaskRepository:

       def __init__(self, db_path: str = ":memory:"):
           self.con = duckdb.connect(db_path)
           self.create_table()

       def create_table(self):
           self.con.execute("""
               CREATE TABLE IF NOT EXISTS tasks (
                   id INTEGER PRIMARY KEY,
                   title VARCHAR,
                   completed BOOLEAN,
                   created_at TIMESTAMP
               )
           """)

       def add(self, task: Task) -> Task:
           ...

       def get(self, task_id: int) -> Task | None:
           ...

       def get_all(self) -> list[Task]:
           ...

       def update(self, task: Task) -> Task:
           ...

       def delete(self, task_id: int) -> bool:
           ...

.. note::

    The repository functions may or may not match the resource model of your API.
    Sometimes, you may need to map the database objects to entities of your resource layout.
    The point of the Repository pattern is that both the data model and the resource model can change independently.


Exercise 5: Use the Repository in FastAPI
-----------------------------------------

Connect the repository to your API endpoints.

Make sure that your todo-items persist across server restarts.


Exercise 6: Discuss Schema Migration
------------------------------------

When your data model changes (e.g., adding a ``due_date`` field), existing data in the database may become incompatible.

Discuss in your group:

- What happens if you add a new required column to the database?
- How would you handle existing rows that don't have the new field?
- What strategies exist for migrating data schemas?

.. hint::

   Tools like `Alembic <https://alembic.sqlalchemy.org/>`__ or `yoyo-migrations <https://ollycope.com/software/yoyo/latest/>`__ help manage database migrations in Python.


Reflection Questions
--------------------

- What are the advantages of the Repository Pattern?
- How does the pattern make testing easier?
- When would you choose JSON files over a database?
- What would change if you switched from DuckDB to PostgreSQL?

.. seealso::

   - `Repository Pattern explanation <https://martinfowler.com/eaaCatalog/repository.html>`__
   - `SQLModel - Pydantic + SQLAlchemy <https://sqlmodel.tiangolo.com/>`__
   - `DuckDB Python API <https://duckdb.org/docs/api/python/overview>`__
