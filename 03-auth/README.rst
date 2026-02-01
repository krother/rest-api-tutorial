
Authentication
==============

.. topic:: Goal

   In this chapter, you will secure your API using JSON Web Tokens (JWT)
   and learn how to integrate authentication with FastAPI.


The OAuth2 Process
------------------

OAuth2 is an authorization protocol that allows access without sharing passwords.
It is based on a third location, the **Auth Server**, to produce a token.
That token is usually signed with a cryptographic algorithm.

An important assumption in OAuth2 is, that a **secure transfer of secrets** is possible between the Auth Server and the API server. This can be done long before any requests are done. An important question is which source of authentication your API is going to trust and for how long.

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

As a token, typically a **JWT** (JSON Web Token) is used. It consists of a **header** containing the algorithm used by the signature, a **payload** that typically consists of at least a user id, and a **signature** that is used for authentication.
When such a token is sent to a server as a HTTP request, it is also called a **Bearer Token**.

In practice, multiple variants of the OAuth2 process are used.
For instance, you could send the signed JWT with every HTTP request, or use it once to exchange a cryptographic key for secure traffic. In any case, encrypted **HTTPS** connections should be used. Typically, HTTPS is handled by a proxy server and not by FastAPI and we will ignore it here.


Exercise 1: Create and Decode a JWT
-----------------------------------

Install the PyJWT library with cryptography support:

.. code-block:: bash

   uv add "pyjwt[crypto]"

Create a simple JWT token:

.. code-block:: python

   import jwt

   payload = {"user_id": 42, "username": "ada"}
   secret = "..."

   token = jwt.encode(payload=payload, key=secret, algorithm="HS256")
   print(token)

Copy the token and paste it at `jwt.io <https://jwt.io>`_ to decode and inspect its contents.

Decode the token in Python:

.. code-block:: python

   decoded = jwt.decode(token, key=secret, algorithms=["HS256"])
   print(decoded)

.. warning::

   It is crucial to understand that the information carried by the JWT is not by itself encrypted.
   Any base64 decoder can access the payload without knowing the secret.
   However, the secret can be used to check the **signature** in the JWT.

Exercise 2: Sign JWT with RSA
-----------------------------

RSA provides asymmetric encryption: sign with a private key, verify with a public key.

Generate an RSA key pair:

.. code-block:: bash

   ssh-keygen -t rsa -b 2048 -f rsa.key -N ""

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
   payload = {"user_id": 42, "username": "ada"}
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


Exercise 3: Dependency Injection
--------------------------------

FastAPI uses **dependency injection** to handle authentication.
The dependency is resolved by FastAPI before the function is called.
In practice, this works very much like the `Decorator Pattern <https://refactoring.guru/design-patterns/decorator>`__ , only that syntactically it is riding piggyback on top of Python's type hint system.

In a first step, create a placeholder function that demonstrates the injection mechanism.
The ``door_check()`` function is passed as a callback function to FastAPI. It is like saying:
*"call this to get an authenticated username"*.

.. code-block:: python

   from fastapi import FastAPI, Depends

   app = FastAPI()

   def get_current_user():
      print("security here!")
      return "Ada"


   @app.get("/protected")
   def protected_route(user: str = Depends(get_current_user)):
      return {"message": f"Hello, {user}!"}


.. note::

   I am not a big fan of this design solution. In most other languages, you would define a class or interface, at the cost of a few more lines of code. I also understand that the authors of FastAPI did not use a Python decorator, because it is used heavily for HTTP routes. I appreciate the brevity of the ``Depends()`` notation, however using a syntax element for security that is clearly built for something else is at least worth a critical thought.


Exercise 4: Protect an Endpoint
-------------------------------

Now you can combine the approach with the JWT token you generated earlier.
Hereby you simulate setting up an auth server that produces JWT tokens.
Replace the ``get_current_user()`` function by the following:

.. code-block:: python

   from fastapi import FastAPI, Depends, HTTPException, status
   from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
   import jwt

   security = HTTPBearer()

   SECRET_KEY = "..."

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

.. note::

   The user returned to the endpoint is now a ``dict``, not a  ``str``.

Test the endpoint:

1. Generate a token using the code from Exercise 1
2. Send a request with the Authorization header:

.. code-block:: bash

   curl -H "Authorization: Bearer <your-token>" http://localhost:8000/protected

Exercise 5: RSA Tokens
----------------------

In case you do not want to set up a JWT server for OAuth2 in production, you might want to use a private/public key pair instead.
In that case, you would need to do the following:

1. Every client needs to generate their own key pair
2. The API server needs to store the **public key** of each client
3. The client creates a JWT and signs it using their **private key**
4. The client accesses an endpoint and sends along the JWT
5. The server verifies the signature using the public key.

Exercise 6: Middleware
----------------------

Create a `FastAPI Middleware <https://fastapi.tiangolo.com/tutorial/middleware/>`__ that validates a Bearer Token for **every request** so that you cannot accidentally expose a single endpoint by forgetting `Depends()`.

Reflection Questions
--------------------

- Who should know the secret used by the HS256 algorithm?
- When would you use symmetric (HS256) vs asymmetric (RS256) signing?
- What claims should a JWT contain for your application?
- How does JWT token expiration help make an application more secure?
- What information does an attacker get when they intercept a valid JWT?
- What information does an attacker get when they intercept an expired JWT?

.. seealso::

   - `OAuth2 Tutorial with Passwords in the FastAPI documentation <https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/>`__
   - `OAuth2 specification <https://oauth.net/2/>`__
   - `JWT introduction <https://jwt.io/introduction>`__
