
Pydantic Models
===============

.. topic:: Goal

   In this chapter, you extend the penguin API by a prediction backend and robust data validation using Pydantic models.

**Pydantic** is a Python library for data validation using type hints.
It converts input data to Python types, validates constraints automatically,
and provides clear error messages when validation fails.
FastAPI uses Pydantic for request/response serialization,
making your API type-safe with minimal code.


Exercise 1: Load a Predictive Model
-----------------------------------

Now we will connect a Machine Learning model that predicts a penguin species.
As input, the model needs the **beak length** and the **body mass** of a penguin.
It returns a most likely species and the predicted probability.

You find a trained scikit-learn model in a **pickle file** :download:`model.pkl`.
It uses **Logistic Regression**.
If you like, inspect the training code in :download:`train.py`

Add model loading at the top of your ``app.py``:

.. code-block:: python

    import pickle
    from pathlib import Path

    # Load the ML model
    model_path = Path(__file__).parent / "model.pkl"
    with open(model_path, "rb") as f:
        model = pickle.load(f)


Exercise 2: Create a POST endpoint with Body Parameter
------------------------------------------------------

To create a POST endpoint, you need to define the request as a Pydantic model.
In this case it contains all data for the prediction:

.. code-block:: python

    from pydantic import BaseModel

    class PenguinPredictionRequest(BaseModel):
        bill_length: float    # in millimeters
        body_mass: float      # in grams


    @app.post("/predict")
    def predict_species(data: PredictionInput):
        return "Adelie"  # dummy response

Test that the validation works by sending invalid data:

.. code-block:: bash

    # This should return a 422 error
    curl -X POST http://localhost:8000/predict \
         -H "Content-Type: application/json" \
         -d '{"body_mass": "not a number", "bill_length": 39.0}'

Notice how Pydantic automatically validates types and returns detailed error messages.


Exercise 3: Define a Response Model
-----------------------------------

Define another class ``PredictionOutput`` containing what the API will return:

.. code-block:: python

    class PredictionOutput(BaseModel):
        species: str
        probability: float

Extend the POST endpoint accordingly. Note that we can use a **type hint** in the function definition:

.. code-block:: python

    @app.post("/predict", response_model=PredictionOutput)
    def predict_species(data: PredictionInput) -> PredictionOutput:
        ... 

        return PredictionOutput(
            species=...,
            ...
        )

Test the endpoint.

Exercise 4: Plug in the predictive model
----------------------------------------

Now you need to call the model and extract the result.
The ``scikit-learn`` library allows to do this with minimal code.

Complete the gaps:

.. code-block:: python

    @app.post("/penguins/predict", response_model=PredictionOutput)
    def predict_penguin(request: PenguinPredictionRequest):
        features = [[...]]
        species = model.predict(features)[0]
        prob = max(model.predict_proba(features)[0])
        return PredictionOutput(...)

Try different values and see how the predictions change.



Exercise 5: Optional and Default Fields
---------------------------------------

Extend your model to include optional fields and fields with default values:

.. code-block:: python

    class PredictionInput(BaseModel):
        bill_length: float
        body_mass: float
        flipper_length: float | None = None  # optional, defaults to None
        island: str = "Biscoe"               # optional with default value

Add these fields and test the endpoint with different combinations.
**Do not** pass the new fields to the prediction. *

Here is an according curl request:

.. code-block:: bash

    # Full request (all fields)
    curl -X POST http://localhost:8000/predict \
         -H "Content-Type: application/json" \
         -d '{"body_mass": 4200.0, "bill_length": 39.0, "flipper_length": 195.0, "island": "Dream"}'


Check the ``/docs`` page to see how optional fields are displayed differently.

----

Exercise 6: Add Nested Model Metadata
-------------------------------------

Create a ``ModelMetadata`` class that contains information about the ML model.
Change the code so that the response of your endpoint looks like this:

.. code-block:: python

    return PredictionOutput(
        species=...,
        probability=...,
        ModelMetadata(
            model_name=str(model),
            version="1.0.0",
            trained_on="2026-01-30"
        )
    )

Verify that the nested structure appears correctly in the response.


Exercise 7: Forbid Extra Attributes
-----------------------------------

See what happens if you include an extra field in the input or the response.
The default behavior should be that pydantic ignores extra fields.

For a stricter quality check, configure your model to reject requests with unknown fields:

.. code-block:: python

    from pydantic import ConfigDict

    class PredictionInput(BaseModel):
        model_config = ConfigDict(extra="forbid")

        bill_length: float
        ...

Test that extra fields are now rejected:

.. code-block:: bash

    # This should return a 422 error
    curl -X POST http://localhost:8000/predict \
         -H "Content-Type: application/json" \
         -d '{"body_mass": 4200.0, "bill_length": 39.0, "unknown_field": "oops"}'

Add the same configuration to the output model as well.

.. hint::

    Other useful config options are: ``str_strip_whitespace``, ``validate_default``, ``frozen``

----

Exercise 8: Custom Validator
----------------------------

For even stricter quality checks, add a validator to ensure the penguin body mass is realistic (between 100g and 20kg):

.. code-block:: python

    from pydantic import field_validator

    class PredictionInput(BaseModel):
        ...

        @field_validator("body_mass")
        @classmethod
        def validate_body_mass(cls, v):
            if v < 100 or v > 20000:
                raise ValueError("body_mass must be between 500g and 20000g")
            return v

Test the validator:

.. code-block:: bash

    # Too light - should fail
    curl -X POST http://localhost:8000/predict \
         -H "Content-Type: application/json" \
         -d '{"body_mass": 10.0, "bill_length": 39.0}'

    # Too heavy - should fail
    curl -X POST http://localhost:8000/predict \
         -H "Content-Type: application/json" \
         -d '{"body_mass": 50000.0, "bill_length": 39.0}'

Add a validator for ``bill_length`` (realistic range: 10-60mm).


Exercise 9: Field Constraints and Annotated
-------------------------------------------

Pydantic offers two ways to add constraints without writing custom validators:

**Using Field():**

.. code-block:: python

    from pydantic import Field

    class PredictionInput(BaseModel):
        body_mass: float = Field(ge=100, le=20000, description="Body mass in grams")
        bill_length: float = Field(ge=30, le=60, description="Bill length in mm")

**Using Annotated:**

.. code-block:: python

    from typing import Annotated
    from pydantic import Field

    BodyMass = Annotated[float, Field(ge=100, le=20000, description="Body mass in grams")]

    class PredictionInput(BaseModel):
        body_mass: BodyMass
        ...

The ``Annotated`` approach lets you reuse type definitions across multiple models.

**Your task:** Refactor your model to use ``Field`` constraints.
Check the ``/docs`` page to see how the descriptions appear in the API documentation.

----

Reflection Questions
--------------------

- What advantages does ``pydantic`` request and return types offer?
- When does Pydantic validation run - before or after your endpoint code?
- How do Field descriptions improve your API documentation?
- When would your prefer a validator function over a ``Field`` or ``Annotated``?

.. seealso::

   - Pydantic documentation: https://docs.pydantic.dev/
   - FastAPI request body: https://fastapi.tiangolo.com/tutorial/body/
   - Pydantic validators: https://docs.pydantic.dev/latest/concepts/validators/
