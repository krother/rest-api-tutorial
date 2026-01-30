Getting started with FastAPI
============================

.. topic:: Goal

   In this chapter, you build an end-to-end REST API microservice on top of a small Machine Learning model.

Contents
--------

- FastAPI architecture
- the lifecycle of an HTTP request
- the OpenAPI standard
- path, query, and body parameters
- HTTP status codes
- sending HTTP queries with postman, curl and httpx


How FastAPI Works
-----------------

FastAPI is a modern Python web framework for building REST APIs. Here is what makes it tick:

- **ASGI-based**: FastAPI runs on ASGI (Asynchronous Server Gateway Interface), enabling async/await support for high-performance applications
- **Pydantic validation**: Request and response data is automatically validated using Pydantic models and Python type hints
- **Automatic documentation**: OpenAPI (Swagger) and JSON Schema documentation are generated automatically from your code
- **Path operations**: Endpoints are defined using decorators like ``@app.get()``, ``@app.post()``, etc. that map HTTP methods to Python functions
- **Uvicorn/Hypercorn**: FastAPI apps are served by ASGI servers like Uvicorn that handle the actual HTTP connections
- **Starlette foundation**: Built on top of Starlette, providing routing, middleware, and other web framework essentials

Lifecycle of an HTTP Request
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When a client sends a request to your FastAPI application, it travels through several layers:

1. **Client sends request**: A browser, curl, or Python client sends an HTTP request to the server
2. **ASGI server receives it**: Uvicorn accepts the connection and parses the raw HTTP data
3. **Starlette routing**: The request URL is matched against registered path operations
4. **Dependency resolution**: FastAPI resolves any dependencies declared in the endpoint
5. **Parameter extraction**: Path, query, and body parameters are extracted and validated
6. **Endpoint execution**: Your Python function runs and produces a return value
7. **Response serialization**: The return value is converted to JSON (or other format)
8. **Response sent**: The HTTP response travels back through Uvicorn to the client 

.. mermaid::

   sequenceDiagram
       participant Client
       participant Uvicorn
       participant FastAPI
       participant Endpoint

       Client->>Uvicorn: HTTP Request
       Uvicorn->>FastAPI: ASGI Request
       FastAPI->>FastAPI: Route matching
       FastAPI->>FastAPI: Validate parameters
       FastAPI->>Endpoint: Call function
       Endpoint->>Endpoint: Business logic
       Endpoint-->>FastAPI: Return value
       FastAPI-->>FastAPI: Serialize response
       FastAPI-->>Uvicorn: ASGI Response
       Uvicorn-->>Client: HTTP Response

Parameter Types
~~~~~~~~~~~~~~~

FastAPI supports three main ways to pass data to an endpoint:

**Path Parameters**
    Values embedded directly in the URL path. Used for identifying specific resources.

    Example: ``/items/42`` where ``42`` is the path parameter

    .. code-block:: python

        @app.get("/items/{item_id}")
        def get_item(item_id: int):
            return {"item_id": item_id}

**Query Parameters**
    Key-value pairs appended to the URL after ``?``. Used for optional filters, pagination, or search terms.

    Example: ``/items?skip=10&limit=5``

    .. code-block:: python

        @app.get("/items")
        def list_items(skip: int = 0, limit: int = 10):
            return {"skip": skip, "limit": limit}

**Body Parameters**
    Data sent in the request body, typically as JSON. Used for complex data or when creating/updating resources.

    .. code-block:: python

        from pydantic import BaseModel

        class Item(BaseModel):
            name: str
            price: float

        @app.post("/items")
        def create_item(item: Item):
            return {"name": item.name, "price": item.price}

HTTP Status Codes
~~~~~~~~~~~~~~~~~

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

Getting Started
---------------

Exercise 1: Set Up the Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a virtual environment and install dependencies:

.. code-block:: bash

    python -m pip install uv
    uv sync

Exercise 2: Create Hello World
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a file ``app.py`` with a minimal FastAPI application:

.. literalinclude:: app.py

Reference: https://fastapi.tiangolo.com/#example

Exercise 3: Run the Server
~~~~~~~~~~~~~~~~~~~~~~~~~~

Start the FastAPI development server:

.. code-block:: bash

    uv run fastapi dev app.py

Visit these URLs in your browser:

- http://localhost:8000/ - Your API root
- http://localhost:8000/docs - Interactive Swagger UI documentation
- http://localhost:8000/redoc - ReDoc documentation (read-only, cleaner layout)

.. hint::

   ReDoc provides a streamlined, readable view of your API documentation.
   Swagger UI (``/docs``) allows you to send requests interactively - useful for testing.

Exercise 4: Make Requests with curl
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Open a new terminal and test your API:

.. code-block:: bash

   # Basic request
   curl http://localhost:8000/

   # Path parameter (integer)
   curl http://localhost:8000/items/3

   # Path + query parameter
   curl http://localhost:8000/items/3?q=cat

   # Invalid path parameter (string instead of int)
   curl http://localhost:8000/items/abc?q=cat

   # Verbose output to see headers and status codes
   curl -v http://localhost:8000/items/abc?q=cat

Notice how FastAPI automatically returns a 422 error with details when validation fails.

Exercise 5: Explore the OpenAPI Specification
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Go to http://localhost:8000/redoc
2. Click the "Download" button to get the OpenAPI JSON specification
3. Examine the structure and identify:

   - What endpoints are documented?
   - What parameters does each endpoint accept?
   - What response schemas are defined?

The OpenAPI specification enables automatic client generation, testing tools, and documentation.

Exercise 6: Build a Penguin API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Extend your ``app.py`` to create a small penguin database API with all three parameter types.

**Step 1: Add sample data**

Add a simple in-memory "database" at the top of your file:

.. code-block:: python

    penguins = {
        1: {"name": "Pingu", "species": "Emperor", "weight": 23.5},
        2: {"name": "Skipper", "species": "Adelie", "weight": 5.2},
        3: {"name": "Private", "species": "Chinstrap", "weight": 4.8},
    }

**Step 2: Create a GET endpoint with path parameter**

Create an endpoint to retrieve a penguin by ID:

.. code-block:: python

    @app.get("/penguins/{penguin_id}")
    def get_penguin(penguin_id: int):
        if penguin_id not in penguins:
            raise HTTPException(status_code=404, detail="Penguin not found")
        return penguins[penguin_id]

Don't forget to import ``HTTPException`` from ``fastapi``.

**Step 3: Create a GET endpoint with query parameters**

Create an endpoint to list penguins with optional filtering:

.. code-block:: python

    @app.get("/penguins")
    def list_penguins(species: str | None = None, min_weight: float | None = None):
        result = list(penguins.values())
        if species:
            result = [p for p in result if p["species"] == species]
        if min_weight:
            result = [p for p in result if p["weight"] >= min_weight]
        return result

**Step 4: Create a POST endpoint with body parameter**

Create a Pydantic model and endpoint to add new penguins:

.. code-block:: python

    from pydantic import BaseModel

    class PenguinCreate(BaseModel):
        name: str
        species: str
        weight: float

    @app.post("/penguins", status_code=201)
    def create_penguin(penguin: PenguinCreate):
        new_id = max(penguins.keys()) + 1
        penguins[new_id] = penguin.model_dump()
        return {"id": new_id, **penguins[new_id]}

**Step 5: Test your endpoints**

Test each endpoint type using curl:

.. code-block:: bash

    # Path parameter
    curl http://localhost:8000/penguins/1

    # Query parameters
    curl "http://localhost:8000/penguins?species=Adelie"
    curl "http://localhost:8000/penguins?min_weight=5.0"

    # Body parameter (POST with JSON)
    curl -X POST http://localhost:8000/penguins \
         -H "Content-Type: application/json" \
         -d '{"name": "Kowalski", "species": "Adelie", "weight": 5.5}'

Exercise 7: Connect the ML Model
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now let's connect a real machine learning model to predict penguin species.
The file ``model.pkl`` contains a trained scikit-learn model that predicts the species
of a penguin based on its body mass and beak length.

**Step 1: Load the model at startup**

Add model loading at the top of your ``app.py``:

.. code-block:: python

    import pickle
    from pathlib import Path

    # Load the ML model
    model_path = Path(__file__).parent / "model.pkl"
    with open(model_path, "rb") as f:
        model = pickle.load(f)

**Step 2: Create the request model**

Define a Pydantic model for the prediction input:

.. code-block:: python

    class PredictionInput(BaseModel):
        body_mass: float      # in grams
        beak_length: float    # in millimeters

**Step 3: Create the response model**

Define what the API will return:

.. code-block:: python

    class PredictionOutput(BaseModel):
        species: str
        probability: float

**Step 4: Create the prediction endpoint**

.. code-block:: python

    @app.post("/predict", response_model=PredictionOutput)
    def predict_species(data: PredictionInput):
        # Prepare input for the model
        features = [[data.body_mass, data.beak_length]]

        # Get prediction and probability
        prediction = model.predict(features)[0]
        probabilities = model.predict_proba(features)[0]
        confidence = float(max(probabilities))

        return PredictionOutput(
            species=prediction,
            probability=confidence
        )

**Step 5: Test the prediction endpoint**

.. code-block:: bash

    # Predict species for a penguin with body mass 4200g and beak length 39mm
    curl -X POST http://localhost:8000/predict \
         -H "Content-Type: application/json" \
         -d '{"body_mass": 4200.0, "beak_length": 39.0}'

Try different values and see how the predictions change:

- Large body mass (5000+) with medium beak → likely Emperor
- Small body mass (3500) with short beak → likely Adelie
- Medium body mass with long beak → likely Chinstrap

**Bonus: Add input validation**

Enhance your model with validation to reject unrealistic values:

.. code-block:: python

    from pydantic import BaseModel, Field

    class PredictionInput(BaseModel):
        body_mass: float = Field(gt=2000, lt=7000, description="Body mass in grams")
        beak_length: float = Field(gt=30, lt=60, description="Beak length in mm")


Reflection Questions
--------------------

After completing the exercises, consider these questions:

1. **HTTP Headers**: How can you check what HTTP headers are being sent in a request? (Hint: try ``curl -v``)

2. **Validation**: What happens when you send the wrong data type to an endpoint? How does FastAPI communicate the error?

3. **Documentation**: How does FastAPI know what documentation to generate? Where does that information come from?

4. **Status Codes**: Which status code does FastAPI return for successful GET requests? For validation errors?

5. **Architecture**: Why might you choose FastAPI over Flask or Django for a microservice?

.. seealso::

    - FastAPI official documentation: https://fastapi.tiangolo.com/
    - Pydantic documentation: https://docs.pydantic.dev/
    - OpenAPI specification: https://www.openapis.org/
