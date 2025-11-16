import httpx
from typing import Any, Dict, List, Optional, Union, Type

from taiyo.parsers.base import BaseQueryParser
from ..types import SolrDocument, SolrResponse, SolrError, DocumentT
from .auth import SolrAuth
from .base import BaseSolrClient


class AsyncSolrClient(BaseSolrClient):
    """
    Asynchronous Python client for Apache Solr.

    Args:
        base_url: Base URL of the Solr instance (e.g., "http://localhost:8983/solr")
        auth: Authentication method to use (optional)
        timeout: Request timeout in seconds
        **client_options: Additional options to pass to the httpx client

    Example:
        ```python
        from taiyo import AsyncSolrClient, BasicAuth
        async with AsyncSolrClient(
            "http://localhost:8983/solr",
            "my_collection",
            auth=BasicAuth("username", "password")
        ) as client:
            results = await client.search("*:*")
        ```
    """

    def __init__(
        self,
        base_url: str,
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
        super().__init__(base_url, auth, timeout)
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
        """
        Ping the Solr instance to check if it's available.

        Returns:
            True if Solr is available, False otherwise
        """
        try:
            response = await self._request("GET", "admin/info/system")
            return response.get("status") == "OK"
        except SolrError:
            return False

    async def create_collection(
        self,
        name: str,
        num_shards: int = 1,
        replication_factor: int = 1,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Create a new Solr collection using the v2 Collections API (POST /api/collections).

        Args:
            name: Name of the collection to create.
            num_shards: Number of shards for the collection.
            replication_factor: Replication factor for the collection.
            **kwargs: Additional Solr parameters (included in JSON body).

        Returns:
            Response from Solr.
        """
        json_body = {
            "name": name,
            "numShards": num_shards,
            "replicationFactor": replication_factor,
            **kwargs,
        }
        return await self._request(
            method="POST",
            endpoint="/api/collections",
            json=json_body,
        )

    async def delete_collection(self, name: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Delete a Solr collection.

        Args:
            name: Name of the collection to delete.

        Returns:
            Response from Solr.
        """
        return await self._request("DELETE", f"/api/collections/{name}")

    async def add(
        self,
        documents: Union[SolrDocument, List[SolrDocument]],
        commit: bool = True,
    ) -> Dict[str, Any]:
        """
        Add one or more documents to the index.

        Args:
            documents: A single document or list of documents to add. Can be dicts or instances of the document_model (which must be a subclass of SolrDocument).
            commit: Whether to commit the changes immediately

        Returns:
            Response from Solr
        """
        if not self.collection:
            raise ValueError("collection needs to be specified via set_collection().")

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

        Returns:
            Response from Solr
        """
        if not self.collection:
            raise ValueError("collection needs to be specified via set_collection().")

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
        """
        Commit pending changes to the index.

        Returns:
            Response from Solr
        """
        return await self._request(
            method="GET",
            endpoint=f"{self.collection}/update",
            params={"commit": "true"},
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
            document_model: Pydantic model class for documents
            **kwargs: Additional query parameters

        Returns:
            SolrResponse with docs as a list of document_model instances (subclass of SolrDocument).
        """
        params = self._build_search_params(query, **kwargs)
        response = await self._request(
            method="GET", endpoint=f"{self.collection}/select", params=params
        )
        return self._build_search_response(response, document_model)


class SolrClient(BaseSolrClient):
    """
    Synchronous Python client for Apache Solr.

    Args:
        base_url: Base URL of the Solr instance (e.g., "http://localhost:8983/solr")
        collection: Name of the Solr collection
        auth: Authentication method to use (optional)
        timeout: Request timeout in seconds
        **client_options: Additional options to pass to the httpx client

    Example:
        ```python
        from taiyo import SolrClient, BasicAuth
        with SolrClient(
            "http://localhost:8983/solr",
            "my_collection",
            auth=BasicAuth("username", "password")
        ) as client:
            results = client.search("*:*")
        ```
    """

    def __init__(
        self,
        base_url: str,
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
        super().__init__(base_url, auth, timeout)
        self.client = httpx.Client(timeout=timeout, **client_options)

        if auth:
            auth.apply(self.client)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """Close the underlying HTTP client."""
        self.client.close()

    def _request(
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
            response = self.client.request(
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

    def ping(self) -> bool:
        """
        Ping the Solr instance to check if it's available.

        Returns:
            True if Solr is available, False otherwise
        """
        try:
            response = self._request("GET", "admin/info/system")
            return response.get("status") == "OK"
        except SolrError:
            return False

    def create_collection(
        self,
        name: str,
        num_shards: int = 1,
        replication_factor: int = 1,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Create a new Solr collection using the v2 Collections API (POST /api/collections).

        Args:
            name: Name of the collection to create.
            num_shards: Number of shards for the collection.
            replication_factor: Replication factor for the collection.
            **kwargs: Additional Solr parameters (included in JSON body).

        Returns:
            Response from Solr.
        """
        json_body = {
            "name": name,
            "numShards": num_shards,
            "replicationFactor": replication_factor,
            **kwargs,
        }
        return self._request(
            method="POST",
            endpoint="/api/collections",
            json=json_body,
        )

    def delete_collection(self, name: str) -> Dict[str, Any]:
        """
        Delete a Solr collection.

        Args:
            name: Name of the collection to delete.

        Returns:
            Response from Solr.
        """
        return self._request("DELETE", f"/api/collections/{name}")

    def add(
        self,
        documents: Union[SolrDocument, List[SolrDocument]],
        commit: bool = True,
    ) -> Dict[str, Any]:
        """
        Add one or more documents to the index.

        Args:
            documents: A single document or list of documents to add. Can be dicts or instances of the document_model (which must be a subclass of SolrDocument).
            commit: Whether to commit the changes immediately

        Returns:
            Response from Solr
        """
        if not isinstance(documents, list):
            documents = [documents]

        params = {"commit": "true"} if commit else {}
        return self._request(
            method="POST",
            endpoint=f"{self.collection}/update/json/docs",
            params=params,
            json=[doc.model_dump(exclude_unset=True) for doc in documents],
        )

    def delete(
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

        Returns:
            Response from Solr
        """
        if not query and not ids:
            raise ValueError("Either query or ids must be provided")

        delete_query = {}
        if query:
            delete_query["query"] = query
        if ids:
            delete_query["id"] = ids

        params = {"commit": "true"} if commit else {}
        return self._request(
            method="POST",
            endpoint=f"{self.collection}/update",
            params=params,
            json={"delete": delete_query},
        )

    def commit(self) -> Dict[str, Any]:
        """
        Commit pending changes to the index.

        Returns:
            Response from Solr
        """
        return self._request(
            method="GET",
            endpoint=f"{self.collection}/update",
            params={"commit": "true"},
        )

    def search(
        self,
        query: Union[str, Dict[str, Any], BaseQueryParser],
        document_model: Type[DocumentT] = SolrDocument,
        **kwargs: Any,
    ) -> SolrResponse[DocumentT]:
        """
        Search the Solr index.

        Args:
            query: query string, dictionary of parameters, or BaseQueryParser instance
            document_model: Pydantic model class for documents
            **kwargs: Additional query parameters

        Returns:
            SolrResponse with docs as a list of document_model instances (subclass of SolrDocument).
        """
        params = self._build_search_params(query, **kwargs)
        response = self._request(
            method="GET", endpoint=f"{self.collection}/select", params=params
        )
        return self._build_search_response(response, document_model)
