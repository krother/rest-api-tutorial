


Course Contents
Day 1: Fundamentals
On this day, participants will build an end-to-end REST API microservice on top of a small Machine Learning model. They will learn about how to set up multiple endpoints with FastAPI and validate input data using the pydantic library. An extra authentication layer introduces the concept of dependency injection. Finally, they will test their API service using automated tests and code checkers.


Day 2: Data Access and Storage
On this day, participants extend the data layer of their application by adding endpoints and schemas for creating, uploading and reading datasets. They connect a database and structure the code following best practices for modularized code and documentation.

Module 2.1: Data-centric APIs

- nesting and inheriting models
- get / put / update / delete endpoints
- requesting paginated data
- filtering
- JSON payloads, form and file uploads
- performance considerations

Module 2.2: Database connections

- object serialization with JSON
- serialization to SQL
- migrating databases and models
- the Repository pattern
- Object-Relational Mappers (ORM)
      
Module 2.3: Structuring an API

- creating a clean project structure
- separating API, service, and data layers
- the BCE Design Pattern
- grouping routes in a module
- testing a larger Python package

Day 3: Structuring Scalable APIs
During the third day, participants will build an API for a ML/AI task that scales to higher data workloads and model pipelines. They delegate longer tasks to worker processes. They expose and expose ML models through clear and consistent, testable endpoints. Typical issues with maintaining APIs and models are adressed.

Module 3.1: Serving Machine Learning Models

- load and cache a model
- organizing pre- and postprocessing steps
- switching between multiple backends
- configuration with pydantic-settings


Nikita:
- streaming requests and responses
- connecting to a secondary, external API

     

Module 3.3: Health checks / monitoring

CHECKLIST: data types, points to consider
CHECKLIST: CRUD points to consider
CHECKLIST: how are ids generated?

Material for group discussion

- health-check endpoints
- retries and timeouts
- checking job status via request IDs
- request and display monitoring data
- batch uploads

Module 3.4: Best Practices

SHOW an OpenAPI schema file

- OpenAPI documentation
- integration vs. unit tests
- automatic schema generation
- schema evolution
- API versioning
- rate limiting and request throttling (slowapi)
- performance tuning (threadpool vs async)
