
Error Handling and Logging
==========================

.. topic:: Goal

   In this chapter, you will catch and log errors that the API generates.


Exercise 1: Create an exception handler
---------------------------------------

FastAPI allows you to define custom exception handlers that intercept errors
and return appropriate responses. Add the following code to your ``app.py``:

.. code-block:: python

   from fastapi import Request
   from fastapi.responses import JSONResponse

   @app.exception_handler(IndexError)
   def db_error_handler(request: Request, exc: IndexError):
       print("log message", str(exc))
       return JSONResponse(
           status_code=422,
           content={
               "message": "an error occurred but I'm not telling you which one. Sorry."
           },
       )

Test the handler by creating an endpoint that raises an ``IndexError``.


Exercise 2: Refactor into separate files
----------------------------------------

Move the exception handler into a separate module to keep your code organized.

Create a new file ``handlers.py``:

.. code-block:: python

   from fastapi import Request
   from fastapi.responses import JSONResponse

   def db_error_handler(request: Request, exc: IndexError):
       print("log message", str(exc))
       return JSONResponse(
           status_code=422,
           content={"message": "an error occurred"},
       )

In your ``app.py``, import and register the handler:

.. code-block:: python

   from fastapi import FastAPI
   from handlers import db_error_handler

   app = FastAPI()
   app.add_exception_handler(IndexError, db_error_handler)


Exercise 3: Custom Exceptions
-----------------------------

Define a custom exception class and write an exception handler for it.

Create a custom exception in ``exceptions.py``:

.. code-block:: python

   class PredictionError(Exception):
       def __init__(self, message: str):
           self.message = message

Register a handler for it in ``app.py``:

.. code-block:: python

   from exceptions import PredictionError

   @app.exception_handler(PredictionError)
   def prediction_error_handler(request: Request, exc: PredictionError):
       return JSONResponse(
           status_code=400,
           content={"message": exc.message},
       )


Exercise 4: Create a logger
---------------------------

Use Python's standard ``logging`` module to log messages when predictions are made.

Add logging to your endpoint:

.. code-block:: python

   import logging

   logging.basicConfig(level=logging.INFO)
   logger = logging.getLogger(__name__)

   @app.post("/predict")
   def predict(data: InputData):
       logger.info(f"Prediction requested for: {data}")
       result = make_prediction(data)
       logger.info(f"Prediction result: {result}")
       return {"prediction": result}


Exercise 5: Measure Latency
---------------------------

Use ``time.time()`` to calculate and log the runtime of each API call.

.. code-block:: python

   import time
   import logging

   logger = logging.getLogger(__name__)

   @app.post("/predict")
   def predict(data: InputData):
       start_time = time.time()

       result = make_prediction(data)

       elapsed = time.time() - start_time
       logger.info(f"Prediction completed in {elapsed:.3f} seconds")
       return {"prediction": result}


Exercise 6: Configuration
-------------------------

Control the log level through an environment variable using a ``.env`` file.

First, install the ``python-dotenv`` package:

.. code-block:: bash

   uv add python-dotenv

Create a ``.env`` file in your project root:

.. code-block:: text

   LOG_LEVEL=INFO

Load the configuration in your ``app.py``:

.. code-block:: python

   import os
   import logging
   from dotenv import load_dotenv

   load_dotenv()

   log_level = os.getenv("LOG_LEVEL", "INFO")
   logging.basicConfig(level=getattr(logging, log_level))


Reflection Questions
--------------------

- Can you log too much?
- What information should you avoid logging (e.g., passwords, personal data)?
- How would you handle logging in a production environment?
