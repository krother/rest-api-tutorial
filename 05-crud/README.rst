
Data-centric APIs
=================

.. topic:: Goal

   In this chapter, you implement a data-centric REST API with standard endpoints for creating, reading, updating and deleting resources.

In a data-centric API, the central concept is the **resource**.
A resource is any data object that can be identified, accessed, and manipulated through the API.
Examples include users, products, orders, or tasks.

Each resource typically has:

- A unique identifier (ID)
- A set of attributes
- Relationships to other resources

CRUD Operations
+++++++++++++++

CRUD stands for the four basic operations on resources:

.. list-table::
   :header-rows: 1
   :widths: 15 15 50

   * - Operation
     - HTTP Method
     - Description
   * - Create
     - POST
     - Add a new resource
   * - Read
     - GET
     - Retrieve one or more resources
   * - Update
     - PUT / PATCH
     - Modify an existing resource
   * - Delete
     - DELETE
     - Remove a resource

Idempotency
+++++++++++

An operation is **idempotent** if calling it multiple times has the same effect as calling it once.
This is important for building reliable APIs:

- **GET** is idempotent (reading data doesn't change it)
- **PUT** is idempotent (setting a value to X twice gives the same result)
- **DELETE** is idempotent (deleting twice has the same outcome)
- **POST** is NOT idempotent (creating twice may create duplicates)

Exercise 1: Design a Data Model
-------------------------------

Draw a class diagram for a **multi-user todo-list application**.
Consider:

- What entities do you need? (users, lists, tasks, ...)
- What attributes does each entity have?
- How are the entities related?

.. hint::

   In Pydantic, you can use ``datetime`` fields:

   .. code-block:: python

      from datetime import datetime
      from pydantic import BaseModel

      class Task(BaseModel):
          title: str
          created_at: datetime
          due_date: datetime | None = None


Exercise 2: Create Pydantic Models
----------------------------------

Based on your design, create Pydantic models for the todo-list app.
Start with a ``Task`` and ``TodoList`` model:

.. code-block:: python

    from pydantic import BaseModel
    from datetime import datetime

    class Task(BaseModel):
        id: int
        title: str
        completed: bool = False
        created_at: datetime

    class TodoList(BaseModel):
        id: int
        name: str
        tasks: list[Task] = []

Store tasks in-memory using a dictionary:

.. code-block:: python

    tasks: dict[int, Task] = {}


Exercise 3: Implement GET Endpoints
-----------------------------------

Create endpoints to read tasks:

.. code-block:: python

    @app.get("/tasks/{task_id}")
    def get_task(task_id: int) -> Task:
        if task_id not in tasks:
            raise HTTPException(status_code=404, detail="Task not found")
        return tasks[task_id]


    @app.get("/tasks/")
    def list_tasks(completed: bool | None = None) -> list[Task]:
        result = list(tasks.values())
        if completed is not None:
            result = [t for t in result if t.completed == completed]
        return result


Exercise 4: Implement POST to Create
------------------------------------

Add an endpoint to create new tasks:

.. code-block:: python

    class TaskCreate(BaseModel):
        title: str

    @app.post("/tasks/", status_code=201)
    def create_task(data: TaskCreate) -> Task:
        task_id = len(tasks) + 1
        task = Task(
            id=task_id,
            title=data.title,
            created_at=datetime.now()
        )
        tasks[task_id] = task
        return task

Test it:

.. code-block:: bash

    curl -X POST http://localhost:8000/tasks/ \
         -H "Content-Type: application/json" \
         -d '{"title": "Buy groceries"}'


Exercise 5: Implement PUT to Update
-----------------------------------

Add an endpoint to update existing tasks:

.. code-block:: python

    class TaskUpdate(BaseModel):
        title: str | None = None
        completed: bool | None = None

    @app.put("/tasks/{task_id}")
    def update_task(task_id: int, data: TaskUpdate) -> Task:
        if task_id not in tasks:
            raise HTTPException(status_code=404, detail="Task not found")

        task = tasks[task_id]
        if data.title is not None:
            task.title = data.title
        if data.completed is not None:
            task.completed = data.completed
        return task


Exercise 6: Implement DELETE
----------------------------

Add an endpoint to delete tasks:

.. code-block:: python

    @app.delete("/tasks/{task_id}", status_code=204)
    def delete_task(task_id: int):
        if task_id not in tasks:
            raise HTTPException(status_code=404, detail="Task not found")
        del tasks[task_id]

Test it:

.. code-block:: bash

    curl -X DELETE http://localhost:8000/tasks/1

.. note::

   Status code 204 (No Content) is typical for successful DELETE operations.

Reflection Questions
++++++++++++++++++++

- What should happen when you try to delete a resource that doesn't exist?
- What should happen when a POST request with the same data is sent twice?
- Why is idempotency important for PUT but not for POST?
- How would you implement pagination for the list endpoint?

.. seealso::

   - REST API design: https://restfulapi.net/
   - HTTP methods: https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods
   - FastAPI path operations: https://fastapi.tiangolo.com/tutorial/first-steps/
