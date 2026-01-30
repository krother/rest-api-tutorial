
Pydantic Models
===============

.. topic:: Goal

   In this chapter, you extend the penguin prediction API with robust data validation using Pydantic models.

**Pydantic** is a Python library for data validation using type hints.
It converts input data to Python types, validates constraints automatically,
and provides clear error messages when validation fails.
FastAPI uses Pydantic for request/response serialization,
making your API type-safe with minimal code.

----

Exercise 1: Define Request Types
--------------------------------

Copy your ``app.py`` from chapter 01 or create a new file with the prediction endpoint.
Define the request body as a Pydantic ``BaseModel``:

.. code-block:: python

    from pydantic import BaseModel

    class PredictionInput(BaseModel):
        body_mass: float
        beak_length: float

    @app.post("/predict")
    def predict_species(data: PredictionInput):
        ...

Test that validation works by sending invalid data:

.. code-block:: bash

    # This should return a 422 error
    curl -X POST http://localhost:8000/predict \
         -H "Content-Type: application/json" \
         -d '{"body_mass": "not a number", "beak_length": 39.0}'

Notice how Pydantic automatically validates types and returns detailed error messages.

----

Exercise 2: Optional and Default Fields
---------------------------------------

Extend your model to include optional fields and fields with default values:

.. code-block:: python

    class PredictionInput(BaseModel):
        body_mass: float
        beak_length: float
        flipper_length: float | None = None  # optional, defaults to None
        island: str = "Biscoe"               # optional with default value

**Your task:** Add these fields and test the endpoint with different combinations:

.. code-block:: bash

    # Minimal request (only required fields)
    curl -X POST http://localhost:8000/predict \
         -H "Content-Type: application/json" \
         -d '{"body_mass": 4200.0, "beak_length": 39.0}'

    # Full request (all fields)
    curl -X POST http://localhost:8000/predict \
         -H "Content-Type: application/json" \
         -d '{"body_mass": 4200.0, "beak_length": 39.0, "flipper_length": 195.0, "island": "Dream"}'

Check the ``/docs`` page to see how optional fields are displayed differently.

----

Exercise 3: Define a Response Model
-----------------------------------

Given this endpoint signature, write a ``PredictionOutput`` model from scratch:

.. code-block:: python

    @app.post("/predict", response_model=PredictionOutput)
    def predict_species(data: PredictionInput):
        features = [[data.body_mass, data.beak_length]]
        prediction = model.predict(features)[0]
        probabilities = model.predict_proba(features)[0]
        confidence = float(max(probabilities))

        return PredictionOutput(
            species=prediction,
            probability=confidence,
            input_data=data
        )

The response model should include:

- ``species``: a string
- ``probability``: a float
- ``input_data``: the original ``PredictionInput``

.. hint::

    You can nest Pydantic models inside each other.

----

Exercise 4: Add Nested Model Metadata
-------------------------------------

Create a ``ModelMetadata`` class that contains information about the ML model,
and include it in your response:

.. code-block:: python

    class ModelMetadata(BaseModel):
        model_name: str
        version: str
        trained_on: str

    class PredictionOutput(BaseModel):
        species: str
        probability: float
        input_data: PredictionInput
        metadata: ModelMetadata

Update your endpoint to return metadata:

.. code-block:: python

    @app.post("/predict", response_model=PredictionOutput)
    def predict_species(data: PredictionInput):
        ...
        return PredictionOutput(
            species=prediction,
            probability=confidence,
            input_data=data,
            metadata=ModelMetadata(
                model_name="PenguinClassifier",
                version="1.0.0",
                trained_on="Palmer Penguins Dataset"
            )
        )

Verify that the nested structure appears correctly in the response.

----

Exercise 5: Forbid Extra Attributes
-----------------------------------

By default, Pydantic ignores extra fields in the input.
Configure your model to reject requests with unknown fields:

.. code-block:: python

    from pydantic import ConfigDict

    class PredictionInput(BaseModel):
        model_config = ConfigDict(extra="forbid")

        body_mass: float
        beak_length: float
        flipper_length: float | None = None
        island: str = "Biscoe"

Test that extra fields are now rejected:

.. code-block:: bash

    # This should return a 422 error
    curl -X POST http://localhost:8000/predict \
         -H "Content-Type: application/json" \
         -d '{"body_mass": 4200.0, "beak_length": 39.0, "unknown_field": "oops"}'

.. hint::

    Other useful config options: ``str_strip_whitespace``, ``validate_default``, ``frozen``

----

Exercise 6: Custom Validator
----------------------------

Add a validator to ensure penguin body mass is realistic (between 500g and 20kg):

.. code-block:: python

    from pydantic import field_validator

    class PredictionInput(BaseModel):
        model_config = ConfigDict(extra="forbid")

        body_mass: float
        beak_length: float
        flipper_length: float | None = None
        island: str = "Biscoe"

        @field_validator("body_mass")
        @classmethod
        def validate_body_mass(cls, v):
            if v < 500 or v > 20000:
                raise ValueError("body_mass must be between 500g and 20000g")
            return v

Test the validator:

.. code-block:: bash

    # Too light - should fail
    curl -X POST http://localhost:8000/predict \
         -H "Content-Type: application/json" \
         -d '{"body_mass": 100.0, "beak_length": 39.0}'

    # Too heavy - should fail
    curl -X POST http://localhost:8000/predict \
         -H "Content-Type: application/json" \
         -d '{"body_mass": 50000.0, "beak_length": 39.0}'

**Your task:** Add a validator for ``beak_length`` (realistic range: 30-60mm).

----

Exercise 7: Field Constraints and Annotated
-------------------------------------------

Pydantic offers two ways to add constraints without writing custom validators:

**Using Field():**

.. code-block:: python

    from pydantic import Field

    class PredictionInput(BaseModel):
        body_mass: float = Field(ge=500, le=20000, description="Body mass in grams")
        beak_length: float = Field(ge=30, le=60, description="Beak length in mm")

**Using Annotated:**

.. code-block:: python

    from typing import Annotated
    from pydantic import Field

    BodyMass = Annotated[float, Field(ge=500, le=20000, description="Body mass in grams")]
    BeakLength = Annotated[float, Field(ge=30, le=60, description="Beak length in mm")]

    class PredictionInput(BaseModel):
        body_mass: BodyMass
        beak_length: BeakLength

The ``Annotated`` approach lets you reuse type definitions across multiple models.

**Your task:** Refactor your model to use ``Field`` constraints.
Check the ``/docs`` page to see how the descriptions appear in the API documentation.

----

Exercise 8: Introduce Bugs
--------------------------

Practice debugging by introducing these bugs one at a time and observing the errors:

- Remove ``body_mass`` from the request
- Send a request to a non-existent endpoint
- Send a GET request instead of POST
- Add a runtime error inside the endpoint function (e.g., ``1/0``)
- Return a response that doesn't match the ``response_model``

For each bug, note:

1. What HTTP status code is returned?
2. What error message does FastAPI provide?
3. How would you fix it?

----

Reflection Questions
--------------------

1. **Validation**: When does Pydantic validation run - before or after your endpoint code?

2. **Documentation**: How do Field descriptions improve your API documentation?

3. **Error messages**: How would you customize error messages for end users?

4. **Performance**: What are the performance implications of using nested models?

.. seealso::

   - Pydantic documentation: https://docs.pydantic.dev/
   - FastAPI request body: https://fastapi.tiangolo.com/tutorial/body/
   - Pydantic validators: https://docs.pydantic.dev/latest/concepts/validators/
