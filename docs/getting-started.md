# Getting started

This guide covers minimal setup to connect to Solr, index documents, and run searches with Taiyo.

## Requirements

- Python 3.11+
- A running Solr instance (e.g., http://localhost:8983/solr)

## Installation

```bash
pip install taiyo
```

## Define your document model

Documents extend `SolrDocument` (a Pydantic model). Extra fields are allowed by default.

```python
from taiyo import SolrDocument
from pydantic import Field

class Product(SolrDocument):
    id: str
    title: str
    category: str = Field(default="general")
```

## Create a client (sync)

```python
from taiyo import SolrClient

with SolrClient("http://localhost:8983/solr", "products") as client:
    assert client.ping() is True
```

## Create a client (async)

```python
import asyncio
from taiyo import AsyncSolrClient

async def main():
    async with AsyncSolrClient("http://localhost:8983/solr", "products") as client:
        ok = await client.ping()
        print("Solr up?", ok)

asyncio.run(main())
```

## Index documents

```python
from taiyo import SolrClient

with SolrClient("http://localhost:8983/solr", "products") as client:
    client.add(Product(id="1", title="Wireless Mouse", category="electronics"))
    client.add([
        Product(id="2", title="Gaming Keyboard", category="electronics"),
        Product(id="3", title="Coffee Beans", category="grocery"),
    ])
    client.commit()
```

## Search

```py
with SolrClient("http://localhost:8983/solr", "products") as client:
    res = client.search("title:mouse", document_model=Product)
    print(res.num_found)
    for d in res.docs:
        print(d.id, d.title)
```

## Errors

All API errors raise `SolrError` with optional HTTP status and parsed response payload.

```python
from taiyo import SolrError
try:
    client.search("invalid:query]")
except SolrError as e:
    print(e.status_code, e.response)
```
