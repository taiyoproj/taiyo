import pytest
from taiyo import SolrClient, AsyncSolrClient, SolrDocument, SolrError
import asyncio
import httpx
import time

SOLR_URL = "http://localhost:8983/solr"
COLLECTION = "test_collection"

class Product(SolrDocument):
    id: str
    title: str
    category: str

def _solr_admin_url():
    return SOLR_URL.rstrip("/") + "/admin/collections"

def _create_collection():
    # Use httpx to create the collection if it doesn't exist
    params = {
        "action": "CREATE",
        "name": COLLECTION,
        "numShards": 1,
        "replicationFactor": 1,
        "wt": "json",
    }
    try:
        r = httpx.get(_solr_admin_url(), params=params, timeout=10)
        r.raise_for_status()
    except Exception as e:
        # If already exists, ignore error
        if r.status_code == 400 and "already exists" in r.text:
            return
        raise
    # Wait for Solr to finish creating the collection
    time.sleep(1)

def _delete_collection():
    params = {
        "action": "DELETE",
        "name": COLLECTION,
        "wt": "json",
    }
    try:
        r = httpx.get(_solr_admin_url(), params=params, timeout=10)
        r.raise_for_status()
    except Exception as e:
        # If already deleted, ignore error
        if r.status_code == 400 and "not found" in r.text:
            return
        raise
    time.sleep(1)

@pytest.fixture(scope="module", autouse=True)
def solr_collection():
    _create_collection()
    yield
    _delete_collection()

@pytest.fixture(scope="module")
def client():
    with SolrClient(SOLR_URL, COLLECTION) as c:
        yield c

@pytest.mark.asyncio
@pytest.fixture(scope="module")
async def async_client():
    async with AsyncSolrClient(SOLR_URL, COLLECTION) as c:
        yield c

def test_ping(client):
    assert client.ping() is True

@pytest.mark.asyncio
def test_async_ping(async_client):
    ok = asyncio.run(async_client.ping())
    assert ok is True

def test_add_and_search(client):
    doc = Product(id="1", title="Test Product", category="books")
    client.add(doc)
    client.commit()
    res = client.search("id:1", document_model=Product)
    assert res.num_found >= 1
    found = any(d.id == "1" for d in res.docs)
    assert found

def test_delete(client):
    client.delete(ids=["1"])
    client.commit()
    res = client.search("id:1", document_model=Product)
    assert res.num_found == 0

@pytest.mark.asyncio
def test_async_add_and_search(async_client):
    doc = Product(id="2", title="Async Product", category="electronics")
    asyncio.run(async_client.add(doc))
    asyncio.run(async_client.commit())
    res = asyncio.run(async_client.search("id:2", document_model=Product))
    assert res.num_found >= 1
    found = any(d.id == "2" for d in res.docs)
    assert found

@pytest.mark.asyncio
def test_async_delete(async_client):
    asyncio.run(async_client.delete(ids=["2"]))
    asyncio.run(async_client.commit())
    res = asyncio.run(async_client.search("id:2", document_model=Product))
    assert res.num_found == 0

def test_error_handling(client):
    with pytest.raises(SolrError):
        client.search("invalid:::query[]")
