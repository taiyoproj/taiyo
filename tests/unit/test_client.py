"""Tests for the SolrClient and AsyncSolrClient classes."""

import pytest
import httpx
from httpx import Response
from taiyo import SolrClient, AsyncSolrClient, SolrError
from tests.unit.conftest import MyDocument
from tests.unit.mocks import (
    mock_search_response,
    mock_update_response,
    mock_delete_response,
    mock_solr_error,
    mock_facet_response,
    mock_highlight_response,
)


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

    monkeypatch.setattr(async_solr_client.client, "request", mock_request)
    assert await async_solr_client.ping() is True


@pytest.mark.asyncio
async def test_async_ping_failure(async_solr_client: AsyncSolrClient, monkeypatch):
    """Test failed ping response."""

    async def mock_request(*args, **kwargs):
        request = httpx.Request("GET", "http://localhost:8983")
        response = Response(500, json={"status": "ERROR"})
        response._request = request
        return response

    monkeypatch.setattr(async_solr_client.client, "request", mock_request)
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

    monkeypatch.setattr(async_solr_client.client, "request", mock_request)
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

    monkeypatch.setattr(async_solr_client.client, "request", mock_request)
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

    monkeypatch.setattr(async_solr_client.client, "request", mock_request)
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

    monkeypatch.setattr(async_solr_client.client, "request", mock_request)
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

    monkeypatch.setattr(async_solr_client.client, "request", mock_request)
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

    monkeypatch.setattr(async_solr_client.client, "request", mock_request)
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

    monkeypatch.setattr(async_solr_client.client, "request", mock_request)
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

    monkeypatch.setattr(async_solr_client.client, "request", mock_request)

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

    monkeypatch.setattr(sync_solr_client.client, "request", mock_request)
    assert sync_solr_client.ping() is True


def test_sync_ping_failure(sync_solr_client: SolrClient, monkeypatch):
    """Test failed ping response."""

    def mock_request(*args, **kwargs):
        request = httpx.Request("GET", "http://localhost:8983")
        response = Response(500, json={"status": "ERROR"})
        response._request = request
        return response

    monkeypatch.setattr(sync_solr_client.client, "request", mock_request)
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

    monkeypatch.setattr(sync_solr_client.client, "request", mock_request)
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

    monkeypatch.setattr(sync_solr_client.client, "request", mock_request)
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

    monkeypatch.setattr(sync_solr_client.client, "request", mock_request)
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

    monkeypatch.setattr(sync_solr_client.client, "request", mock_request)
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

    monkeypatch.setattr(sync_solr_client.client, "request", mock_request)
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

    monkeypatch.setattr(sync_solr_client.client, "request", mock_request)
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

    monkeypatch.setattr(sync_solr_client.client, "request", mock_request)
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

    monkeypatch.setattr(sync_solr_client.client, "request", mock_request)

    with pytest.raises(SolrError) as exc_info:
        sync_solr_client.search("invalid:query]")

    assert exc_info.value.status_code == 400
    assert exc_info.value.response["error"]["message"] == error_message
