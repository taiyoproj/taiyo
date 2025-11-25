import httpx
from typing import Any, Dict, List, Optional, Union, Type
from typing_extensions import Self

from taiyo.parsers.base import BaseQueryParser
from ..types import SolrDocument, SolrResponse, SolrError, DocumentT
from .auth import SolrAuth
from .base import BaseSolrClient
from ..schema import SolrFieldType, SolrField, SolrDynamicField


class AsyncSolrClient(BaseSolrClient[httpx.AsyncClient]):
    """
    Asynchronous Python client for Apache Solr.

    Args:
        base_url: Base URL of the Solr instance (e.g., "http://localhost:8983/solr")
        auth: Authentication method to use (optional)
        timeout: Request timeout in seconds
        verify: SSL certificate verification (default: True)
        **client_options: Additional options to pass to the httpx client

    Usage:
        ```python
        from taiyo import AsyncSolrClient, BasicAuth
        async with AsyncSolrClient(
            "http://localhost:8983/solr",
            auth=BasicAuth("username", "password")
        ) as client:
            client.set_collection("my_collection")
            results = await client.search("*:*")
        ```
    Note:
        You must call `set_collection()` before using methods that require a collection.
    """

    def __init__(
        self,
        base_url: str,
        auth: Optional[SolrAuth] = None,
        timeout: float = 10.0,
        verify: Union[bool, str] = True,
        **client_options: Any,
    ):
        """
        Args:
            base_url: Base URL of the Solr instance i.e. http://localhost:8983/solr.
            auth: Authentication method to use (optional).
            timeout: Request timeout in seconds. Defaults to 10.
            verify: SSL certificate verification. Can be True (default), False, or path to CA bundle.
            **client_options: Additional options to pass to the httpx client.
        """
        super().__init__(base_url, auth, timeout, verify)
        self._client = httpx.AsyncClient(
            timeout=timeout, verify=verify, **client_options
        )

        if auth:
            auth.apply(self)

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()

    async def close(self) -> None:  # type: ignore[override]
        """Close the underlying HTTP client."""
        await self._client.aclose()

    async def _request(  # type: ignore[override]
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
            response = await self._client.request(
                method=method, url=url, params=params, json=json, **kwargs
            )
            response.raise_for_status()
            result: Dict[str, Any] = response.json()
            return result
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
        content = [doc.model_dump(exclude_unset=True) for doc in documents]
        response = await self._client.post(
            url=self._build_url("update/json/docs"),
            params=params,
            json=content,
        )
        result: Dict[str, Any] = response.json()
        return result

    async def delete(
        self,
        query: Optional[str] = None,
        ids: Optional[Union[str, List[str]]] = None,
        commit: bool = True,
    ) -> Dict[str, Any]:
        """
        Delete documents from the index.

        Supports multiple delete formats per Apache Solr specification:
        - Single ID: {"delete": "myid"}
        - Multiple IDs: {"delete": ["id1", "id2"]}
        - Query: {"delete": {"query": "field:value"}}
        - Combined: {"delete": {"id": "myid", "query": "field:value"}}

        Args:
            query: Delete documents matching this query
            ids: Delete document(s) with this ID or these IDs. Can be a single string or list.
            commit: Whether to commit the changes immediately

        Returns:
            Response from Solr

        Example:
            ```python
            # Delete by single ID
            await client.delete(ids="doc1")

            # Delete by multiple IDs
            await client.delete(ids=["doc1", "doc2"])

            # Delete by query
            await client.delete(query="status:archived")

            # Delete by ID and query combined
            await client.delete(ids="doc1", query="status:archived")
            ```
        """
        if not self.collection:
            raise ValueError("collection needs to be specified via set_collection().")

        if not (query or ids):
            raise ValueError("Either query or ids must be provided")

        delete_cmd = self._build_delete_command(query=query, ids=ids)
        params = {"commit": "true"} if commit else {}

        return await self._request(
            method="POST",
            endpoint="update",
            params=params,
            json={"delete": delete_cmd},
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
        document_model: Type[DocumentT] = SolrDocument,  # type: ignore[assignment]
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

    async def add_field_type(
        self,
        field_type: Union[SolrFieldType, Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Add a field type to the collection schema.

        Args:
            field_type: SolrFieldType instance or dictionary defining the field type

        Returns:
            Response from Solr Schema API

        Example:
            ```python
            from taiyo.schema import SolrFieldType, SolrFieldClass

            field_type = SolrFieldType(
                name="text_general",
                solr_class=SolrFieldClass.TEXT,
                position_increment_gap=100
            )
            await client.add_field_type(field_type)
            ```
        """
        if not self.collection:
            raise ValueError("collection needs to be specified via set_collection().")

        if isinstance(field_type, SolrFieldType):
            field_type_dict = field_type.build(format="json")
        else:
            field_type_dict = field_type

        return await self._request(
            method="POST",
            endpoint=f"{self.collection}/schema/fieldtypes",
            json={"add-field-type": field_type_dict},
        )

    async def add_field(
        self,
        field: Union[SolrField, Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Add a field to the collection schema.

        Args:
            field: SolrField instance or dictionary defining the field

        Returns:
            Response from Solr Schema API

        Example:
            ```python
            from taiyo.schema import SolrField

            field = SolrField(
                name="title",
                type="text_general",
                indexed=True,
                stored=True
            )
            await client.add_field(field)
            ```
        """
        if not self.collection:
            raise ValueError("collection needs to be specified via set_collection().")

        if isinstance(field, SolrField):
            field_dict = field.build(format="json")
        else:
            field_dict = field

        return await self._request(
            method="POST",
            endpoint=f"{self.collection}/schema/fields",
            json={"add-field": field_dict},
        )

    async def add_dynamic_field(
        self,
        field: Union[SolrDynamicField, Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Add a dynamic field to the collection schema.

        Args:
            field: SolrDynamicField instance or dictionary defining the dynamic field

        Returns:
            Response from Solr Schema API

        Example:
            ```python
            from taiyo.schema import SolrDynamicField

            field = SolrDynamicField(
                name="*_txt",
                type="text_general",
                indexed=True,
                stored=True
            )
            await client.add_dynamic_field(field)
            ```
        """
        if not self.collection:
            raise ValueError("collection needs to be specified via set_collection().")

        if isinstance(field, SolrDynamicField):
            field_dict = field.build(format="json")
        else:
            field_dict = field

        return await self._request(
            method="POST",
            endpoint=f"{self.collection}/schema/fields",
            json={"add-dynamic-field": field_dict},
        )


class SolrClient(BaseSolrClient[httpx.Client]):
    """
    Synchronous Python client for Apache Solr.

    Args:
        base_url: Base URL of the Solr instance (e.g., "http://localhost:8983/solr")
        auth: Authentication method to use (optional)
        timeout: Request timeout in seconds
        verify: SSL certificate verification (default: True)
        **client_options: Additional options to pass to the httpx client

    Usage:
        ```python
        from taiyo import SolrClient, BasicAuth
        with SolrClient(
            "http://localhost:8983/solr",
            auth=BasicAuth("username", "password")
        ) as client:
            client.set_collection("my_collection")
            results = client.search("*:*")
        ```
    Note:
        You must call `set_collection()` before using methods that require a collection.
    """

    def __init__(
        self,
        base_url: str,
        auth: Optional[SolrAuth] = None,
        timeout: float = 10.0,
        verify: Union[bool, str] = True,
        **client_options: Any,
    ):
        """
        Args:
            base_url: Base URL of the Solr instance i.e. http://localhost:8983/solr.
            auth: Authentication method to use (optional).
            timeout: Request timeout in seconds. Defaults to 10.
            verify: SSL certificate verification. Can be True (default), False, or path to CA bundle.
            **client_options: Additional options to pass to the httpx client.
        """
        super().__init__(base_url, auth, timeout, verify)
        self._client = httpx.Client(timeout=timeout, verify=verify, **client_options)

        if auth:
            auth.apply(self)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()

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
            response = self._client.request(
                method=method, url=url, params=params, json=json, **kwargs
            )
            response.raise_for_status()
            result: Dict[str, Any] = response.json()
            return result
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
        content = [doc.model_dump(exclude_unset=True) for doc in documents]
        response = self._client.post(
            url=self._build_url(f"{self.collection}/update/json/docs"),
            params=params,
            json=content,
        )
        response.raise_for_status()
        result: Dict[str, Any] = response.json()
        return result

    def delete(
        self,
        query: Optional[str] = None,
        ids: Optional[Union[str, List[str]]] = None,
        commit: bool = True,
    ) -> Dict[str, Any]:
        """
        Delete documents from the index.

        Supports multiple delete formats per Apache Solr specification:
        - Single ID: {"delete": "myid"}
        - Multiple IDs: {"delete": ["id1", "id2"]}
        - Query: {"delete": {"query": "field:value"}}
        - Combined: {"delete": {"id": "myid", "query": "field:value"}}

        Args:
            query: Delete documents matching this query
            ids: Delete document(s) with this ID or these IDs. Can be a single string or list.
            commit: Whether to commit the changes immediately

        Returns:
            Response from Solr

        Example:
            ```python
            # Delete by single ID
            client.delete(ids="doc1")

            # Delete by multiple IDs
            client.delete(ids=["doc1", "doc2"])

            # Delete by query
            client.delete(query="status:archived")

            # Delete by ID and query combined
            client.delete(ids="doc1", query="status:archived")
            ```
        """
        if not self.collection:
            raise ValueError("collection needs to be specified via set_collection().")

        if not (query or ids):
            raise ValueError("Either query or ids must be provided")

        delete_cmd = self._build_delete_command(query=query, ids=ids)
        params = {"commit": "true"} if commit else {}

        return self._request(
            method="POST",
            endpoint=f"{self.collection}/update",
            params=params,
            json={"delete": delete_cmd},
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
        document_model: Type[DocumentT] = SolrDocument,  # type: ignore[assignment]
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

    def add_field_type(
        self,
        field_type: Union[SolrFieldType, Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Add a field type to the collection schema.

        Args:
            field_type: SolrFieldType instance or dictionary defining the field type

        Returns:
            Response from Solr Schema API

        Example:
            ```python
            from taiyo.schema import SolrFieldType, SolrFieldClass

            field_type = SolrFieldType(
                name="text_general",
                solr_class=SolrFieldClass.TEXT,
                position_increment_gap=100
            )
            client.add_field_type(field_type)
            ```
        """
        if not self.collection:
            raise ValueError("collection needs to be specified via set_collection().")

        if isinstance(field_type, SolrFieldType):
            field_type_dict = field_type.build(format="json")
        else:
            field_type_dict = field_type

        return self._request(
            method="POST",
            endpoint=f"{self.collection}/schema/fieldtypes",
            json={"add-field-type": field_type_dict},
        )

    def add_field(
        self,
        field: Union[SolrField, Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Add a field to the collection schema.

        Args:
            field: SolrField instance or dictionary defining the field

        Returns:
            Response from Solr Schema API

        Example:
            ```python
            from taiyo.schema import SolrField

            field = SolrField(
                name="title",
                type="text_general",
                indexed=True,
                stored=True
            )
            client.add_field(field)
            ```
        """
        if not self.collection:
            raise ValueError("collection needs to be specified via set_collection().")

        if isinstance(field, SolrField):
            field_dict = field.build(format="json")
        else:
            field_dict = field

        return self._request(
            method="POST",
            endpoint=f"{self.collection}/schema/fields",
            json={"add-field": field_dict},
        )

    def add_dynamic_field(
        self,
        field: Union[SolrDynamicField, Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Add a dynamic field to the collection schema.

        Args:
            field: SolrDynamicField instance or dictionary defining the dynamic field

        Returns:
            Response from Solr Schema API

        Example:
            ```python
            from taiyo.schema import SolrDynamicField

            field = SolrDynamicField(
                name="*_txt",
                type="text_general",
                indexed=True,
                stored=True
            )
            client.add_dynamic_field(field)
            ```
        """
        if not self.collection:
            raise ValueError("collection needs to be specified via set_collection().")

        if isinstance(field, SolrDynamicField):
            field_dict = field.build(format="json")
        else:
            field_dict = field

        return self._request(
            method="POST",
            endpoint=f"{self.collection}/schema/fields",
            json={"add-dynamic-field": field_dict},
        )
