import pytest
from typing import AsyncGenerator, Generator
import httpx
import pytest_asyncio
from taiyo import SolrClient, AsyncSolrClient
from taiyo.types import SolrDocument
from pydantic import Field


class MyDocument(SolrDocument):
    id: str
    title: str
    content: str
    category: str = Field(default="general")


@pytest.fixture
def base_url() -> str:
    return "http://localhost:8983/solr"


@pytest.fixture
def collection() -> str:
    return "test_collection"


@pytest_asyncio.fixture
async def mock_httpx_client(monkeypatch) -> AsyncGenerator[None, None]:
    """Mock httpx client to avoid real HTTP requests."""

    async def mock_request(*args, **kwargs) -> httpx.Response:
        # Default successful response
        return httpx.Response(
            200,
            json={
                "responseHeader": {"status": 0, "QTime": 5},
                "response": {"numFound": 0, "start": 0, "docs": []},
            },
        )

    with monkeypatch.context() as m:
        m.setattr(httpx.AsyncClient, "request", mock_request)
        yield


@pytest_asyncio.fixture
async def async_solr_client(
    base_url: str, mock_httpx_client
) -> AsyncGenerator[AsyncSolrClient, None]:
    async with AsyncSolrClient(base_url) as client:
        yield client


@pytest.fixture
def sync_solr_client(base_url: str) -> Generator[SolrClient, None, None]:
    with SolrClient(base_url) as client:
        yield client


@pytest.fixture
def sample_doc() -> MyDocument:
    return MyDocument(
        id="1",
        title="Test Document",
        content="This is a test document",
        category="news",
    )


@pytest.fixture
def sample_docs() -> list[MyDocument]:
    return [
        MyDocument(
            id="1",
            title="First Document",
            content="Content of first document",
            category="books",
        ),
        MyDocument(
            id="2",
            title="Second Document",
            content="Content of second document",
            category="electronics",
        ),
    ]
