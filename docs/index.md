# Taiyo

Taiyo is a Python client for Apache Solr built with httpx and Pydantic.

The library provides a type-safe interface for interacting with Apache Solr, supporting both synchronous and asynchronous operations. It includes comprehensive support for Solr's query parsers, schema management, and vector search capabilities.

## Features

- Synchronous and asynchronous client implementations
- Type safety with Pydantic for runtime validation and IDE support
- Full support for Solr query parsers (standard, dismax, edismax, and specialized parsers)
- Native support for KNN, dense vector similarity, and spatial queries
- Programmatic schema definition and management
- Authentication via Basic Auth and Bearer Token
- HTTP/2 support through httpx
- Comprehensive type annotations

## Quick Start

### Installation

```bash
pip install taiyo
```

Or using [uv](https://github.com/astral-sh/uv):

```bash
uv add taiyo
```

### Basic Usage

```python
from taiyo import SolrClient, SolrDocument

# Create a synchronous client
with SolrClient("http://localhost:8983/solr") as client:
    client.set_collection("my_collection")
    
    # Search documents
    results = client.search("*:*")
    print(f"Found {results.num_found} documents")
    
    # Add documents
    doc = SolrDocument(title="Hello Solr", content="My first document")
    client.add(doc)
    client.commit()
```

### Async Usage

```python
from taiyo import AsyncSolrClient, SolrDocument

async def main():
    async with AsyncSolrClient("http://localhost:8983/solr") as client:
        client.set_collection("my_collection")
        
        # Search documents
        results = await client.search("*:*")
        print(f"Found {results.num_found} documents")
        
        # Add documents
        doc = SolrDocument(title="Hello Solr")
        await client.add(doc)
        await client.commit()
```

## Use Cases

- Full-text search applications with faceting and highlighting
- Recommendation systems using vector similarity for semantic search
- Analytics using Solr's aggregation and faceting capabilities
- Content management with document indexing and rich metadata
- Geospatial applications with location-based search and filtering

## Documentation

- [Getting Started](getting-started.md) - Basic setup and first queries
- [Clients](clients/overview.md) - Client configuration, authentication, and usage patterns
- [Indexing](indexing/overview.md) - Document indexing and batch operations
- [Query Parsers](parsers/overview.md) - Query parser reference and examples
- [Controlling Results](controlling-results/faceting.md) - Faceting, grouping, and highlighting

## Requirements

- Python 3.11+
- Apache Solr 8.0+

## Community & Support

- **GitHub**: [KengoA/taiyo](https://github.com/KengoA/taiyo)
- **Issues**: Report bugs or request features on GitHub Issues

## License

Taiyo is licensed under the MIT License. See LICENSE for details.
