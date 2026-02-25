
Testing
=======

.. topic:: Goal

   Run automated tests of a REST API.

Automated tests help you verify that your API works correctly
and continues to work as you extend or refactor.
In this chapter, you use static analysis tools
and write unit tests for FastAPI endpoints.


Exercise 1: Static Checks
-------------------------

Static analysis tools check your code without running it.
Install three essential tools:

.. code-block:: bash

    uv add --dev ty black ruff

Inspect the ``pyproject.toml`` file and see what changed.

**ty** is a type checker that verifies your type hints are consistent:

.. code-block:: bash

    uv run ty check .

**black** formats your code to a consistent style:

.. code-block:: bash

    uv run black .

**ruff** is a fast linter that catches common bugs and style issues:

.. code-block:: bash

    uv run ruff check .

Run all three commands on your project and fix any issues they report.

Exercise 2: Create a Test
-------------------------

FastAPI provides a ``TestClient`` for testing endpoints without actually starting a server.
It is fully compatible with the ``pytest`` library.
Create a file ``tests/test_app.py``:

.. code-block:: python

    from fastapi.testclient import TestClient
    from app import app

    client = TestClient(app)


    def test_root():
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"Hello": "Mars"}

Install pytest and run the test:

.. code-block:: bash

    uv add --dev pytest
    uv run pytest

You should see the test fail. Try changing the expected response to see a passing test.

Exercise 3: Test POST Endpoints
-------------------------------

Test your prediction endpoint by sending a POST request with JSON data:

.. code-block:: python

    def test_predict_species():
        response = client.post(
            "/predict",
            json={"body_mass": 4200.0, "beak_length": 39.0}
        )
        assert response.status_code == 200
        data = response.json()
        assert "species" in data
        assert "probability" in data

Write additional tests that verify:

- The endpoint returns a 422 error for invalid input (missing required fields)
- The endpoint returns a 422 error for out-of-range values (if you added validators)

.. note::

   Should you test the actual probability values? Why or why not?


Exercise 4: Fixtures
--------------------

Fixtures provide reusable test data and setup code.
Create a file ``tests/conftest.py`` with shared fixtures:

.. code-block:: python

    import pytest
    from fastapi.testclient import TestClient
    from app import app


    @pytest.fixture
    def client():
        return TestClient(app)


    @pytest.fixture
    def valid_penguin():
        return {
            "body_mass": 4200.0,
            "bill_length": 39.0,
            "flipper_length": 195.0,
            "island": "Biscoe"
        }


    @pytest.fixture
    def invalid_penguin():
        return {
            "body_mass": "not a number",
            "bill_length": 39.0
        }

Now use fixtures in your tests:

.. code-block:: python

    def test_predict_with_valid_data(client, valid_penguin):
        response = client.post("/predict", json=valid_penguin)
        assert response.status_code == 200


    def test_predict_with_invalid_data(client, invalid_penguin):
        response = client.post("/predict", json=invalid_penguin)
        assert response.status_code == 422


Exercise 5: Refactor for Testability
------------------------------------

Extract business logic into a separate function that can be tested without FastAPI.
Create a ``predict.py`` module:

.. code-block:: python

   def predict_species(request: PenguinPredictionRequest) -> PredictionOutput:
       ...

Move all necessary codes and imports to ``predict.py``.
Now you can test the prediction logic directly:

.. code-block:: python

    from predict import predict_species

    def test_predict_gentoo():
        result = predict_species(PenguinPredictionRequest(body_mass=5000.0, bill_length=50.0))
        assert result.species == "Gentoo"

    def test_predict_adelie():
        ...
        # insert data that firmly results in a predicted "Adelie" penguin

This approach makes unit tests faster and easier to write.
Also, your code in ``app.py`` becomes leaner.


Exercise 6: Mocking
-------------------

Use mocking to replace dependencies during testing.
This is useful when your endpoint calls external services or databases.

Install pytest-mock:

.. code-block:: bash

    uv add --dev pytest-mock

Mock the prediction function to test the endpoint independently:

.. code-block:: python

    from unittest.mock import patch

    def test_endpoint_with_mocked_prediction(client, valid_penguin, valid_prediction):
        with patch("app.predict_species", return_value=valid_prediction):
            response = client.post("/penguins/predict", json=valid_penguin)
            assert response.status_code == 200
            assert response.json()["species"] == "Gentoo"

Add a **fixture** ``valid_prediction`` so that the test passes.

You can also use the ``mocker`` fixture from pytest-mock:

.. code-block:: python

    def test_with_mocker(client, valid_penguin, mocker):
        mocker.patch("app.predict_species", return_value="Gentoo")
        response = client.post("/penguins/predict", json=valid_penguin)
        ...


Exercise 7: Test Coverage
-------------------------

As a final check, analyze whether all code has been tested.
Install pytest-cov:

.. code-block:: bash

    uv add --dev pytest-cov

Then run:

.. code-block:: bash

    uv run pytest --cov

To find out which lines have been missed out, try:

.. code-block:: bash
 
   uv run coverage html

Open the file ``htmlcov/index.html`` in a browser.  


Reflection Questions
--------------------

- What information does a passing test give you?
- What information does a failing test give you?
- How much testing is enough?
- Why is it useful to have tests that don't require HTTP requests?
- Discuss the statement *"only mock what you own."*

.. seealso::

   - FastAPI testing: https://fastapi.tiangolo.com/tutorial/testing/
   - pytest documentation: https://docs.pytest.org/
   - pytest-mock: https://pytest-mock.readthedocs.io/
