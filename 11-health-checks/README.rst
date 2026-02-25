
Health Checks
=============

.. topic:: Goal

   Add health check endpoints to monitor your API's status.


Exercise 1: Basic Health Endpoint
---------------------------------

Add a simple health check that returns the service status:

.. code-block:: python

   @app.get("/health")
   def health():
       return {"status": "ok"}


Exercise 2: Check Dependencies
------------------------------

Verify that dependencies (database, external services) are reachable:

.. code-block:: python

   @app.get("/health/ready")
   def readiness():
       # Check database connection
       # Check external service availability
       return {"status": "ready", "database": "ok"}



Discussion
----------

- What should a health check verify?
- How often should health checks run?
- What happens when a health check fails?
