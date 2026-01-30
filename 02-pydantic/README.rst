

1. create environment

    python -m pip install uv

2. install dependencies

    uv sync

3. create hello world

.. literalinclude app.py

from https://fastapi.tiangolo.com/#example

4. run

    uv run fastapi run 02-pydantic/app.py

go to http://localhost:8000/

and http://localhost:8000/docs

5. Try:

- edit the request and leave away the quantity
- leave away the name
- send the request to a different endpoint instead
- send a GET request instead
- cause a runtime bug inside the python function

6. send request via curl

.. code::

   curl -X 'POST' \
     'http://localhost:8000/order/' \
     -H 'accept: application/json' \
     -H 'Content-Type: application/json' \
     -d '{
     "name": "cat",
     "quantity": 7
   }'

7. send request with postman

install postman.

send a POST request to the /order/ endpoint. Set the **Body** of the request, using the **raw JSON** type:

{
    "name": "cat",
    "quantity": 7
}

.. seealso::

    FastAPI 

