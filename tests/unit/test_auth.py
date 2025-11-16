"""Tests for authentication methods."""

from taiyo import BasicAuth, BearerAuth


def test_basic_auth():
    """Test Basic authentication."""

    class MockClient:
        def __init__(self):
            self.headers = {}

        def set_header(self, key, value):
            self.headers[key] = value

    client = MockClient()
    auth = BasicAuth("user", "pass")
    auth.apply(client)
    assert "Authorization" in client.headers
    assert client.headers["Authorization"].startswith("Basic ")
    # Check that it's base64 encoded "user:pass"
    assert client.headers["Authorization"] == "Basic dXNlcjpwYXNz"


def test_bearer_auth():
    """Test Bearer token authentication."""

    class MockClient:
        def __init__(self):
            self.headers = {}

        def set_header(self, key, value):
            self.headers[key] = value

    client = MockClient()
    auth = BearerAuth("test-token")
    auth.apply(client)

    assert client.headers["Authorization"] == "Bearer test-token"
