# Overview

Taiyo provides two client implementations for interacting with Apache Solr: a synchronous client (`SolrClient`) and an asynchronous client (`AsyncSolrClient`). Both share the same API surface with the only difference being that async methods must be awaited.

## Client Setup

=== "Sync"

    ```python
    from taiyo import SolrClient

    with SolrClient("http://localhost:8983/solr") as client:
        client.set_collection("my_collection")
        results = client.search("*:*")
    ```

=== "Async"

    ```python
    from taiyo import AsyncSolrClient

    async with AsyncSolrClient("http://localhost:8983/solr") as client:
        client.set_collection("my_collection")
        results = await client.search("*:*")
    ```

### Additional Configurations

=== "Sync"

    ```python
    from taiyo import SolrClient

    client = SolrClient(
        base_url="http://localhost:8983/solr",
        timeout=30.0,              # Request timeout in seconds
        verify=True,               # SSL certificate verification
    )
    ```

=== "Async"

    ```python
    from taiyo import AsyncSolrClient

    client = AsyncSolrClient(
        base_url="http://localhost:8983/solr",
        timeout=30.0,              # Request timeout in seconds
        verify=True,               # SSL certificate verification
    )
    ```

### SSL Configuration

=== "Sync"

    ```python
    from taiyo import SolrClient

    client = SolrClient(
        "https://solr.example.com/solr",
        verify=False
    )

    client = SolrClient(
        "https://solr.example.com/solr",
        verify="/path/to/ca-bundle.crt"
    )
    ```

=== "Async"

    ```python
    from taiyo import AsyncSolrClient

    client = AsyncSolrClient(
        "https://solr.example.com/solr",
        verify=False
    )

    client = AsyncSolrClient(
        "https://solr.example.com/solr",
        verify="/path/to/ca-bundle.crt"
    )
    ```

### httpx Options

Pass any httpx client options:

=== "Sync"

    ```python
    import httpx
    from taiyo import SolrClient

    client = SolrClient(
        "http://localhost:8983/solr",
        timeout=30.0,
        limits=httpx.Limits(max_connections=100),
        http2=True,
        follow_redirects=True,
    )
    ```

=== "Async"

    ```python
    import httpx
    from taiyo import AsyncSolrClient

    client = AsyncSolrClient(
        "http://localhost:8983/solr",
        timeout=30.0,
        limits=httpx.AsyncLimits(max_connections=100),
        http2=True,
        follow_redirects=True,
    )
    ```

## Context Managers

Context managers ensure proper resource cleanup:

=== "Sync"

    ```python
    with SolrClient("http://localhost:8983/solr") as client:
        client.set_collection("my_collection")
        results = client.search("*:*")
    ```

=== "Async"

    ```python
    async with AsyncSolrClient("http://localhost:8983/solr") as client:
        client.set_collection("my_collection")
        results = await client.search("*:*")
    ```

### Manual Management

Manual cleanup without context managers:

=== "Sync"

    ```python
    client = SolrClient("http://localhost:8983/solr")
    try:
        results = client.search("*:*")
    finally:
        client.close()
    ```

=== "Async"

    ```python
    from taiyo import AsyncSolrClient


    async def main() -> None:
        client = AsyncSolrClient("http://localhost:8983/solr")
        try:
            results = await client.search("*:*")
        finally:
            await client.close()
    ```

## Setting the Collection

Most operations require an active collection:

=== "Sync"

    ```python
    from taiyo import SolrClient

    client = SolrClient("http://localhost:8983/solr")
    client.set_collection("my_collection")

    results = client.search("*:*")
    client.add(documents)
    client.add_field(field)
    ```

=== "Async"

    ```python
    from taiyo import AsyncSolrClient


    async def main() -> None:
        client = AsyncSolrClient("http://localhost:8983/solr")
        client.set_collection("my_collection")

        results = await client.search("*:*")
        await client.add(documents)
        await client.add_field(field)
    ```

### Switching Collections

You can change the active collection at any time:

=== "Sync"

    ```python
    client.set_collection("collection1")
    results1 = client.search("*:*")

    client.set_collection("collection2")
    results2 = client.search("*:*")
    ```

=== "Async"

    ```python
    client.set_collection("collection1")
    results1 = await client.search("*:*")

    client.set_collection("collection2")
    results2 = await client.search("*:*")
    ```

## Core Operations

### Ping

Check if Solr is reachable:


=== "Sync"

    ```python
    if client.ping():
        print("Solr is available")
    ```

=== "Async"

    ```python
    if await client.ping():
        print("Solr is available")
    ```

### Create Collection

Create a new collection:

=== "Sync"

    ```python
    client.create_collection(
        name="my_collection",
        num_shards=2,
        replication_factor=1,
        maxShardsPerNode=2,
        collection_configName="myconfig",
    )
    ```

=== "Async"

    ```python
    await client.create_collection(
        name="my_collection",
        num_shards=2,
        replication_factor=1,
        maxShardsPerNode=2,
        collection_configName="myconfig",
    )
    ```

### Delete Collection

Delete a collection:

=== "Sync"

    ```python
    client.delete_collection("my_collection")
    ```

=== "Async"

    ```python
    await client.delete_collection("my_collection")
    ```

## Document Operations

### Adding Documents

Add a single document:

=== "Sync"

    ```python
    from taiyo import SolrDocument

    doc = SolrDocument(
        title="Hello World",
        content="This is a test document"
    )

    client.add(doc, commit=True)
    ```

=== "Async"

    ```python
    from taiyo import AsyncSolrClient, SolrDocument


    async def main() -> None:
        client = AsyncSolrClient("http://localhost:8983/solr")
        doc = SolrDocument(
            title="Hello World",
            content="This is a test document"
        )
        await client.add(doc, commit=True)
    ```

Add multiple documents:

=== "Sync"

    ```python
    docs = [
        SolrDocument(title="First"),
        SolrDocument(title="Second"),
        SolrDocument(title="Third")
    ]

    client.add(docs, commit=True)
    ```

=== "Async"

    ```python
    from taiyo import AsyncSolrClient, SolrDocument


    async def main() -> None:
        client = AsyncSolrClient("http://localhost:8983/solr")
        docs = [
            SolrDocument(title="First"),
            SolrDocument(title="Second"),
            SolrDocument(title="Third")
        ]
        await client.add(docs, commit=True)
    ```

### Committing Changes

Commit pending changes explicitly:

=== "Sync"

    ```python
    client.add(doc, commit=False)
    client.commit()
    ```

=== "Async"

    ```python
    await client.add(doc, commit=False)
    await client.commit()
    ```

### Deleting Documents

Delete by ID:

=== "Sync"

    ```python
    client.delete(ids=["1", "2", "3"], commit=True)
    ```

=== "Async"

    ```python
    await client.delete(ids=["1", "2", "3"], commit=True)
    ```

Delete by query:

=== "Sync"

    ```python
    client.delete(query="status:archived", commit=True)
    ```

=== "Async"

    ```python
    await client.delete(query="status:archived", commit=True)
    ```

Delete all documents:

=== "Sync"

    ```python
    client.delete(query="*:*", commit=True)
    ```

=== "Async"

    ```python
    await client.delete(query="*:*", commit=True)
    ```

## Searching

### Basic Search

=== "Sync"

    ```python
    # Simple query string
    results = client.search("title:test")

    # With parameters
    results = client.search("*:*", rows=20, start=0)
    ```

=== "Async"

    ```python
    # Simple query string
    results = await client.search("title:test")

    # With parameters
    results = await client.search("*:*", rows=20, start=0)
    ```

### Using Query Parsers

=== "Sync"

    ```python
    from taiyo.parsers import StandardParser

    parser = StandardParser(
        query="laptop",
        query_operator="AND",
        default_field="content"
    )

    results = client.search(parser)
    ```

=== "Async"

    ```python
    from taiyo.parsers import StandardParser

    parser = StandardParser(
        query="laptop",
        query_operator="AND",
        default_field="content"
    )

    results = await client.search(parser)
    ```

### With Custom Document Models

=== "Sync"

    ```python
    from taiyo import SolrDocument

    class Product(SolrDocument):
        name: str
        price: float
        category: str

    results = client.search("*:*", document_model=Product)

    for product in results.docs:
        print(f"{product.name}: ${product.price}")
    ```

=== "Async"

    ```python
    from taiyo import SolrDocument

    class Product(SolrDocument):
        name: str
        price: float
        category: str

    results = await client.search("*:*", document_model=Product)

    for product in results.docs:
        print(f"{product.name}: ${product.price}")
    ```

## Schema Management

### Adding Field Types

=== "Sync"

    ```python
    from taiyo.schema import SolrFieldType, SolrFieldClass

    field_type = SolrFieldType(
        name="text_custom",
        solr_class=SolrFieldClass.TEXT,
        position_increment_gap=100
    )

    client.add_field_type(field_type)
    ```

=== "Async"

    ```python
    from taiyo.schema import SolrFieldType, SolrFieldClass

    field_type = SolrFieldType(
        name="text_custom",
        solr_class=SolrFieldClass.TEXT,
        position_increment_gap=100
    )

    await client.add_field_type(field_type)
    ```

### Adding Fields

=== "Sync"

    ```python
    from taiyo.schema import SolrField

    field = SolrField(
        name="custom_field",
        type="text_general",
        indexed=True,
        stored=True
    )

    client.add_field(field)
    ```

=== "Async"

    ```python
    from taiyo.schema import SolrField

    field = SolrField(
        name="custom_field",
        type="text_general",
        indexed=True,
        stored=True
    )

    await client.add_field(field)
    ```

### Adding Dynamic Fields

=== "Sync"

    ```python
    from taiyo.schema import SolrDynamicField

    dynamic_field = SolrDynamicField(
        name="*_txt",
        type="text_general",
        indexed=True,
        stored=True
    )

    client.add_dynamic_field(dynamic_field)
    ```

=== "Async"

    ```python
    from taiyo.schema import SolrDynamicField

    dynamic_field = SolrDynamicField(
        name="*_txt",
        type="text_general",
        indexed=True,
        stored=True
    )

    await client.add_dynamic_field(dynamic_field)
    ```

## Error Handling

Handle Solr errors gracefully:

=== "Sync"

    ```python
    from taiyo import SolrError

    try:
        results = client.search("invalid:query:[")
    except SolrError as e:
        print(f"Error: {e}")
        print(f"Status: {e.status_code}")
        print(f"Response: {e.response}")
    ```

=== "Async"

    ```python
    from taiyo import SolrError

    try:
        results = await client.search("invalid:query:[")
    except SolrError as e:
        print(f"Error: {e}")
        print(f"Status: {e.status_code}")
        print(f"Response: {e.response}")
    ```

Common error scenarios:

=== "Sync"

    ```python
    try:
        client.add(doc)
    except SolrError as e:
        if e.status_code == 400:
            print("Bad request - check document format")
        elif e.status_code == 404:
            print("Collection not found")
        elif e.status_code == 500:
            print("Solr server error")
    ```

=== "Async"

    ```python
    try:
        await client.add(doc)
    except SolrError as e:
        if e.status_code == 400:
            print("Bad request - check document format")
        elif e.status_code == 404:
            print("Collection not found")
        elif e.status_code == 500:
            print("Solr server error")
    ```

## Best Practices

### Use Context Managers

=== "Sync"

    ```python
    with SolrClient("http://localhost:8983/solr") as client:
        results = client.search("*:*")
    ```

=== "Async"

    ```python
    async with AsyncSolrClient("http://localhost:8983/solr") as client:
        results = await client.search("*:*")
    ```

### Set Collection Once

=== "Sync"

    ```python
    client = SolrClient("http://localhost:8983/solr")
    client.set_collection("my_collection")
    ```

=== "Async"

    ```python
    client = AsyncSolrClient("http://localhost:8983/solr")
    client.set_collection("my_collection")
    ```

### Batch Operations

=== "Sync"

    ```python
    docs = [SolrDocument(title=f"Document {i}") for i in range(1000)]
    client.add(docs, commit=True)
    ```

=== "Async"

    ```python
    docs = [SolrDocument(title=f"Document {i}") for i in range(1000)]
    await client.add(docs, commit=True)
    ```

Avoid individual operations in loops:

=== "Sync"

    ```python
    for i in range(1000):
        doc = SolrDocument(title=f"Document {i}")
        client.add(doc, commit=True)
    ```

=== "Async"

    ```python
    for i in range(1000):
        doc = SolrDocument(title=f"Document {i}")
        await client.add(doc, commit=True)
    ```

### Commit Strategy

For bulk indexing:

=== "Sync"

    ```python
    for batch in batches:
        client.add(batch, commit=False)
    client.commit()
    ```

=== "Async"

    ```python
    for batch in batches:
        await client.add(batch, commit=False)
    await client.commit()
    ```

For real-time updates:

=== "Sync"

    ```python
    client.add(doc, commit=True)
    ```

=== "Async"

    ```python
    await client.add(doc, commit=True)
    ```

### Error Handling

=== "Sync"

    ```python
    try:
        client.create_collection("my_collection")
    except SolrError as e:
        if "already exists" in str(e).lower():
            # Collection exists, that's okay
            pass
        else:
            # Unexpected error
            raise
    ```

=== "Async"

    ```python
    try:
        await client.create_collection("my_collection")
    except SolrError as e:
        if "already exists" in str(e).lower():
            # Collection exists, that's okay
            pass
        else:
            # Unexpected error
            raise
    ```

## Performance Tips

### Connection Pooling

httpx automatically handles connection pooling. Configure limits:

=== "Sync"

    ```python
    client = SolrClient(
        "http://localhost:8983/solr",
        limits=httpx.Limits(
            max_keepalive_connections=10,
            max_connections=50,
            keepalive_expiry=30.0
        )
    )
    ```

=== "Async"

    ```python
    client = AsyncSolrClient(
        "http://localhost:8983/solr",
        limits=httpx.Limits(
            max_keepalive_connections=10,
            max_connections=50,
            keepalive_expiry=30.0
        )
    )
    ```

### Timeout Configuration

Configure timeouts based on operation type:

=== "Sync"

    ```python
    client = SolrClient("http://localhost:8983/solr", timeout=5.0)

    client = SolrClient("http://localhost:8983/solr", timeout=300.0)

    client = SolrClient("http://localhost:8983/solr", timeout=httpx.Timeout(
        connect=5.0,
        read=60.0,
        write=30.0,
        pool=10.0
    ))
    ```

=== "Async"

    ```python
    client = AsyncSolrClient("http://localhost:8983/solr", timeout=5.0)

    client = AsyncSolrClient("http://localhost:8983/solr", timeout=300.0)

    client = AsyncSolrClient("http://localhost:8983/solr", timeout=httpx.Timeout(
        connect=5.0,
        read=60.0,
        write=30.0,
        pool=10.0
    ))
    ```

### HTTP/2 Support

Enable HTTP/2 for better performance:

=== "Sync"

    ```python
    client = SolrClient(
        "http://localhost:8983/solr",
        http2=True
    )
    ```

=== "Async"

    ```python
    client = AsyncSolrClient(
        "http://localhost:8983/solr",
        http2=True
    )
    ```

## Next Steps

- Learn about [Authentication](auth.md) options
- Explore [Data Models](models.md) for type-safe documents
- Master [Query Parsers](parsers/query-parsers.md) for powerful searches
