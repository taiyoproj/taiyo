"""Authentication module for Taiyo Solr client."""

import base64
import httpx


class SolrAuth:
    """Base class for Solr authentication methods."""

    def apply(self, client: httpx.AsyncClient) -> None:
        """
        Apply authentication to the client.

        Args:
            client: The httpx.AsyncClient instance to apply authentication to
        """
        raise NotImplementedError


class BasicAuth(SolrAuth):
    """
    Basic HTTP authentication.
    https://solr.apache.org/guide/solr/latest/deployment-guide/basic-authentication-plugin.html

    Args:
        username: Username for authentication
        password: Password for authentication

    Example:
        ```python
        auth = BasicAuth("admin", "secret")
        client = SolrClient("http://localhost:8983/solr", "my_collection", auth=auth)
        ```
    """

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    def apply(self, client: httpx.AsyncClient) -> None:
        auth_str = base64.b64encode(
            f"{self.username}:{self.password}".encode()
        ).decode()
        client.headers["Authorization"] = f"Basic {auth_str}"


class BearerAuth(SolrAuth):
    """
    Bearer token authentication.
    https://solr.apache.org/guide/solr/latest/deployment-guide/jwt-authentication-plugin.html

    Args:
        token: JWT token to use

    Example:
        ```python
        auth = BearerAuth("my-token")
        client = SolrClient("http://localhost:8983/solr", "my_collection", auth=auth)
        ```
    """

    def __init__(self, token: str):
        self.token = token

    def apply(self, client: httpx.AsyncClient) -> None:
        client.headers["Authorization"] = f"Bearer {self.token}"
