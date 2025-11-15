# Clients: sync vs async

Taiyo offers both synchronous and asynchronous clients with an identical public API:

- `SolrClient` — blocking, built on `httpx.Client`
- `AsyncSolrClient` — non-blocking, built on `httpx.AsyncClient`

Both clients share the same methods: `ping()`, `add()`, `delete()`, `commit()`, and `search()`.

## Synchronous client

```python
from taiyo import SolrClient

with SolrClient("http://localhost:8983/solr", "products") as client:
    ok = client.ping()
    client.add({"id": "1", "title": "Mouse"})  # dicts are allowed but Pydantic is recommended
    client.commit()

    res = client.search("*:*")
    print(res.num_found)
```

### Notes
- Context manager closes the underlying `httpx.Client`.
- `timeout` and any extra `httpx` options can be passed via `**client_options`.

```python
client = SolrClient(
    base_url="http://localhost:8983/solr",
    collection="products",
    timeout=20.0,
    verify=False,  # passed to httpx
)
```

## Asynchronous client

```python
import asyncio
from taiyo import AsyncSolrClient

async def main():
    async with AsyncSolrClient("http://localhost:8983/solr", "products") as client:
        ok = await client.ping()
        await client.add({"id": "2", "title": "Keyboard"})
        await client.commit()

        res = await client.search("*:*")
        print(res.num_found)

asyncio.run(main())
```

### Notes
- Must be used in an async context; all methods are `await`able.
- Under the hood uses `httpx.AsyncClient`.

## Adding and deleting documents

Both clients accept either a single `SolrDocument` instance or a list of them. They internally serialize via `model_dump(exclude_unset=True)`.

```python
from taiyo import SolrClient, SolrDocument

class Product(SolrDocument):
    id: str
    title: str

with SolrClient("http://localhost:8983/solr", "products") as client:
    client.add(Product(id="100", title="Desk"))
    client.add([
        Product(id="101", title="Chair"),
        Product(id="102", title="Lamp"),
    ])
    client.commit()

    client.delete(query="title:Desk")
    client.delete(ids=["101", "102"])  # commit defaults to true
```

Async is identical but with `await`.

## Searching and mapping to models

```python
res = client.search("title:mouse", document_model=Product)
print(res.status, res.query_time)
for doc in res.docs:
    reveal_type = type(doc)  # Product
```

If you don't pass `document_model`, results map to the base `SolrDocument`.
