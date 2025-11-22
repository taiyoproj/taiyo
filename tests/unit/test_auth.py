"""Tests for authentication methods."""

import httpx
from taiyo import BasicAuth, BearerAuth


def test_basic_auth():
    """Test Basic authentication."""

    class MockClient:
        def __init__(self):
            self._client = httpx.Client()

        def set_header(self, key, value):
            self._client.headers[key] = value

    client = MockClient()
    auth = BasicAuth("user", "pass")
    auth.apply(client)
    assert "Authorization" in client._client.headers
    assert client._client.headers["Authorization"].startswith("Basic ")
    # Check that it's base64 encoded "user:pass"
    assert client._client.headers["Authorization"] == "Basic dXNlcjpwYXNz"
    client._client.close()


def test_bearer_auth():
    """Test Bearer token authentication."""

    class MockClient:
        def __init__(self):
            self._client = httpx.Client()

        def set_header(self, key, value):
            self._client.headers[key] = value

    client = MockClient()
    auth = BearerAuth("test-token")
    auth.apply(client)

    assert client._client.headers["Authorization"] == "Bearer test-token"
    client._client.close()
