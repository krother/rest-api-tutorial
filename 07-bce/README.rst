
Structuring a Larger API
========================

.. topic:: Goal

   In this chapter, you structure your API using the BCE (Boundary-Control-Entity) pattern to create a maintainable, testable codebase.


As your API grows, keeping all code in a single file becomes unmanageable.
The **BCE Pattern (Boundary-Control-Entity)** separates your code into three layers:

.. mermaid::

   flowchart LR
       subgraph Boundary
           A[API endpoints]
           B[top-level functions]
       end
       subgraph Control
           C[Services]
       end
       subgraph Entity
           D[Repository]
           E[Business Objects]
       end

       A --> B
       B --> C
       C --> D
       C --> E

- **Boundary**: Entry points to your application (the public interface)
- **Control**: Business logic and orchestration (services)
- **Entity**: Data models and persistence (repositories, database models)

The key principle is that **dependencies point inward**: Boundaries depend on Control, Control depends on Entity.
The Entity knows nothing about the outer layers.


Exercise 1: Create a Clean Project Structure
--------------------------------------------

Set up a proper Python package structure for your todo-list API.

Initialize the project with ``uv``:

.. code-block:: bash

   uv init

Update ``pyproject.toml``:

.. literalinclude:: pyproject.toml

Exercise 2: Create the Folder Structure
---------------------------------------

We want to create a REST API with two separate applications: the penguin prediction and the todo-list.
Set up the following folder structure:

.. code-block:: text

   my_project/
   ├── pyproject.toml
   ├── README.md
   ├── my_app/
       ├── app.py
       ├── pingu_predictor/
           ├── __init__.py
           ├── endpoints.py
           ├── boundary.py
           ├── models.py
           └── services.py
       └── todo_list/
           ├── __init__.py
           ├── endpoints.py
           ├── boundary.py
           ├── models.py
           └── services.py
   └── tests/
       ├── test_pingu_predictor.py
       └── test_todo_list.py


Exercise 3: Define Endpoints
----------------------------

In the ``endpoints.py``, you want to have lean endpoints that contain the request and response objects and nothing else. Here is an example:

.. code-block:: python

   from fastapi import APIRouter

   router = APIRouter()

   @router.post("/tasks/", status_code=201)
   def create_task(data: TaskCreate) -> Task:
       ...

Leave the body of the endpoints empty for now or leave existing code there.

In the main ``app.py``, you need to import your endpoints:

.. code-block:: python

   from fastapi import Depends, FastAPI
   import pingu_predictor
   
   app = FastAPI(dependencies=[Depends(get_user)]) # <-- optional: auth for all endpoints

   app.include_router(pingu_predictor.endpoints.router)
   
   # alternative with more details
   app.include_router(
       todolist.endpoints.router,
       prefix="/todo-list",
       tags=["admin"],
       dependencies=[Depends(get_token_header)],
       responses={418: {"description": "I'm a teapot"}},
   )


.. seealso::

    `FastAPI guide to distribute an app over multiple modules <https://fastapi.tiangolo.com/tutorial/bigger-applications/#apirouter>`__


Exercise 4: Define Boundaries
-----------------------------

The ``boundary.py`` file contains public functions that other parts of your program may use.
They are:

- very thin functions
- non-HTTP replicas of your endpoints
- do not know anything about HTTP
- allow the different parts of your app to call each other.
- delegating all logic to the service layer
- may be omitted if you only need the endpoints

.. code-block:: python

   def create_task(data: TaskCreate) -> Task:
       ...

.. note::

    The Boundary file may seem unnecessary at first.
    It only pays off in a larger API.


Exercise 5: Create Entities
---------------------------

The Entity layer contains your **Business Objects**. It also is a good place for your repository.
In the ``models.py`` file, you collect:

- your **resource model** (the main classes for the data your API is working with)
- request / response classes as necessary
- thin classes without a lot of logic


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

Move the repository from the previous chapter to ``repository.py``.


Exercise 6: Create the Control Layer
------------------------------------

The Control layer contains your entire business logic.
Create a file ``services.py``.
Here you can create whatever functions or classes you want to get the job done.

.. code-block:: python

    def create_task(self, data: TaskCreate) -> Task:
        ...

    def get_task(self, task_id: int) -> Task | None:
        ...

    def list_tasks(self, completed: bool | None = None) -> list[Task]:
        ...

    def delete_task(self, task_id: int) -> bool:
        ...

Call these functions from the Boundary layer.

.. note::

    The service layer should not know anything about HTTP or FastAPI.
    Use custom Exception classes, not HTTP errors.


Exercise 7: Data Transfer Objects
---------------------------------

Sometimes your database model differs from your API model.
For example, the database might store additional fields that you do not want to expose.
You may want to define extra **data transfer objects** in a separate file ``dto.py``.

In that case, create mapping functions to convert between the dto and your entities.
This separation allows you to:

- Hide internal fields from the API
- Change the database schema without breaking the API
- Add computed fields to the response


Exercise 8: Adjust Tests
------------------------

Adjust the imports of your tests.
Then run the tests:

.. code-block:: bash

   uv run pytest tests/ -v


Reflection Questions
--------------------

- What are the advantages of the BCE pattern?
- Which parts of the BCE pattern are considered public?
- How does separating layers make testing easier?
- What belongs in the service layer vs. the repository layer?

.. seealso::

   - `Clean Architecture by Robert C. Martin <https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html>`__
   - `BCE Pattern by Robert C. Martin Video <https://www.youtube.com/watch?v=sn0aFEMVTpA&t=570s>`__
   - `Hexagonal Architecture <https://alistair.cockburn.us/hexagonal-architecture/>`__
   - `FastAPI Dependency Injection <https://fastapi.tiangolo.com/tutorial/dependencies/>`__
