# Overview

Taiyo provides two client implementations for interacting with Apache Solr: a synchronous client (`SolrClient`) and an asynchronous client (`AsyncSolrClient`). Both share the same API surface with the only difference being that async methods must be awaited.

## Client Types

### SolrClient (Synchronous)

Use the synchronous client for:
- Scripts and command-line tools
- Synchronous web frameworks (Flask, Django)
- Applications without concurrency requirements
- Testing and development

```python
from taiyo import SolrClient

with SolrClient("http://localhost:8983/solr") as client:
    client.set_collection("my_collection")
    results = client.search("*:*")
```

### AsyncSolrClient (Asynchronous)

Use the asynchronous client for:
- Async web frameworks (FastAPI, Sanic, Starlette)
- High-concurrency applications
- Applications with concurrent Solr requests
- Microservices and API gateways

```python
from taiyo import AsyncSolrClient

async with AsyncSolrClient("http://localhost:8983/solr") as client:
    client.set_collection("my_collection")
    results = await client.search("*:*")
```

## Client Initialization

### Basic Initialization

```python
from taiyo import SolrClient, AsyncSolrClient

# Synchronous client
sync_client = SolrClient("http://localhost:8983/solr")

# Asynchronous client
async_client = AsyncSolrClient("http://localhost:8983/solr")
```

### With Configuration

```python
from taiyo import SolrClient

client = SolrClient(
    base_url="http://localhost:8983/solr",
    timeout=30.0,              # Request timeout in seconds
    verify=True,               # SSL certificate verification
)
```

### SSL Configuration

```python
client = SolrClient(
    "https://solr.example.com/solr",
    verify=False
)

client = SolrClient(
    "https://solr.example.com/solr",
    verify="/path/to/ca-bundle.crt"
)
```

### Additional Client Options

Pass any httpx client options:

```python
client = SolrClient(
    "http://localhost:8983/solr",
    timeout=30.0,
    limits=httpx.Limits(max_connections=100),
    http2=True,
    follow_redirects=True,
)
```

## Context Managers

Context managers ensure proper resource cleanup:

### Synchronous

```python
with SolrClient("http://localhost:8983/solr") as client:
    client.set_collection("my_collection")
    results = client.search("*:*")
```

### Asynchronous

```python
async with AsyncSolrClient("http://localhost:8983/solr") as client:
    client.set_collection("my_collection")
    results = await client.search("*:*")
```

### Manual Management

Manual cleanup without context managers:

```python
# Sync
client = SolrClient("http://localhost:8983/solr")
try:
    results = client.search("*:*")
finally:
    client.close()

# Async
client = AsyncSolrClient("http://localhost:8983/solr")
try:
    results = await client.search("*:*")
finally:
    await client.close()
```

## Setting the Collection

Most operations require an active collection:

```python
client.set_collection("my_collection")

results = client.search("*:*")
client.add(documents)
client.add_field(field)
```

### Switching Collections

You can change the active collection at any time:

```python
client.set_collection("collection1")
results1 = client.search("*:*")

client.set_collection("collection2")
results2 = client.search("*:*")
```

## Core Operations

### Ping

Check if Solr is reachable:

```python
# Sync
if client.ping():
    print("Solr is available")

# Async
if await client.ping():
    print("Solr is available")
```

### Create Collection

Create a new collection:

```python
# Sync
client.create_collection(
    name="my_collection",
    num_shards=2,
    replication_factor=1
)

# Async
await client.create_collection(
    name="my_collection",
    num_shards=2,
    replication_factor=1,
    maxShardsPerNode=2,
    collection_configName="myconfig"
)
```

### Delete Collection

Delete a collection:

```python
# Sync
client.delete_collection("my_collection")

# Async
await client.delete_collection("my_collection")
```

## Document Operations

### Adding Documents

Add a single document:

```python
from taiyo import SolrDocument

doc = SolrDocument(
    title="Hello World",
    content="This is a test document"
)

# Sync
client.add(doc, commit=True)

# Async
await client.add(doc, commit=True)
```

Add multiple documents:

```python
docs = [
    SolrDocument(title="First"),
    SolrDocument(title="Second"),
    SolrDocument(title="Third")
]

# Sync
client.add(docs, commit=True)

# Async
await client.add(docs, commit=True)
```

### Committing Changes

Commit pending changes explicitly:

```python
# Sync
client.add(doc, commit=False)
client.commit()

# Async
await client.add(doc, commit=False)
await client.commit()
```

### Deleting Documents

Delete by ID:

```python
# Sync
client.delete(ids=["1", "2", "3"], commit=True)

# Async
await client.delete(ids=["1", "2", "3"], commit=True)
```

Delete by query:

```python
# Sync
client.delete(query="status:archived", commit=True)

# Async
await client.delete(query="status:archived", commit=True)
```

Delete all documents:

```python
# Sync
client.delete(query="*:*", commit=True)

# Async
await client.delete(query="*:*", commit=True)
```

## Searching

### Basic Search

```python
# Simple query string
results = client.search("title:test")

# With parameters
results = client.search("*:*", rows=20, start=0)
```

### Using Query Parsers

```python
from taiyo.parsers import StandardParser

parser = StandardParser(
    query="laptop",
    query_operator="AND",
    default_field="content"
)

results = client.search(parser)
```

### With Custom Document Models

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

## Schema Management

### Adding Field Types

```python
from taiyo.schema import SolrFieldType, SolrFieldClass

field_type = SolrFieldType(
    name="text_custom",
    solr_class=SolrFieldClass.TEXT,
    position_increment_gap=100
)

# Sync
client.add_field_type(field_type)

# Async
await client.add_field_type(field_type)
```

### Adding Fields

```python
from taiyo.schema import SolrField

field = SolrField(
    name="custom_field",
    type="text_general",
    indexed=True,
    stored=True
)

# Sync
client.add_field(field)

# Async
await client.add_field(field)
```

### Adding Dynamic Fields

```python
from taiyo.schema import SolrDynamicField

dynamic_field = SolrDynamicField(
    name="*_txt",
    type="text_general",
    indexed=True,
    stored=True
)

# Sync
client.add_dynamic_field(dynamic_field)

# Async
await client.add_dynamic_field(dynamic_field)
```

## Custom Headers

Set custom headers for all requests:

```python
client.set_header("X-Custom-Header", "value")
```

## Error Handling

Handle Solr errors gracefully:

```python
from taiyo import SolrError

try:
    results = client.search("invalid:query:[")
except SolrError as e:
    print(f"Error: {e}")
    print(f"Status: {e.status_code}")
    print(f"Response: {e.response}")
```

Common error scenarios:

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

## Best Practices

### Use Context Managers

```python
with SolrClient("http://localhost:8983/solr") as client:
    results = client.search("*:*")
```

### Set Collection Once

```python
client = SolrClient("http://localhost:8983/solr")
client.set_collection("my_collection")
```

### Batch Operations

```python
docs = [SolrDocument(title=f"Document {i}") for i in range(1000)]
client.add(docs, commit=True)
```

Avoid individual operations in loops:

```python
for i in range(1000):
    doc = SolrDocument(title=f"Document {i}")
    client.add(doc, commit=True)
```

### Commit Strategy

For bulk indexing:

```python
for batch in batches:
    client.add(batch, commit=False)
client.commit()
```

For real-time updates:

```python
client.add(doc, commit=True)
```

### Error Handling

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

## Configuration Examples

### Production Configuration

```python
from taiyo import SolrClient, BasicAuth
import httpx

client = SolrClient(
    base_url="https://solr.production.com/solr",
    auth=BasicAuth("username", "password"),
    timeout=60.0,
    verify=True,
    limits=httpx.Limits(
        max_keepalive_connections=20,
        max_connections=100
    ),
    http2=True
)
```

### Development Configuration

```python
client = SolrClient(
    base_url="http://localhost:8983/solr",
    timeout=10.0,
    verify=False
)
```

### Load Balancing

```python
nodes = [
    "http://solr1.example.com/solr",
    "http://solr2.example.com/solr",
    "http://solr3.example.com/solr"
]

import itertools
node_cycle = itertools.cycle(nodes)

def get_client():
    return SolrClient(next(node_cycle))

with get_client() as client:
    client.set_collection("my_collection")
    results = client.search("*:*")
```

## Performance Tips

### Connection Pooling

httpx automatically handles connection pooling. Configure limits:

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

### Timeout Configuration

Configure timeouts based on operation type:

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

### HTTP/2 Support

Enable HTTP/2 for better performance:

```python
client = SolrClient(
    "http://localhost:8983/solr",
    http2=True
)
```

## Next Steps

- Learn about [Authentication](auth.md) options
- Explore [Data Models](models.md) for type-safe documents
- Master [Query Parsers](parsers/query-parsers.md) for powerful searches
