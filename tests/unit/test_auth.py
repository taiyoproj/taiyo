"""Tests for authentication methods."""

import httpx
from taiyo import BasicAuth, BearerAuth


def test_basic_auth():
    """Test Basic authentication."""
    client = httpx.AsyncClient()
    auth = BasicAuth("user", "pass")
    auth.apply(client)

    auth_header = client.headers["Authorization"]
    assert auth_header.startswith("Basic ")
    # Check that it's base64 encoded "user:pass"
    assert auth_header == "Basic dXNlcjpwYXNz"


def test_bearer_auth():
    """Test Bearer token authentication."""
    client = httpx.AsyncClient()
    auth = BearerAuth("test-token")
    auth.apply(client)

    assert client.headers["Authorization"] == "Bearer test-token"
