

async
=====

.. literalinclude app.py

from https://fastapi.tiangolo.com/#example

2. run

    uv run fastapi run 03-async/app.py

3. request

curl http://localhost:8000/wait?secs=5

4. many requests

run the `send_many` program.

    time uv run send_many.py

compare by sending requests to the wait_async endpoint instead.

find examples for CPU-heavy vs I/O-heavy tasks

.. seealso::

    FastAPI 

