# Taiyo

A modern Python client for Apache Solr with a clean, type-safe API, rich query builders, and first-class sync/async support.

- Simple client setup with pluggable authentication (Basic, Bearer)
- Sync (`SolrClient`) and Async (`AsyncSolrClient`) clients with the same API
- Strongly-typed documents via Pydantic (`SolrDocument`)
- Search response model (`SolrResponse`) with facets and highlighting support
- Composable query parsers: sparse (lucene, dismax/edismax), dense (KNN, vectorSimilarity), spatial (bbox, geofilt)
- Feature configs (faceting, grouping, highlighting, more-like-this) as Pydantic models

## Quick install

```bash
pip install taiyo
```

If installing from source:

```bash
git clone https://github.com/KengoA/taiyo
cd taiyo
pip install -e .
```

## Quickstart

```python
from taiyo import SolrClient, SolrDocument

class Product(SolrDocument):
    id: str
    title: str
    category: str

with SolrClient("http://localhost:8983/solr", "products") as client:
    # Ping
    assert client.ping()

    # Index
    client.add(Product(id="1", title="Wireless Mouse", category="electronics"))
    client.commit()

    # Search (simple query string)
    res = client.search("title:mouse", document_model=Product)
    for doc in res.docs:
        print(doc.id, doc.title)
```


Next steps

- Getting started: environment, minimal examples
- Clients: sync vs async and authentication
- Queries: parsers, mixins, and feature configs
- Recipes: common tasks and patterns

