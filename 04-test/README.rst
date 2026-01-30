
Testing
=======

.. topic:: Goal

   Run automated tests of a REST API.

Automated tests help you verify that your API works correctly
and continues to work as you make changes.
In this chapter, you will learn how to use static analysis tools
and write tests for FastAPI endpoints.

----

Exercise 1: Static Checks
-------------------------

Static analysis tools check your code without running it.
Install three essential tools:

.. code-block:: bash

    uv add --dev ty black ruff

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

----

Exercise 2: Create a Test
-------------------------

FastAPI provides a ``TestClient`` for testing endpoints without starting a server.
Create a file ``tests/test_api.py``:

.. code-block:: python

    from fastapi.testclient import TestClient
    from app import app

    client = TestClient(app)


    def test_root():
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"Hello": "World"}

Install pytest and run the test:

.. code-block:: bash

    uv add --dev pytest
    uv run pytest

You should see the test pass. Try changing the expected response to see a failing test.

----

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

**Your task:** Write tests that verify:

1. The endpoint returns a 422 error for invalid input (missing required fields)
2. The endpoint returns a 422 error for out-of-range values (if you added validators)

----

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
    def valid_penguin_data():
        return {
            "body_mass": 4200.0,
            "beak_length": 39.0,
            "flipper_length": 195.0,
            "island": "Biscoe"
        }


    @pytest.fixture
    def invalid_penguin_data():
        return {
            "body_mass": "not a number",
            "beak_length": 39.0
        }

Now use fixtures in your tests:

.. code-block:: python

    def test_predict_with_valid_data(client, valid_penguin_data):
        response = client.post("/predict", json=valid_penguin_data)
        assert response.status_code == 200


    def test_predict_with_invalid_data(client, invalid_penguin_data):
        response = client.post("/predict", json=invalid_penguin_data)
        assert response.status_code == 422

----

Exercise 5: Refactor for Testability
------------------------------------

Extract business logic into a separate function that can be tested without FastAPI.
Create a ``predict.py`` module:

.. code-block:: python

    def predict_species(body_mass: float, beak_length: float) -> str:
        """Predict penguin species based on measurements."""
        if body_mass > 4500 and beak_length > 45:
            return "Gentoo"
        elif beak_length < 40:
            return "Adelie"
        else:
            return "Chinstrap"

Now you can test the prediction logic directly:

.. code-block:: python

    from predict import predict_species


    def test_predict_gentoo():
        result = predict_species(body_mass=5000.0, beak_length=50.0)
        assert result == "Gentoo"


    def test_predict_adelie():
        result = predict_species(body_mass=3500.0, beak_length=35.0)
        assert result == "Adelie"

This approach makes unit tests faster and easier to write.

----

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


    def test_endpoint_with_mocked_prediction(client, valid_penguin_data):
        with patch("app.predict_species", return_value="Gentoo"):
            response = client.post("/predict", json=valid_penguin_data)
            assert response.status_code == 200
            assert response.json()["species"] == "Gentoo"

You can also use the ``mocker`` fixture from pytest-mock:

.. code-block:: python

    def test_with_mocker(client, valid_penguin_data, mocker):
        mocker.patch("app.predict_species", return_value="Chinstrap")
        response = client.post("/predict", json=valid_penguin_data)
        assert response.json()["species"] == "Chinstrap"

**Your task:** Mock a prediction to always return ``"Adelie"`` and verify the response.

----

Reflection Questions
--------------------

1. **Test coverage**: How do you know if you have enough tests?

2. **Test speed**: Why is it useful to have tests that don't require HTTP requests?

3. **Mocking**: When should you mock, and when should you test the real implementation?

.. seealso::

   - FastAPI testing: https://fastapi.tiangolo.com/tutorial/testing/
   - pytest documentation: https://docs.pytest.org/
   - pytest-mock: https://pytest-mock.readthedocs.io/
