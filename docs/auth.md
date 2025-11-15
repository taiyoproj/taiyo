# Authentication

Taiyo supports pluggable authentication by passing an auth object to the client. Two strategies are built in:

- `BasicAuth(username, password)` — HTTP Basic auth
- `BearerAuth(token)` — JWT or opaque bearer token

Auth objects simply set the `Authorization` header on the underlying `httpx` client when the client is constructed.

## Basic auth

```python
from taiyo import SolrClient, BasicAuth

auth = BasicAuth("admin", "secret")
with SolrClient("http://localhost:8983/solr", "products", auth=auth) as client:
    print(client.ping())
```

## Bearer token

```python
from taiyo import AsyncSolrClient, BearerAuth

auth = BearerAuth("your-jwt-or-token")
async def main():
    async with AsyncSolrClient("http://localhost:8983/solr", "products", auth=auth) as client:
        print(await client.ping())
```

## Custom auth

To implement your own auth scheme, subclass `SolrAuth` (from `taiyo.client.auth`) and implement `apply(client)` which receives the constructed `httpx.Client`/`AsyncClient`.

```python
from taiyo.client.auth import SolrAuth

class ApiKeyAuth(SolrAuth):
    def __init__(self, key: str):
        self.key = key
    def apply(self, client):
        client.headers["X-API-Key"] = self.key
```

Then pass `auth=ApiKeyAuth("...")` to the client constructor.
