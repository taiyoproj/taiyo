"""Authentication module for Taiyo Solr client."""

import base64
from typing import Optional, Any
from .base import BaseSolrClient
from pydantic import SecretStr
import httpx


class SolrAuth:
    """Base class for Solr authentication methods."""

    def apply(self, client: BaseSolrClient[Any]) -> None:
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
        username: Username for authentication (str or SecretStr)
        password: Password for authentication (str or SecretStr)

    Example:
        ```python
        auth = BasicAuth("admin", "secret")
        client = SolrClient("http://localhost:8983/solr", "my_collection", auth=auth)
        ```
    """

    def __init__(self, username: str | SecretStr, password: str | SecretStr):
        self.username = (
            username if isinstance(username, SecretStr) else SecretStr(username)
        )
        self.password = (
            password if isinstance(password, SecretStr) else SecretStr(password)
        )

    def apply(self, client: BaseSolrClient[Any]) -> None:
        username = self.username.get_secret_value()
        password = self.password.get_secret_value()
        auth_str = base64.b64encode(f"{username}:{password}".encode()).decode()
        client.set_header("Authorization", f"Basic {auth_str}")


class BearerAuth(SolrAuth):
    """
    Bearer token authentication.
    https://solr.apache.org/guide/solr/latest/deployment-guide/jwt-authentication-plugin.html

    Args:
        token: JWT token to use (str or SecretStr)

    Example:
        ```python
        auth = BearerAuth("my-token")
        client = SolrClient("http://localhost:8983/solr", "my_collection", auth=auth)
        ```
    """

    def __init__(self, token: str | SecretStr):
        self.token = token if isinstance(token, SecretStr) else SecretStr(token)

    def apply(self, client: BaseSolrClient[Any]) -> None:
        client.set_header("Authorization", f"Bearer {self.token.get_secret_value()}")


class OAuth2Auth(SolrAuth):
    """
    OAuth 2.0 authentication with token refresh.

    Args:
        client_id: OAuth client ID (str or SecretStr)
        client_secret: OAuth client secret (str or SecretStr)
        token_url: Token endpoint URL

    Example:
        ```python
        auth = OAuth2Auth(
            client_id="your-client-id",
            client_secret="your-client-secret",
            token_url="https://auth.example.com/token"
        )
        client = SolrClient("http://localhost:8983/solr", auth=auth)
        ```
    """

    def __init__(
        self, client_id: str | SecretStr, client_secret: str | SecretStr, token_url: str
    ):
        self.client_id = (
            client_id if isinstance(client_id, SecretStr) else SecretStr(client_id)
        )
        self.client_secret = (
            client_secret
            if isinstance(client_secret, SecretStr)
            else SecretStr(client_secret)
        )
        self.token_url = token_url
        self.access_token: Optional[str] = None

    def get_access_token(self) -> str:
        """
        Fetch access token from OAuth2 server.

        Returns:
            Access token string

        Raises:
            httpx.HTTPStatusError: If token request fails
        """
        response = httpx.post(
            self.token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id.get_secret_value(),
                "client_secret": self.client_secret.get_secret_value(),
            },
        )
        response.raise_for_status()
        token: str = response.json()["access_token"]
        return token

    def apply(self, client: BaseSolrClient[Any]) -> None:
        if not self.access_token:
            self.access_token = self.get_access_token()
        client.set_header("Authorization", f"Bearer {self.access_token}")
