
Best Practices
==============

.. topic:: Goal

   Apply common patterns for production-ready FastAPI applications.


Exercise 1: Explore the OpenAPI Schema
--------------------------------------

Start your FastAPI app and visit ``/docs`` to see the interactive documentation.

Export the schema as JSON:

.. code-block:: bash

   curl http://localhost:8000/openapi.json > schema.json

This schema can be used to generate client libraries or validate API contracts.


Exercise 2: Configuration with Pydantic
---------------------------------------

Use ``pydantic-settings`` to load configuration from environment variables:

.. code-block:: bash

   uv add pydantic-settings

.. code-block:: python

   from pydantic_settings import BaseSettings

   class Settings(BaseSettings):
       model_path: str = "model.pkl"
       debug: bool = False

   settings = Settings()

Set values via environment variables: ``MODEL_PATH=./models/v2.pkl``


Exercise 3: Cache Expensive Resources
-------------------------------------

Load models or database connections once at startup:

.. code-block:: python

   from functools import lru_cache

   @lru_cache
   def get_model():
       return load_model(settings.model_path)

   @app.get("/predict")
   def predict(model=Depends(get_model)):
       ...


Discussion Topics
-----------------

- How would you version your API? (URL path vs. header vs. query parameter)
- When to use integration tests vs. unit tests?
- How do you handle breaking changes to your schema?
