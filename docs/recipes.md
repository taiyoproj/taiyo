# Recipes

A few common patterns end-to-end.

## Faceted search with highlighting

```python
from taiyo import (
    SolrClient, SolrDocument,
    StandardParser,
    FacetParamsConfig, HighlightParamsConfig,
)

class Article(SolrDocument):
    id: str
    title: str
    body: str

with SolrClient("http://localhost:8983/solr", "articles") as client:
    parser = StandardParser(
        query="wireless mouse",
        facet=FacetParamsConfig(fields=["category"], mincount=1),
        highlight=HighlightParamsConfig(fields=["title","body"], encoder="html"),
        rows=5,
    )
    res = client.search(parser, document_model=Article)
    print(res.facet_counts)
    print(res.highlighting)
```

## Dense vector search

```python
from taiyo import SolrClient, KNNQueryParser

with SolrClient("http://localhost:8983/solr", "products") as client:
    parser = KNNQueryParser(
        field="vector",
        vector=[0.1, 0.2, 0.3],
        top_k=10,
        pre_filter=["inStock:true"],
    )
    res = client.search(parser)
```

## Spatial filtering

```python
from taiyo import SolrClient, GeoFilterQueryParser

with SolrClient("http://localhost:8983/solr", "stores") as client:
    parser = GeoFilterQueryParser(
        spatial_field="store",
        center_point=[45.15, -93.85],
        radial_distance=10,
        score="distance",
    )
    res = client.search(parser)
```

## Async batch indexing

```python
import asyncio
from taiyo import AsyncSolrClient, SolrDocument

class Product(SolrDocument):
    id: str
    title: str

async def main():
    docs = [Product(id=str(i), title=f"Item {i}") for i in range(100)]
    async with AsyncSolrClient("http://localhost:8983/solr", "products") as client:
        await client.add(docs)
        await client.commit()

asyncio.run(main())
```
