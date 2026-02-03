
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
---------------

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
     - Remove a resource, if successful, it typically returns status code 204.

Idempotency
-----------

An operation is **idempotent** if calling it multiple times has the same effect as calling it once.
This is important for building reliable APIs:

- **POST** is NOT idempotent (creating twice may create duplicates)
- **GET** is idempotent (reading data doesn't change it)
- **PUT** is idempotent (setting a value to X twice gives the same result)
- **DELETE** may or may not be idempotent (design choice)

Guidelines for choosing attributes
----------------------------------

Generic thoughts:
+++++++++++++++++

- stick to naming conventions (case etc)
- what does a missing value imply?
- what does an empty value imply?

**How would your attribute values distinguish the following**

.. code::

    Q: What color is your bike?

    A1: I don't know.

    A2: I am not telling you.

    A3: It has none.

    A4: None of the colors you know.

Identifiers:
++++++++++++

Choosing identifiers is trickier than you might think.
In many cases you want your identifiers to be:

- unique
- permanent (created only once per lifetime of the API)
- unpredictable (to prevent attackers from guessing ids and for better sharding)
- using ASCII character only
- fast (not too long)
- information-dense
- checkable (to recognize typos)
- shareable / easy to read and copy
- random bytes are good
- UUIDs are discouraged (rather long)

A good practice is to use **Crockford Base 32 characters** (a-z,0-9 but none of ``ilou`` and append the modulus by 37 as a checksum.

.. note::

    In many cases, you will want your API to take care of assinging identifiers,
    although exceptions do exist.


Numeric values:
+++++++++++++++

- include a unit in the name if applicable
- enforce boundaries (also because boundaries differ among programming languages)
- how much numerical precision do you need?
- will you need to compare floats for equality (try 0.1 + 0.2)
- what time zone do timestamps refer to?
- consider serializing large numbers to strings

String values:
++++++++++++++

- is there a minimum or maximum length?
- are there special values like `"default"`?
- is there a maximum length for values of lists?
- is there a maximum length for keys/values of dictionaries?


Exercise 1: Design a Resource Layout
------------------------------------

Draw a class diagram for the **resource layout** of a **multi-user todo-list application**.
Go through the following sub-tasks:

- Which entities do you need? (users, lists, tasks, ...)
- What attributes should each entity have?
- How are the entities related (one-to-many, many-to-many)?


Exercise 2: Create Pydantic Models
----------------------------------

Based on your design, create Pydantic models for the todo-list app.
Use the list of guidelines above for choosing attributes.
     
.. hint::

   In Pydantic, you can use ``datetime`` fields:

   .. code-block:: python

      from datetime import datetime
      from pydantic import BaseModel

      class MyEntity(BaseModel):
          ...
          created_at: datetime | None = None


Exercise 3: Decide on available Resources
-----------------------------------------

Designing a resource model is very similar to designing a data model in other contexts.
There is one noteworthy difference: not all entities might be available through the API directly.
When you have parent-child relationships, you have the following options:

- create separate endpoints for operations on the parent and child
- create endpoints for the parent and retrieve or modify the child objects as well.

This works, because the JSON objects allow to submit or return nested objects.

Exercise 4: Create Standard Endpoints
-------------------------------------

Create function headers for each available resource, covering the CRUD cases.
Here is a standard set of endpoints for a resource that is consistent and ideally idempotent.
Endpoints following the standard spec should not have side effects.

.. code::

    # create new
    POST /items/  -> Item

    # read one
    GET /items/<item-id>/ -> Item

    # read many
    GET /items/ -> [Item]

    # update
    PATCH /items/<item-id>/ -> Item

    # replace
    PUT /items/<item-id>/ -> Item

    # delete
    DELETE /items/<item-id> -> None

    # create new child item
    POST /items/<item-id>/child/ -> Child



Reflection Questions
--------------------

- What should happen when you try to delete a resource that doesn't exist?
- What should happen when a POST request with the same data is sent twice?
- Why is idempotency important for PUT but not for POST?

.. seealso::

   - `REST API design <https://restfulapi.net/>`__
   - `HTTP methods <https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods>`__
   - `FastAPI path operations <https://fastapi.tiangolo.com/tutorial/first-steps/>`__
