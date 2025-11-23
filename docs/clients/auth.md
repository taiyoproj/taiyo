# Authentication

Taiyo supports Apache Solr's authentication mechanisms. Use Basic Authentication, Bearer Token authentication, or OAuth2 to secure your Solr connection. 


!!! note "Handling Secrets"
    Taiyo uses `pydantic.SecretStr` for secure handling of credentials and raw strings are converted to `SecretStr`. 
    See: [https://docs.pydantic.dev/2.2/usage/types/secrets/](https://docs.pydantic.dev/2.2/usage/types/secrets/) for details.


## Authentication Methods

- Basic Auth uses username and password credentials encoded in HTTP headers.

- Bearer Token authentication uses JWT (JSON Web Tokens) for authentication.

- OAuth2 authentication with automatic token management using client credentials flow.

- You can also set a custom header value from `.set_header()` method which takes a string key-value pair.

=== "Basic Auth"

    ```python
    from taiyo import SolrClient, BasicAuth

    auth = BasicAuth(username=SecretStr("admin"), password="secret_password")

    client = SolrClient(
        "http://localhost:8983/solr",
        auth=auth
    )
    ```

=== "Bearer Token"

    ```python
    from taiyo import SolrClient, BearerAuth

    auth = BearerAuth(token="your-jwt-token-here")

    client = SolrClient(
        "http://localhost:8983/solr",
        auth=auth
    )
    ```

=== "OAuth2"

    ```python
    from taiyo import SolrClient, OAuth2Auth
    from pydantic import SecretStr

    auth = OAuth2Auth(
        client_id=SecretStr("client-id"),
        client_secret=SecretStr("client-secret"),
        token_url="https://auth.example.com/oauth/token"
    )

    # Token is fetched automatically on first request
    client = SolrClient("http://localhost:8983/solr", auth=auth)
    results = client.search("*:*")

    # Manually refresh token if needed
    auth.access_token = None
    auth.apply(client)
    ```

=== "Custom"

    ```python
    from taiyo import SolrClient

    client = SolrClient("http://proxy.example.com/solr")

    # Set custom headers required by the proxy server
    client = SolrClient("http://proxy.example.com/solr")
    client.set_header("X-API-Key", "your-api-key")
    ```

## Extending SolrAuth class

For custom authentication schemes, you can extend the `SolrAuth` base class:

```python
from taiyo.client.auth import SolrAuth

class APIKeyAuth(SolrAuth):
    """Custom API key authentication."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def apply(self, client):
        """Apply API key to client headers."""
        client.set_header("My-API-Key", self.api_key)

auth = APIKeyAuth("my-secret-key")
client = SolrClient("http://localhost:8983/solr", auth=auth)
```

### Error Handling

When a Taiyo client fails, it will raise a `SolrError` instance.

```python
from taiyo import SolrClient, SolrError

try:
    client = SolrClient(
        "http://localhost:8983/solr",
        auth=BasicAuth(username="admin", password="wrong")
    )
    client.ping()
except SolrError as e:
    if e.status_code == 401:
        print("Authentication failed - check credentials")
    elif e.status_code == 403:
        print("Forbidden - user doesn't have required permissions")
```

### SSL Configuration

Taiyo clients use `httpx.Client` and `httpx.AsyncClient`, and you can pass in any kwargs supported by httpx such as `verify` which defaults to `True`.

```python
# Temporarily disable verification for debugging
client = SolrClient(
    "https://solr.example.com/solr",
    auth=BasicAuth(username="admin", password="pass"),
    verify=False
)

# Or provide custom CA bundle
client = SolrClient(
    "https://solr.example.com/solr",
    auth=BasicAuth(username="admin", password="pass"),
    verify="/path/to/custom-ca-bundle.crt"
)
```

## Next Steps

- Learn about [Clients](clients.md) for more client configuration options
- Explore [Data Models](models.md) for type-safe document handling
- See [Query Parsers](parsers/query-parsers.md) for advanced search capabilities


## Solr References

- [Basic Authentication Plugin](https://solr.apache.org/guide/solr/latest/deployment-guide/basic-authentication-plugin.html)

- [JWT Authentication Plugin](https://solr.apache.org/guide/solr/latest/deployment-guide/jwt-authentication-plugin.html)