
Authentication
==============

.. topic:: Goal

   In this chapter, you will secure your API using JSON Web Tokens (JWT)
   and learn how to integrate authentication with FastAPI.


Key Concepts
------------

Before implementing authentication, it helps to understand these terms:

- **OAuth2**: A protocol for authorization that allows third-party access without sharing passwords
- **HTTPS**: Encrypted HTTP connection that protects data in transit
- **JWT**: JSON Web Token, a compact way to transmit claims between parties
- **Session ID**: A server-side identifier stored in cookies to track user sessions

.. mermaid::

   sequenceDiagram
       participant Client
       participant API
       participant AuthServer

       Client->>AuthServer: Login (username/password)
       AuthServer->>Client: JWT Token
       Client->>API: Request + JWT Token
       API->>API: Verify Token
       API->>Client: Protected Resource

For more details, see the `OAuth2 specification <https://oauth.net/2/>`_
and `JWT introduction <https://jwt.io/introduction>`_.


Exercise 1: Create and Decode a JWT
-----------------------------------

Install the PyJWT library:

.. code-block:: bash

   uv add pyjwt

Create a simple JWT token:

.. code-block:: python

   import jwt

   payload = {"user_id": 42, "username": "alice"}
   secret = "your-secret-key"

   token = jwt.encode(payload=payload, key=secret, algorithm="HS256")
   print(token)

Copy the token and paste it at `jwt.io <https://jwt.io>`_ to decode and inspect its contents.

Decode the token in Python:

.. code-block:: python

   decoded = jwt.decode(token, key=secret, algorithms=["HS256"])
   print(decoded)


Exercise 2: Sign JWT with RSA
-----------------------------

RSA provides asymmetric encryption: sign with a private key, verify with a public key.

Generate an RSA key pair:

.. code-block:: bash

   ssh-keygen -t rsa -b 2048 -f rsa.key -N ""

Install PyJWT with cryptography support:

.. code-block:: bash

   uv add "pyjwt[crypto]"

Sign a token with the private key:

.. code-block:: python

   import jwt
   from cryptography.hazmat.primitives import serialization

   # Load the private key
   with open("rsa.key", "r") as f:
       private_key_data = f.read()

   private_key = serialization.load_ssh_private_key(
       private_key_data.encode(),
       password=None
   )

   # Create and sign the token
   payload = {"user_id": 42, "username": "alice"}
   token = jwt.encode(payload=payload, key=private_key, algorithm="RS256")
   print(token)

Verify the token with the public key:

.. code-block:: python

   # Load the public key
   with open("rsa.key.pub", "r") as f:
       public_key_data = f.read()

   public_key = serialization.load_ssh_public_key(public_key_data.encode())

   # Verify and decode
   decoded = jwt.decode(token, key=public_key, algorithms=["RS256"])
   print(decoded)


Exercise 3: Protect an Endpoint with Depends
--------------------------------------------

FastAPI uses dependency injection to handle authentication.
Create a dependency that validates the JWT token.

.. code-block:: python

   from fastapi import FastAPI, Depends, HTTPException, status
   from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
   import jwt

   app = FastAPI()
   security = HTTPBearer()

   SECRET_KEY = "your-secret-key"

   def get_current_user(
       credentials: HTTPAuthorizationCredentials = Depends(security)
   ):
       token = credentials.credentials
       try:
           payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
           return payload
       except jwt.InvalidTokenError:
           raise HTTPException(
               status_code=status.HTTP_401_UNAUTHORIZED,
               detail="Invalid token",
           )

   @app.get("/protected")
   def protected_route(user: dict = Depends(get_current_user)):
       return {"message": f"Hello, {user['username']}!"}

Test the endpoint:

1. Generate a token using the code from Exercise 1
2. Send a request with the Authorization header:

.. code-block:: bash

   curl -H "Authorization: Bearer <your-token>" http://localhost:8000/protected


Reflection Questions
--------------------

- When would you use symmetric (HS256) vs asymmetric (RS256) signing?
- What claims should a JWT contain for your application?
- How would you handle token expiration?
