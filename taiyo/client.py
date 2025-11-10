import httpx
from typing import Any, Dict, List, Optional, Union, Type
from urllib.parse import urljoin

from taiyo.parsers.base import BaseQueryParser
from .types import SolrDocument, SolrResponse, SolrError, DocumentT
from .auth import SolrAuth
from pydantic import ValidationError


class SolrClient:
    """
    Modern async client for Apache Solr.

    Args:
        base_url: Base URL of the Solr instance (e.g., "http://localhost:8983/solr")
        collection: Name of the Solr collection
        auth: Authentication method to use (optional)
        timeout: Request timeout in seconds
        **client_options: Additional options to pass to the httpx client

    Examples:
        ```python
        from taiyo import SolrClient
        from taiyo.auth import BasicAuth, BearerAuth

        # Basic authentication
        client = SolrClient(
            "http://localhost:8983/solr",
            "my_collection",
            auth=BasicAuth("username", "password")
        )

        # Bearer token
        client = SolrClient(
            "http://localhost:8983/solr",
            "my_collection",
            auth=BearerAuth("my-token")
        )
        ```
    """

    def __init__(
        self,
        base_url: str,
        collection: str,
        auth: Optional[SolrAuth] = None,
        timeout: float = 10.0,
        **client_options: Any,
    ):
        """
        Args:
            base_url: Base URL of the Solr instance i.e. http://localhost:8983/solr.
            collection: Name of the Solr collection.
            auth: Authentication method to use (optional).
            timeout: Request timeout in seconds. Defaults to 10.
            **client_options: Additional options to pass to the httpx client.
        """
        self.base_url = base_url.rstrip("/")
        self.collection = collection
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout, **client_options)

        if auth:
            auth.apply(self.client)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        """Close the underlying HTTP client."""
        await self.client.aclose()

    def _build_url(self, endpoint: str) -> str:
        """Build the full URL for a Solr API endpoint."""
        return urljoin(f"{self.base_url}/{self.collection}/", endpoint)

    async def _request(
        self,
        method: str,
        endpoint: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make a request to Solr and handle the response."""
        url = self._build_url(endpoint)

        try:
            response = await self.client.request(
                method=method, url=url, params=params, json=json, **kwargs
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            if hasattr(e, "response") and e.response is not None:
                try:
                    error_data = e.response.json()
                except ValueError:
                    error_data = {"error": e.response.text}
                raise SolrError(
                    f"Solr request failed: {str(e)}",
                    status_code=e.response.status_code,
                    response=error_data,
                )
            raise SolrError(f"HTTP request failed: {str(e)}")

    async def ping(self) -> bool:
        try:
            response = await self._request("GET", "admin/ping")
            return response.get("status") == "OK"
        except SolrError:
            return False

    async def add(
        self,
        documents: SolrDocument | List[SolrDocument],
        commit: bool = True,
    ) -> Dict[str, Any]:
        """
        Add one or more documents to the index.

        Args:
            documents: A single document or list of documents to add. Can be dicts or instances of the document_model (which must be a subclass of SolrDocument).
            commit: Whether to commit the changes immediately
        """
        if not isinstance(documents, list):
            documents = [documents]

        params = {"commit": "true"} if commit else {}
        return await self._request(
            method="POST",
            endpoint="update/json/docs",
            params=params,
            json=[doc.model_dump(exclude_unset=True) for doc in documents],
        )

    async def delete(
        self,
        query: Optional[str] = None,
        ids: Optional[List[str]] = None,
        commit: bool = True,
    ) -> Dict[str, Any]:
        """
        Delete documents from the index.

        Args:
            query: Delete documents matching this query
            ids: Delete documents with these IDs
            commit: Whether to commit the changes immediately
        """
        if not query and not ids:
            raise ValueError("Either query or ids must be provided")

        delete_query = {}
        if query:
            delete_query["query"] = query
        if ids:
            delete_query["id"] = ids

        params = {"commit": "true"} if commit else {}
        return await self._request(
            method="POST",
            endpoint="update",
            params=params,
            json={"delete": delete_query},
        )

    async def commit(self) -> Dict[str, Any]:
        """Commit pending changes to the index."""
        return await self._request(
            method="GET", endpoint="update", params={"commit": "true"}
        )

    async def search(
        self,
        query: Union[str, Dict[str, Any], BaseQueryParser],
        document_model: Type[DocumentT] = SolrDocument,
        **kwargs: Any,
    ) -> SolrResponse[DocumentT]:
        """
        Search the Solr index.

        Args:
            query: Query string, dictionary of parameters, or QueryBuilder instance
            **kwargs: Additional query parameters

        Returns:
            SolrResponse with docs as a list of document_model instances (subclass of SolrDocument).
        """
        if isinstance(query, str):
            params = {"q": query}
        elif isinstance(query, BaseQueryParser):
            params = query.build()
        else:
            params = query

        params.update(kwargs)
        params.setdefault("wt", "json")

        response = await self._request(method="GET", endpoint="select", params=params)

        docs: list[DocumentT] = []
        for doc in response["response"]["docs"]:
            try:
                docs.append(document_model.model_validate(doc, by_name=True))
            except ValidationError:
                docs.append(document_model.model_validate(doc, by_alias=True))
            except Exception:
                raise

        return SolrResponse[document_model](
            status=response["responseHeader"]["status"],
            qtime=response["responseHeader"]["QTime"],
            num_found=response["response"]["numFound"],
            start=response["response"]["start"],
            docs=docs,
            facet_counts=response.get("facet_counts"),
            highlighting=response.get("highlighting"),
        )
