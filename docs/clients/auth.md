# Authentication

Taiyo supports Apache Solr's authentication mechanisms. Use Basic Authentication, Bearer Token authentication, or OAuth2 to secure your Solr connection. 

!!! note Handling credentials
    Taiyo uses `pydantic.SecretStr` for secure handling of credentials and raw strings are converted to `SecretStr`. 
    See: https://docs.pydantic.dev/2.2/usage/types/secrets/ for details.

## Authentication Methods

### Basic Authentication

Basic Authentication uses username and password credentials encoded in HTTP headers.

**Solr Documentation**: [Basic Authentication Plugin](https://solr.apache.org/guide/solr/latest/deployment-guide/basic-authentication-plugin.html)

#### Usage

```python
from taiyo import SolrClient, BasicAuth

auth = BasicAuth(username=SecretStr("admin"), password="secret_password")

client = SolrClient(
    "http://localhost:8983/solr",
    auth=auth
)
```

### Bearer Token Authentication

Bearer Token authentication uses JWT (JSON Web Tokens) for authentication.

**Solr Documentation**: [JWT Authentication Plugin](https://solr.apache.org/guide/solr/latest/deployment-guide/jwt-authentication-plugin.html)

#### Usage

```python
from taiyo import SolrClient, BearerAuth

auth = BearerAuth(token="your-jwt-token-here")

client = SolrClient(
    "http://localhost:8983/solr",
    auth=auth
)
```

#### Secure Token Storage

```python
from pydantic import SecretStr
from taiyo import BearerAuth

auth = BearerAuth(token=SecretStr("your-jwt-token-here"))
```

### OAuth2 Authentication

OAuth2 authentication with automatic token management using client credentials flow.

#### Usage

```python
from taiyo import SolrClient, OAuth2Auth
from pydantic import SecretStr

auth = OAuth2Auth(
    client_id=SecretStr("your-client-id"),
    client_secret=SecretStr("your-client-secret"),
    token_url="https://auth.example.com/token"
)

client = SolrClient(
    "http://localhost:8983/solr",
    auth=auth
)
```

#### With Async Client

```python
from taiyo import AsyncSolrClient, OAuth2Auth
from pydantic import SecretStr

auth = OAuth2Auth(
    client_id=SecretStr("your-client-id"),
    client_secret=SecretStr("your-client-secret"),
    token_url="https://auth.example.com/token"
)

async with AsyncSolrClient("http://localhost:8983/solr", auth=auth) as client:
    results = await client.search("*:*")
```

#### Token Management

The OAuth2Auth class automatically fetches and manages access tokens:

```python
from taiyo import SolrClient
from taiyo.client.auth import OAuth2Auth
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

## Configuration Examples

### Environment Variables

Load credentials from environment variables:

```python
import os
from taiyo import SolrClient, BasicAuth

auth = BasicAuth(
    username=os.environ["SOLR_USERNAME"],
    password=os.environ["SOLR_PASSWORD"]
)

client = SolrClient(
    os.environ["SOLR_URL"],
    auth=auth
)
```

### Configuration File

Load from a configuration file:

```python
import json
from taiyo import SolrClient, BasicAuth

with open("config.json") as f:
    config = json.load(f)

auth = BasicAuth(
    username=config["solr"]["username"],
    password=config["solr"]["password"]
)

client = SolrClient(config["solr"]["url"], auth=auth)
```

Example `config.json`:

```json
{
  "solr": {
    "url": "http://localhost:8983/solr",
    "username": "admin",
    "password": "secret"
  }
}
```

## Authentication with Different Solr Setups

### SolrCloud

```python
from taiyo import SolrClient, BasicAuth

# SolrCloud typically uses the same auth across all nodes
auth = BasicAuth(username="admin", password="password")

# Connect to any node in the cluster
client = SolrClient(
    "http://solr-node1:8983/solr",
    auth=auth
)
```

### Standalone Solr

```python
from taiyo import SolrClient, BasicAuth

auth = BasicAuth(username="admin", password="password")

client = SolrClient(
    "http://localhost:8983/solr",
    auth=auth
)
```

### Solr with Reverse Proxy

If Solr is behind a reverse proxy that handles authentication:

```python
from taiyo import SolrClient

# No auth needed if proxy handles it
client = SolrClient("http://proxy.example.com/solr")

# Or set custom headers required by the proxy
client = SolrClient("http://proxy.example.com/solr")
client.set_header("X-API-Key", "your-api-key")
```

## Custom Authentication

For custom authentication schemes, you can extend the `SolrAuth` base class:

```python
from taiyo.client.auth import SolrAuth

class APIKeyAuth(SolrAuth):
    """Custom API key authentication."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def apply(self, client):
        """Apply API key to client headers."""
        client.set_header("X-API-Key", self.api_key)

# Usage
auth = APIKeyAuth("my-secret-key")
client = SolrClient("http://localhost:8983/solr", auth=auth)
```

## Testing with Authentication

### Mocking Authentication

```python
from unittest.mock import Mock
from taiyo import SolrClient, BasicAuth

def test_with_auth():
    # Mock auth for testing
    mock_auth = Mock(spec=BasicAuth)
    
    client = SolrClient(
        "http://localhost:8983/solr",
        auth=mock_auth
    )
    
    # Test operations
    # ...
```

### Test Without Real Credentials

```python
import pytest
from taiyo import SolrClient, BasicAuth

@pytest.fixture
def test_client():
    """Create test client with test credentials."""
    auth = BasicAuth(username="test", password="test")
    return SolrClient("http://localhost:8983/solr", auth=auth)

def test_search(test_client):
    test_client.set_collection("test_collection")
    results = test_client.search("*:*")
    assert results.status == 0
```

## Troubleshooting

### Authentication Failed

```python
from taiyo import SolrError

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

### Certificate Verification Errors

```python
# Temporarily disable verification for debugging
client = SolrClient(
    "https://solr.example.com/solr",
    auth=BasicAuth(username="admin", password="pass"),
    verify=False  # Only for debugging!
)

# Or provide custom CA bundle
client = SolrClient(
    "https://solr.example.com/solr",
    auth=BasicAuth(username="admin", password="pass"),
    verify="/path/to/custom-ca-bundle.crt"
)
```

### Token Expiration

Handle JWT token expiration:

```python
from taiyo import SolrError, BearerAuth
import time

class RefreshableBearerAuth(BearerAuth):
    """Bearer auth with automatic token refresh."""
    
    def __init__(self, token_provider):
        self.token_provider = token_provider
        self._token = None
        self._expiry = 0
    
    @property
    def token(self):
        if time.time() >= self._expiry:
            self._token = self.token_provider()
            self._expiry = time.time() + 3600  # 1 hour
        return self._token

def get_fresh_token():
    """Fetch a fresh JWT token."""
    # Your token fetching logic
    return "fresh-token"

auth = RefreshableBearerAuth(get_fresh_token)
client = SolrClient("https://solr.example.com/solr", auth=auth)
```

## Examples

### Complete Production Setup

```python
import os
from taiyo import SolrClient, BasicAuth
from pydantic import SecretStr
import logging

logger = logging.getLogger(__name__)

def create_production_client():
    """Create a production Solr client with proper auth and error handling."""
    
    # Load credentials securely
    username = os.environ.get("SOLR_USERNAME")
    password = os.environ.get("SOLR_PASSWORD")
    url = os.environ.get("SOLR_URL")
    
    if not all([username, password, url]):
        raise ValueError("Missing required environment variables")
    
    # Create authentication
    auth = BasicAuth(
        username=SecretStr(username),
        password=SecretStr(password)
    )
    
    # Create client with production settings
    client = SolrClient(
        base_url=url,
        auth=auth,
        timeout=60.0,
        verify=True,
        http2=True
    )
    
    # Test connection
    if not client.ping():
        logger.error("Failed to connect to Solr")
        raise ConnectionError("Cannot reach Solr server")
    
    logger.info("Successfully connected to Solr")
    return client

# Usage
try:
    with create_production_client() as client:
        client.set_collection("production_collection")
        results = client.search("*:*")
except Exception as e:
    logger.error(f"Error accessing Solr: {e}")
    raise
```

## Next Steps

- Learn about [Clients](clients.md) for more client configuration options
- Explore [Data Models](models.md) for type-safe document handling
- See [Query Parsers](parsers/query-parsers.md) for advanced search capabilities
