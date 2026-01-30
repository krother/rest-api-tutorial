


Course Contents
Day 1: Fundamentals
On this day, participants will build an end-to-end REST API microservice on top of a small Machine Learning model. They will learn about how to set up multiple endpoints with FastAPI and validate input data using the pydantic library. An extra authentication layer introduces the concept of dependency injection. Finally, they will test their API service using automated tests and code checkers.



Module 1.2: Pydantic models

- BaseModel
- optional and default fields
- Fields and Annotated fields
- nested objects
- custom Validators
- configuration using Meta classes
      
Module 1.3: Authentication

- authentication with web tokens
- the OAuth2 protocol
- creating and serving JWT tokens
- traffic encryption
- authentication with dependency injection 
- running a proxy server

   - HTTPS
   - set session id
   - OAuth
   - set cookies
   
Module 1.4: Testing

- checking type annotations
- running automated tests with pytest
- testing request and response models
- test fixtures and mocks
- maintaining test data



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

Module 2.4: Error handling and logging

- basic error handling
- custom exception responses
- logging latency
- using structlog for tracking metadata
- writing a custom error handler

Day 3: Structuring Scalable APIs
During the third day, participants will build an API for a ML/AI task that scales to higher data workloads and model pipelines. They delegate longer tasks to worker processes. They expose and expose ML models through clear and consistent, testable endpoints. Typical issues with maintaining APIs and models are adressed.

Module 3.1: Serving Machine Learning Models

- load and cache a model
- organizing pre- and postprocessing steps
- Mocking model / LLM calls for automated testing
- switching between multiple backends
- configuration with pydantic-settings

Module 3.2: async requests and worker processes

- concurrent requests with asyncio
- running background worker tasks
- handling large payloads (JSON, CSV, binary)
- streaming requests and responses
- testing asynchronous APIs
      
Module 3.3: Health checks / monitoring

- connecting to a secondary, external API
- health-check endpoints
- retries and timeouts
- checking job status via request IDs
- request and display monitoring data
- batch uploads

Module 3.4: Best Practices

- OpenAPI documentation
- integration vs. unit tests
- automatic schema generation
- schema evolution
- API versioning
- rate limiting and request throttling (slowapi)
- performance tuning (threadpool vs async)
