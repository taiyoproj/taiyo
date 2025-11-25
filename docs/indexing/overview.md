# Overview

Indexing is the process of adding documents to Solr for retrieval. Taiyo provides both synchronous and asynchronous clients for efficient document indexing.

## Core Concepts

### Documents

Documents are the primary unit of data in Solr. Each document contains fields with values that can be indexed, stored, and searched.

### Collections

A collection is a logical index in Solr. Documents are indexed into collections, which can be distributed across multiple nodes for scalability.

### Commits

Commits make indexed documents visible for search. Taiyo supports:

- Immediate commits (`commit=True`)
- Manual commits (`client.commit()`)
- Batch commits for performance

## Indexing Approaches

### Single Document

```python
from taiyo import SolrClient, SolrDocument

with SolrClient("http://localhost:8983/solr") as client:
    client.set_collection("my_collection")

    doc = SolrDocument(title="Document Title", content="Document content")

    client.add(doc, commit=True)
```

### Batch Indexing
=== "Sync"

    ```python
    from taiyo import SolrClient

    with SolrClient("http://localhost:8983/solr") as client:
        client.set_collection("my_collection")
        docs = [
            SolrDocument(title=f"Document {i}", content=f"Content {i}")
            for i in range(1000)
        ]

        client.add(docs, commit=False)
        client.commit()
    ```

=== "Async"

    ```python
    import asyncio
    from taiyo import AsyncSolrClient

    async with AsyncSolrClient("http://localhost:8983/solr") as client:
        client.set_collection("my_collection")
        
        # Split into batches and process concurrently
        batch_size = 100
        all_docs = [SolrDocument(title=f"Doc {i}") for i in range(1000)]
        batches = [all_docs[i:i + batch_size] for i in range(0, len(all_docs), batch_size)]
        
        # Index all batches concurrently
        await asyncio.gather(*[client.add(batch, commit=False) for batch in batches])
        await client.commit()
    ```

### Commit Strategy

Commits are expensive operations. For bulk indexing:

```python
for batch in batches:
    client.add(batch, commit=False)

client.commit()
```

For real-time updates:

```python
client.add(doc, commit=True)
```

### Async for Concurrency

Use async clients when indexing from multiple sources concurrently:

```python
import asyncio


async def index_source(client, source):
    docs = await fetch_from_source(source)
    await client.add(docs, commit=False)


async with AsyncSolrClient(url) as client:
    client.set_collection("my_collection")

    await asyncio.gather(
        index_source(client, "source1"),
        index_source(client, "source2"),
        index_source(client, "source3"),
    )

    await client.commit()
```

## Error Handling

```python
from taiyo import SolrError

try:
    client.add(docs, commit=True)
except SolrError as e:
    print(f"Indexing failed: {e}")
    print(f"Status: {e.status_code}")
```

## See Also

- [Examples](examples.md) - Complete indexing examples with real datasets
- [Schema Management](schema.md) - Define and manage your Solr schema
- [Client Overview](../clients/overview.md) - Client configuration and usage
