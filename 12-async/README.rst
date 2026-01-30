
Async Requests
==============

.. topic:: Goal

   Compare the performance of synchronous vs asynchronous endpoints
   and learn when to use each approach.


Sync vs Async
-------------

FastAPI supports both synchronous and asynchronous endpoints:

- **Synchronous** (``def``): Blocks the worker while waiting for I/O
- **Asynchronous** (``async def``): Releases the worker during I/O, allowing concurrent requests

Use ``async`` for I/O-bound tasks (network calls, database queries, file operations).
Use regular ``def`` for CPU-bound tasks or when calling synchronous libraries.

.. literalinclude:: app.py
   :language: python


Exercise 1: Compare Performance
-------------------------------

Start the server:

.. code-block:: bash

   uv run fastapi dev 12-async/app.py

Test a single synchronous request:

.. code-block:: bash

   curl http://localhost:8000/wait?secs=2

Now send many concurrent requests using the test script:

.. code-block:: bash

   time uv run 12-async/send_many.py

Observe the total time. Then modify ``send_many.py`` to call ``/wait_async`` instead
and run it again. Compare the results.


Exercise 2: Test an Async Endpoint
----------------------------------

Write a test for the async endpoint using ``pytest`` and ``httpx``:

.. code-block:: python

   import pytest
   from httpx import AsyncClient, ASGITransport
   from app import app

   @pytest.mark.asyncio
   async def test_wait_async():
       transport = ASGITransport(app=app)
       async with AsyncClient(transport=transport, base_url="http://test") as client:
           response = await client.get("/wait_async?secs=1")
           assert response.status_code == 200
           assert response.json()["status"] == "ready"

Install the required packages:

.. code-block:: bash

   uv add pytest-asyncio httpx


Background Workers
------------------

For long-running tasks that exceed typical request timeouts, consider background workers:

- **Celery**: Distributed task queue with Redis or RabbitMQ as broker
- **ARQ**: Lightweight async task queue built on Redis
- **Dramatiq**: Simple alternative to Celery with fewer dependencies

These allow you to return immediately to the client and process tasks asynchronously.


Handling Large Payloads
-----------------------

When your API needs to handle large data transfers:

- **Streaming responses**: Use ``StreamingResponse`` to send data in chunks
- **File uploads**: Use ``UploadFile`` with chunked reading for large files
- **Pagination**: Split large result sets into pages
- **Compression**: Enable gzip compression for JSON/CSV responses
- **Background processing**: Accept the upload, return a job ID, process asynchronously


Reflection Questions
--------------------

- When would blocking ``time.sleep()`` be a problem in production?
- How would you handle a mix of CPU-heavy and I/O-heavy operations?
- What happens if an async endpoint calls a blocking function?

.. seealso::

   `FastAPI Async Documentation <https://fastapi.tiangolo.com/async/>`_
