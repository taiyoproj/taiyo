"""Tests for the SolrClient and AsyncSolrClient classes."""

import pytest
import httpx
from httpx import Response
from taiyo import SolrClient, AsyncSolrClient, SolrError
from tests.unit.conftest import MyDocument, collection
from tests.unit.mocks import (
    mock_search_response,
    mock_update_response,
    mock_delete_response,
    mock_solr_error,
    mock_facet_response,
    mock_highlight_response,
)
import types
from taiyo.client.base import BaseSolrClient


# ============================================================================
# Async Client Tests
# ============================================================================


@pytest.mark.asyncio
async def test_async_ping_success(async_solr_client: AsyncSolrClient, monkeypatch):
    """Test successful ping response."""

    async def mock_request(*args, **kwargs):
        request = httpx.Request("GET", "http://localhost:8983")
        response = Response(200, json={"status": "OK"})
        response._request = request
        return response

    monkeypatch.setattr(async_solr_client._client, "request", mock_request)
    assert await async_solr_client.ping() is True


@pytest.mark.asyncio
async def test_async_ping_failure(async_solr_client: AsyncSolrClient, monkeypatch):
    """Test failed ping response."""

    async def mock_request(*args, **kwargs):
        request = httpx.Request("GET", "http://localhost:8983")
        response = Response(500, json={"status": "ERROR"})
        response._request = request
        return response

    monkeypatch.setattr(async_solr_client._client, "request", mock_request)
    assert await async_solr_client.ping() is False


@pytest.mark.asyncio
async def test_async_add_single_document(
    async_solr_client: AsyncSolrClient, monkeypatch, sample_doc
):
    """Test adding a single document."""

    async def mock_request(*args, **kwargs):
        assert kwargs["json"] == [sample_doc.model_dump(exclude_unset=True)]
        assert kwargs["params"] == {"commit": "true"}
        request = httpx.Request(
            "POST",
            "http://localhost:8983",
            json=[sample_doc.model_dump(exclude_unset=True)],
        )
        response = Response(200, json=mock_update_response())
        response._request = request
        return response

    monkeypatch.setattr(async_solr_client._client, "request", mock_request)
    async_solr_client.set_collection(collection)
    response = await async_solr_client.add(sample_doc)
    assert response["responseHeader"]["status"] == 0


@pytest.mark.asyncio
async def test_async_add_multiple_documents(
    async_solr_client: AsyncSolrClient, monkeypatch, sample_docs
):
    """Test adding multiple documents."""

    async def mock_request(*args, **kwargs):
        expected_json = [doc.model_dump(exclude_unset=True) for doc in sample_docs]
        assert kwargs["json"] == expected_json
        assert kwargs["params"] == {"commit": "true"}
        request = httpx.Request("POST", "http://localhost:8983", json=expected_json)
        response = Response(200, json=mock_update_response())
        response._request = request
        return response

    monkeypatch.setattr(async_solr_client._client, "request", mock_request)
    async_solr_client.set_collection(collection)
    response = await async_solr_client.add(sample_docs)
    assert response["responseHeader"]["status"] == 0


@pytest.mark.asyncio
async def test_async_delete_by_id(async_solr_client: AsyncSolrClient, monkeypatch):
    """Test deleting documents by ID."""
    ids = ["1", "2"]

    async def mock_request(*args, **kwargs):
        assert kwargs["json"] == {"delete": {"id": ids}}
        assert kwargs["params"] == {"commit": "true"}
        request = httpx.Request(
            "POST", "http://localhost:8983", json={"delete": {"id": ids}}
        )
        response = Response(200, json=mock_delete_response())
        response._request = request
        return response

    monkeypatch.setattr(async_solr_client._client, "request", mock_request)
    async_solr_client.set_collection(collection)
    response = await async_solr_client.delete(ids=ids)
    assert response["responseHeader"]["status"] == 0


@pytest.mark.asyncio
async def test_async_delete_by_query(async_solr_client: AsyncSolrClient, monkeypatch):
    """Test deleting documents by query."""
    query = "title:test"

    async def mock_request(*args, **kwargs):
        assert kwargs["json"] == {"delete": {"query": query}}
        assert kwargs["params"] == {"commit": "true"}
        request = httpx.Request(
            "POST", "http://localhost:8983", json={"delete": {"query": query}}
        )
        response = Response(200, json=mock_delete_response())
        response._request = request
        return response

    monkeypatch.setattr(async_solr_client._client, "request", mock_request)
    async_solr_client.set_collection(collection)
    response = await async_solr_client.delete(query=query)
    assert response["responseHeader"]["status"] == 0


@pytest.mark.asyncio
async def test_async_search_basic(
    async_solr_client: AsyncSolrClient, monkeypatch, sample_docs
):
    """Test basic search functionality."""

    async def mock_request(*args, **kwargs):
        assert kwargs["params"]["q"] == "title:test"
        docs_dicts = [doc.model_dump(exclude_unset=True) for doc in sample_docs]
        request = httpx.Request("GET", "http://localhost:8983", params=kwargs["params"])
        response = Response(200, json=mock_search_response(docs_dicts))
        response._request = request
        return response

    monkeypatch.setattr(async_solr_client._client, "request", mock_request)
    async_solr_client.set_collection(collection)
    response = await async_solr_client.search("title:test", MyDocument)
    assert response.num_found == len(sample_docs)
    assert len(response.docs) == len(sample_docs)
    for doc in response.docs:
        assert isinstance(doc, type(sample_docs[0]))
        assert hasattr(doc, "category")
        assert doc.category in {"books", "electronics"}


@pytest.mark.asyncio
async def test_async_search_with_facets(
    async_solr_client: AsyncSolrClient, monkeypatch, sample_docs
):
    """Test search with facets."""
    facets = {"category": {"books": 5, "electronics": 3}}

    async def mock_request(*args, **kwargs):
        docs_dicts = [doc.model_dump(exclude_unset=True) for doc in sample_docs]
        request = httpx.Request("GET", "http://localhost:8983", params=kwargs["params"])
        response = Response(200, json=mock_facet_response(docs_dicts, facets))
        response._request = request
        return response

    monkeypatch.setattr(async_solr_client._client, "request", mock_request)
    async_solr_client.set_collection(collection)
    response = await async_solr_client.search(
        "*:*", facet="true", facet_field="category"
    )
    assert response.facet_counts is not None
    assert response.facet_counts["facet_fields"] == facets


@pytest.mark.asyncio
async def test_async_search_with_highlighting(
    async_solr_client: AsyncSolrClient, monkeypatch, sample_docs
):
    """Test search with highlighting."""
    highlights = {
        "1": {"title": ["<em>Test</em> Document"]},
        "2": {"title": ["Another <em>Test</em>"]},
    }

    async def mock_request(*args, **kwargs):
        docs_dicts = [doc.model_dump(exclude_unset=True) for doc in sample_docs]
        request = httpx.Request("GET", "http://localhost:8983", params=kwargs["params"])
        response = Response(200, json=mock_highlight_response(docs_dicts, highlights))
        response._request = request
        return response

    monkeypatch.setattr(async_solr_client._client, "request", mock_request)
    async_solr_client.set_collection(collection)
    response = await async_solr_client.search("test", hl="true", hl_fl="title")
    assert response.highlighting == highlights


@pytest.mark.asyncio
async def test_async_error_handling(async_solr_client: AsyncSolrClient, monkeypatch):
    """Test error handling."""
    error_message = "Invalid query syntax"

    async def mock_request(*args, **kwargs):
        request = httpx.Request(
            "GET", "http://localhost:8983", params=kwargs.get("params")
        )
        error_response = mock_solr_error(error_message)
        response = Response(400, json=error_response)
        response._request = request
        return response

    monkeypatch.setattr(async_solr_client._client, "request", mock_request)

    with pytest.raises(SolrError) as exc_info:
        await async_solr_client.search("invalid:query]")

    assert exc_info.value.status_code == 400
    assert exc_info.value.response["error"]["message"] == error_message


# ============================================================================
# Sync Client Tests
# ============================================================================


def test_sync_ping_success(sync_solr_client: SolrClient, monkeypatch):
    """Test successful ping response."""

    def mock_request(*args, **kwargs):
        request = httpx.Request("GET", "http://localhost:8983")
        response = Response(200, json={"status": "OK"})
        response._request = request
        return response

    monkeypatch.setattr(sync_solr_client._client, "request", mock_request)
    assert sync_solr_client.ping() is True


def test_sync_ping_failure(sync_solr_client: SolrClient, monkeypatch):
    """Test failed ping response."""

    def mock_request(*args, **kwargs):
        request = httpx.Request("GET", "http://localhost:8983")
        response = Response(500, json={"status": "ERROR"})
        response._request = request
        return response

    monkeypatch.setattr(sync_solr_client._client, "request", mock_request)
    assert sync_solr_client.ping() is False


def test_sync_add_single_document(
    sync_solr_client: SolrClient, monkeypatch, sample_doc
):
    """Test adding a single document."""

    def mock_request(*args, **kwargs):
        assert kwargs["json"] == [sample_doc.model_dump(exclude_unset=True)]
        assert kwargs["params"] == {"commit": "true"}
        request = httpx.Request(
            "POST",
            "http://localhost:8983",
            json=[sample_doc.model_dump(exclude_unset=True)],
        )
        response = Response(200, json=mock_update_response())
        response._request = request
        return response

    monkeypatch.setattr(sync_solr_client._client, "request", mock_request)
    response = sync_solr_client.add(sample_doc)
    assert response["responseHeader"]["status"] == 0


def test_sync_add_multiple_documents(
    sync_solr_client: SolrClient, monkeypatch, sample_docs
):
    """Test adding multiple documents."""

    def mock_request(*args, **kwargs):
        expected_json = [doc.model_dump(exclude_unset=True) for doc in sample_docs]
        assert kwargs["json"] == expected_json
        assert kwargs["params"] == {"commit": "true"}
        request = httpx.Request("POST", "http://localhost:8983", json=expected_json)
        response = Response(200, json=mock_update_response())
        response._request = request
        return response

    monkeypatch.setattr(sync_solr_client._client, "request", mock_request)
    response = sync_solr_client.add(sample_docs)
    assert response["responseHeader"]["status"] == 0


def test_sync_delete_by_id(sync_solr_client: SolrClient, monkeypatch):
    """Test deleting documents by ID."""
    ids = ["1", "2"]

    def mock_request(*args, **kwargs):
        assert kwargs["json"] == {"delete": {"id": ids}}
        assert kwargs["params"] == {"commit": "true"}
        request = httpx.Request(
            "POST", "http://localhost:8983", json={"delete": {"id": ids}}
        )
        response = Response(200, json=mock_delete_response())
        response._request = request
        return response

    monkeypatch.setattr(sync_solr_client._client, "request", mock_request)
    response = sync_solr_client.delete(ids=ids)
    assert response["responseHeader"]["status"] == 0


def test_sync_delete_by_query(sync_solr_client: SolrClient, monkeypatch):
    """Test deleting documents by query."""
    query = "title:test"

    def mock_request(*args, **kwargs):
        assert kwargs["json"] == {"delete": {"query": query}}
        assert kwargs["params"] == {"commit": "true"}
        request = httpx.Request(
            "POST", "http://localhost:8983", json={"delete": {"query": query}}
        )
        response = Response(200, json=mock_delete_response())
        response._request = request
        return response

    monkeypatch.setattr(sync_solr_client._client, "request", mock_request)
    response = sync_solr_client.delete(query=query)
    assert response["responseHeader"]["status"] == 0


def test_sync_search_basic(sync_solr_client: SolrClient, monkeypatch, sample_docs):
    """Test basic search functionality."""

    def mock_request(*args, **kwargs):
        assert kwargs["params"]["q"] == "title:test"
        docs_dicts = [doc.model_dump(exclude_unset=True) for doc in sample_docs]
        request = httpx.Request("GET", "http://localhost:8983", params=kwargs["params"])
        response = Response(200, json=mock_search_response(docs_dicts))
        response._request = request
        return response

    monkeypatch.setattr(sync_solr_client._client, "request", mock_request)
    response = sync_solr_client.search("title:test", MyDocument)
    assert response.num_found == len(sample_docs)
    assert len(response.docs) == len(sample_docs)
    for doc in response.docs:
        assert isinstance(doc, type(sample_docs[0]))
        assert hasattr(doc, "category")
        assert doc.category in {"books", "electronics"}


def test_sync_search_with_facets(
    sync_solr_client: SolrClient, monkeypatch, sample_docs
):
    """Test search with facets."""
    facets = {"category": {"books": 5, "electronics": 3}}

    def mock_request(*args, **kwargs):
        docs_dicts = [doc.model_dump(exclude_unset=True) for doc in sample_docs]
        request = httpx.Request("GET", "http://localhost:8983", params=kwargs["params"])
        response = Response(200, json=mock_facet_response(docs_dicts, facets))
        response._request = request
        return response

    monkeypatch.setattr(sync_solr_client._client, "request", mock_request)
    response = sync_solr_client.search("*:*", facet="true", facet_field="category")
    assert response.facet_counts is not None
    assert response.facet_counts["facet_fields"] == facets


def test_sync_search_with_highlighting(
    sync_solr_client: SolrClient, monkeypatch, sample_docs
):
    """Test search with highlighting."""
    highlights = {
        "1": {"title": ["<em>Test</em> Document"]},
        "2": {"title": ["Another <em>Test</em>"]},
    }

    def mock_request(*args, **kwargs):
        docs_dicts = [doc.model_dump(exclude_unset=True) for doc in sample_docs]
        request = httpx.Request("GET", "http://localhost:8983", params=kwargs["params"])
        response = Response(200, json=mock_highlight_response(docs_dicts, highlights))
        response._request = request
        return response

    monkeypatch.setattr(sync_solr_client._client, "request", mock_request)
    response = sync_solr_client.search("test", hl="true", hl_fl="title")
    assert response.highlighting == highlights


def test_sync_error_handling(sync_solr_client: SolrClient, monkeypatch):
    """Test error handling."""
    error_message = "Invalid query syntax"

    def mock_request(*args, **kwargs):
        request = httpx.Request(
            "GET", "http://localhost:8983", params=kwargs.get("params")
        )
        error_response = mock_solr_error(error_message)
        response = Response(400, json=error_response)
        response._request = request
        return response

    monkeypatch.setattr(sync_solr_client._client, "request", mock_request)

    with pytest.raises(SolrError) as exc_info:
        sync_solr_client.search("invalid:query]")

    assert exc_info.value.status_code == 400
    assert exc_info.value.response["error"]["message"] == error_message


# ============================================================================
# BaseSolrClient Tests
# ============================================================================


class DummySolrClient(BaseSolrClient):
    def __init__(self, base_url, auth=None, timeout=10.0):
        super().__init__(base_url, auth, timeout)
        # Use a simple dict for headers for testing
        self._client = types.SimpleNamespace(headers={})

    def _request(self, *a, **k):
        return {}


def test_base_solr_client_set_collection():
    client = DummySolrClient("http://localhost:8983/solr")
    client.set_collection("my_collection")
    assert client.collection == "my_collection"


def test_base_solr_client_set_headers_single():
    client = DummySolrClient("http://localhost:8983/solr")
    client.set_header("X-Test", "value")
    assert client._client.headers["X-Test"] == "value"
    client.unset_header("X-Test")
    assert "X-Test" not in client._client.headers


def test_base_solr_client_set_headers_dict():
    client = DummySolrClient("http://localhost:8983/solr")
    client.set_header("A", "1")
    client.set_header("B", "2")
    assert client._client.headers["A"] == "1"
    assert client._client.headers["B"] == "2"
    client.unset_header("A")
    client.unset_header("B")
    assert "A" not in client._client.headers
    assert "B" not in client._client.headers


@pytest.mark.asyncio
async def test_async_add_field_type_with_schema_object(
    async_solr_client: AsyncSolrClient, monkeypatch
):
    """Test adding field type using SolrFieldType object."""
    from taiyo.schema import SolrFieldType, SolrFieldClass

    field_type = SolrFieldType(
        name="text_general",
        solr_class=SolrFieldClass.TEXT,
        position_increment_gap=100,
    )

    async def mock_request(*args, **kwargs):
        assert kwargs["json"]["add-field-type"]["name"] == "text_general"
        assert kwargs["json"]["add-field-type"]["class"] == "solr.TextField"
        assert kwargs["json"]["add-field-type"]["positionIncrementGap"] == 100
        request = httpx.Request("POST", "http://localhost:8983", json=kwargs["json"])
        response = Response(200, json={"responseHeader": {"status": 0}})
        response._request = request
        return response

    monkeypatch.setattr(async_solr_client._client, "request", mock_request)
    async_solr_client.set_collection(collection)
    response = await async_solr_client.add_field_type(field_type)
    assert response["responseHeader"]["status"] == 0


@pytest.mark.asyncio
async def test_async_add_field_type_with_dict(
    async_solr_client: AsyncSolrClient, monkeypatch
):
    """Test adding field type using dictionary."""
    field_type_dict = {
        "name": "pdouble",
        "class": "solr.DoublePointField",
        "docValues": True,
    }

    async def mock_request(*args, **kwargs):
        assert kwargs["json"]["add-field-type"] == field_type_dict
        request = httpx.Request("POST", "http://localhost:8983", json=kwargs["json"])
        response = Response(200, json={"responseHeader": {"status": 0}})
        response._request = request
        return response

    monkeypatch.setattr(async_solr_client._client, "request", mock_request)
    async_solr_client.set_collection(collection)
    response = await async_solr_client.add_field_type(field_type_dict)
    assert response["responseHeader"]["status"] == 0


@pytest.mark.asyncio
async def test_async_add_field_with_schema_object(
    async_solr_client: AsyncSolrClient, monkeypatch
):
    """Test adding field using SolrField object."""
    from taiyo.schema import SolrField

    field = SolrField(
        name="title",
        type="text_general",
        indexed=True,
        stored=True,
    )

    async def mock_request(*args, **kwargs):
        assert kwargs["json"]["add-field"]["name"] == "title"
        assert kwargs["json"]["add-field"]["type"] == "text_general"
        assert kwargs["json"]["add-field"]["indexed"] is True
        request = httpx.Request("POST", "http://localhost:8983", json=kwargs["json"])
        response = Response(200, json={"responseHeader": {"status": 0}})
        response._request = request
        return response

    monkeypatch.setattr(async_solr_client._client, "request", mock_request)
    async_solr_client.set_collection(collection)
    response = await async_solr_client.add_field(field)
    assert response["responseHeader"]["status"] == 0


@pytest.mark.asyncio
async def test_async_add_dynamic_field(async_solr_client: AsyncSolrClient, monkeypatch):
    """Test adding dynamic field using SolrDynamicField object."""
    from taiyo.schema import SolrDynamicField

    field = SolrDynamicField(
        name="*_txt",
        type="text_general",
        indexed=True,
        stored=True,
    )

    async def mock_request(*args, **kwargs):
        assert kwargs["json"]["add-dynamic-field"]["name"] == "*_txt"
        assert kwargs["json"]["add-dynamic-field"]["type"] == "text_general"
        request = httpx.Request("POST", "http://localhost:8983", json=kwargs["json"])
        response = Response(200, json={"responseHeader": {"status": 0}})
        response._request = request
        return response

    monkeypatch.setattr(async_solr_client._client, "request", mock_request)
    async_solr_client.set_collection(collection)
    response = await async_solr_client.add_dynamic_field(field)
    assert response["responseHeader"]["status"] == 0


def test_sync_add_field_type_with_schema_object(
    sync_solr_client: SolrClient, monkeypatch
):
    """Test adding field type using SolrFieldType object (sync)."""
    from taiyo.schema import SolrFieldType, SolrFieldClass

    field_type = SolrFieldType(
        name="knn_vector",
        solr_class=SolrFieldClass.DENSE_VECTOR,
        vectorDimension=768,
        similarityFunction="cosine",
    )

    def mock_request(*args, **kwargs):
        assert kwargs["json"]["add-field-type"]["name"] == "knn_vector"
        assert kwargs["json"]["add-field-type"]["class"] == "solr.DenseVectorField"
        assert kwargs["json"]["add-field-type"]["vectorDimension"] == 768
        request = httpx.Request("POST", "http://localhost:8983", json=kwargs["json"])
        response = Response(200, json={"responseHeader": {"status": 0}})
        response._request = request
        return response

    monkeypatch.setattr(sync_solr_client._client, "request", mock_request)
    sync_solr_client.set_collection(collection)
    response = sync_solr_client.add_field_type(field_type)
    assert response["responseHeader"]["status"] == 0


def test_sync_add_field_with_schema_object(sync_solr_client: SolrClient, monkeypatch):
    """Test adding field using SolrField object (sync)."""
    from taiyo.schema import SolrField

    field = SolrField(
        name="vector",
        type="knn_vector",
        indexed=True,
        stored=False,
    )

    def mock_request(*args, **kwargs):
        assert kwargs["json"]["add-field"]["name"] == "vector"
        assert kwargs["json"]["add-field"]["type"] == "knn_vector"
        assert kwargs["json"]["add-field"]["indexed"] is True
        assert kwargs["json"]["add-field"]["stored"] is False
        request = httpx.Request("POST", "http://localhost:8983", json=kwargs["json"])
        response = Response(200, json={"responseHeader": {"status": 0}})
        response._request = request
        return response

    monkeypatch.setattr(sync_solr_client._client, "request", mock_request)
    sync_solr_client.set_collection(collection)
    response = sync_solr_client.add_field(field)
    assert response["responseHeader"]["status"] == 0


@pytest.mark.asyncio
async def test_async_add_field_type_without_collection_raises(
    async_solr_client: AsyncSolrClient,
):
    """Test that adding field type without setting collection raises error."""
    from taiyo.schema import SolrFieldType, SolrFieldClass

    field_type = SolrFieldType(name="test", solr_class=SolrFieldClass.TEXT)

    with pytest.raises(ValueError, match="collection needs to be specified"):
        await async_solr_client.add_field_type(field_type)


def test_sync_add_field_without_collection_raises(sync_solr_client: SolrClient):
    """Test that adding field without setting collection raises error."""
    from taiyo.schema import SolrField

    field = SolrField(name="test", type="string")

    with pytest.raises(ValueError, match="collection needs to be specified"):
        sync_solr_client.add_field(field)
