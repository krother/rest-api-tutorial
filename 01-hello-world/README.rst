Getting started with FastAPI
============================

.. topic:: Goal

   In this chapter, you build an end-to-end REST API microservice with GET requests for querying data.

Lifecycle of an HTTP Request in FastAPI
---------------------------------------

.. mermaid::

   sequenceDiagram
       participant Client
       participant Uvicorn
       participant FastAPI
       participant Endpoint

       Client->>Uvicorn: HTTP Request
       Uvicorn->>FastAPI: ASGI Request
       FastAPI->>FastAPI: Route matching
       FastAPI->>FastAPI: Call middleware
       FastAPI->>FastAPI: Dependency resolution
       FastAPI->>FastAPI: Validate parameters
       FastAPI->>Endpoint: Call function
       Endpoint->>Endpoint: Business logic
       Endpoint-->>FastAPI: Return value
       FastAPI-->>FastAPI: Serialize response
       FastAPI-->>Uvicorn: ASGI Response
       Uvicorn-->>Client: HTTP Response


When a client sends a request to your FastAPI application, it travels through several layers:

1. **Client sends request**: A browser, curl, or Python client sends an HTTP request to the server
2. **The Uvicorn ASGI server receives the request**: Uvicorn accepts the connection and parses the raw HTTP data. The ASGI(Asynchronous Server Gateway Interface) enables async support for high-performance applications
3. **Routing**: The request URL is matched against registered path operations. Middleware is called. Both are handled by the `starlette` library
4. **Dependency resolution**: FastAPI resolves any dependencies declared in the endpoint
5. **Parameter validation**: Path, query, and body parameters are extracted and validated
6. **Call endpoint**: Your Python function runs and produces a return value
7. **Response serialization**: The return value is converted to JSON (or other format)
8. **Response sent**: The HTTP response travels back through Uvicorn to the client 


HTTP Status Codes
-----------------

Here are the most common HTTP status codes you'll encounter when building APIs:

.. list-table::
   :header-rows: 1
   :widths: 15 30 55

   * - Code
     - Name
     - When to use
   * - 200
     - OK
     - Request succeeded (default for GET)
   * - 201
     - Created
     - Resource was created successfully (use for POST)
   * - 400
     - Bad Request
     - Client sent invalid data
   * - 401
     - Unauthorized
     - Authentication required or failed
   * - 404
     - Not Found
     - Requested resource doesn't exist
   * - 422
     - Unprocessable Entity
     - Validation error (FastAPI's default for invalid input)
   * - 500
     - Internal Server Error
     - Something went wrong on the server

Parameter Types
---------------

FastAPI supports three main ways to pass data to an endpoint:

**Path Parameters** 
    Values embedded directly in the URL path. Commonly used for identifying resources (data objects).

    .. code-block:: python

        @app.get("/penguins/{penguin_id}")
        def get_penguin(penguin_id: int):
            ...

**Query Parameters**
    Key-value pairs appended to the URL after ``?``. Commonly used for optional filters, pagination, or search terms.

    Example: ``/penguins?species=Adelie&min_weight=3000``

    .. code-block:: python

        @app.get("/penguins")
        def list_penguins(species: str, min_weight: int|None):
            ...

**Body Parameters**
    Data sent in the request body, typically as JSON. Used for complex data or when creating/updating resources.

    .. code-block:: python

        from pydantic import BaseModel

        class PenguinUpdate(BaseModel):
            penguin_id: int
            beak_length: float

        @app.post("/penguins/update")
        def update_penguins(penguin: PenguinUpdate):
            ...


Exercise 1: Set Up the Environment
----------------------------------

Create new folder for the project and place the following ``pyproject.toml`` file there:

.. literalinclude:: pyproject.toml

Then use the ``uv`` package manager to create a virtual environment:

.. code-block:: bash

    python -m pip install uv
    uv sync

You should see several packages being downloaded. a ``.venv`` folder should appear.

Exercise 2: Hello World API
---------------------------

Create a file ``app.py`` with a minimal FastAPI application:

.. literalinclude:: app.py

.. seealso::
    
   `fastapi.tiangolo.com/#example <https://fastapi.tiangolo.com/#example>`__

Exercise 3: Run the Server
--------------------------

Start the FastAPI development server:

.. code-block:: bash

    uv run fastapi dev app.py

Visit these URLs in your browser:

- `http://localhost:8000/ <http://localhost:8000/>`__ - Your API root
- `http://localhost:8000/docs <http://localhost:8000/docs>`__ - Interactive Swagger UI documentation
- `http://localhost:8000/redoc <http://localhost:8000/redoc>`__ - ReDoc documentation (read-only, cleaner layout)

.. hint::

   Swagger UI (``/docs``) allows you to send requests interactively - useful for testing.
   ReDoc provides a more streamlined, readable view of your API documentation.


Exercise 4: Build a Penguin API with Path Parameters
----------------------------------------------------

In the next three exercises, you will extend your API to serve data from the **Palmer Penguins Dataset**.
You will try all three parameter types.

First, the API will need to load the penguins internally. You should already have ``polars`` installed in the virtual environment. Place the file :download:`penguins.csv` in the same folder as your app. Read the data in ``app.py``:

.. code-block:: python

    import polars as pl
    from pathlib import Path

    filename = Path(__file__).parent / 'penguins.csv'
    df = pl.read_csv(filename)

Now add the following endpoint, so that it returns a penguin entry:

.. code-block:: python

    @app.get("/penguins/{penguin_id}")
    def get_penguin(penguin_id: int):
        selected = df.filter(id=penguin_id)
        return selected.to_dicts()

Try out the endpoint as a raw URL or on the ``docs/`` page. You should be able to retrieve penguin records.

Exercise 5: Create a GET endpoint with Query Parameters
-------------------------------------------------------

Let's search for penguins. 
This time, we need an endpoint with filter parameters.
These will become URL parameters.
To search, use the ``.filter()`` method. Here is an example:

.. code-block:: python

    @app.get("/penguins/")
    def list_penguins(species: str, min_weight: float | None = None):
        result = df.filter(pl.col("species") == ...)
        return ...


- Complete the function.
- Take care of the optional ``min_weight`` parameter.
- Add another query parameter
- Try out everything

.. warning::

    The search endpoint has to be before the other endpoint with the path parameter if their names are overlapping.

Exercise 6: Extra Validation
----------------------------

If you'd like to restrict the valid species, try adding:

.. code-block:: python

    from typing import Literal

    PenguinSpecies = Literal["Adelie", "Chinstrap", "Gentoo"]

    def list_penguins(species: PenguinSpecies, ...):
        ...

You might already include some error handling, if nothing is found:
    
.. code-block:: python

   from fastapi import HTTPException

   if ...:
       raise HTTPException(status_code=404, detail="Penguin not found")



Exercise 7: Send requests with curl
-----------------------------------

To test your API from the command line, you need the ``curl`` program. 
Open a new terminal and test your API:

.. code-block:: bash

   # Basic request
   curl http://localhost:8000/

    # Path parameter
    curl http://localhost:8000/penguins/1

    # Query parameters
    curl "http://localhost:8000/penguins?species=Adelie"

    # Body parameter (POST with JSON)
    curl -X POST http://localhost:8000/penguins/predict \
         -H "Content-Type: application/json" \
         -d '{"bill_length": 45, "body_mass": 4500}'

.. hint::

    Try ``curl -v ...`` to inspect the HTTP headers.


Exercise 8: Send request with postman
-------------------------------------

install postman.

send a POST request to the /order/ endpoint. Set the **Body** of the request, using the **raw JSON** type:

{
    "name": "cat",
    "quantity": 7
}



Reflection Questions
--------------------

After completing the exercises, consider these questions:

- How does FastAPI know what documentation to generate on ``docs/``?
- What happens when you send the wrong data type to an endpoint? How does FastAPI communicate the error?
- Which status code does FastAPI return for successful GET requests? For validation errors?
- Why might you choose FastAPI over Django for a microservice?

.. seealso::

    - FastAPI official documentation: https://fastapi.tiangolo.com/
    - Pydantic documentation: https://docs.pydantic.dev/
    - OpenAPI specification: https://www.openapis.org/
