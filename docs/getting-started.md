# Getting Started

This guide demonstrates basic usage of Taiyo with Apache Solr.

## Installation

```bash
pip install taiyo
```

Or using [uv](https://github.com/astral-sh/uv):

```bash
uv add taiyo
```

## Running Solr

Start a Solr instance using Docker:

```bash
docker run -p 8983:8983 solr:9 solr-precreate books
```

This command starts Solr on `http://localhost:8983` with a collection named `books`.

## Basic Usage

### Connect to Solr

```python
from taiyo import SolrClient

client = SolrClient("http://localhost:8983/solr")
client.set_collection("books")
```

### Add Documents

```python
from taiyo import SolrDocument

books = [
    SolrDocument(
        title="The Great Gatsby",
        author="F. Scott Fitzgerald"
    ),
    SolrDocument(
        title="1984",
        author="George Orwell"
    ),
]

client.add(books, commit=True)
```

### Search

```python
# Find all books
results = client.search("*:*")
print(f"Found {results.num_found} books")

for doc in results.docs:
    print(f"- {doc.title} by {doc.author}")
```

## Query Syntax

```python
# Search by field
results = client.search("author:Orwell")

# Search multiple fields
results = client.search("title:Gatsby OR author:Lee")

# Phrase search
results = client.search('title:"Great Gatsby"')

# Range search
results = client.search("year:[1940 TO 1950]")
```

## Document Models

Define custom document types using Pydantic:

```python
from taiyo import SolrDocument

class Book(SolrDocument):
    title: str
    author: str
    year: int | None = None

# Create books with validation
book = Book(
    title="1984",
    author="George Orwell",
    year=1949
)

client.add(book, commit=True)

# Search with typed results
results = client.search("*:*", document_model=Book)
for book in results.docs:
    print(f"{book.title} ({book.year})")
```

## Async Support

Use `AsyncSolrClient` for async/await:

```python
import asyncio
from taiyo import AsyncSolrClient

async def search_books():
    async with AsyncSolrClient("http://localhost:8983/solr") as client:
        client.set_collection("books")
        results = await client.search("author:Orwell")
        return results

asyncio.run(search_books())
```

## Working with Results

Search results have useful properties:

```python
results = client.search("author:Orwell")

print(f"Total matches: {results.num_found}")
print(f"Query took: {results.query_time}ms")

# Iterate through documents
for doc in results.docs:
    print(doc.title)
```

## Pagination

Get results page by page:

```python
# First page (0-9)
results = client.search("*:*", rows=10, start=0)

# Second page (10-19)
results = client.search("*:*", rows=10, start=10)

# Third page (20-29)
results = client.search("*:*", rows=10, start=20)
```

## Query Parsers

Use query parser objects for advanced queries:

```python
from taiyo.parsers import ExtendedDisMaxQueryParser

# Search across multiple fields
parser = ExtendedDisMaxQueryParser(
    query="science fiction",
    query_fields={"title": 3.0, "description": 1.0}  # Title is 3x more important
)

results = client.search(parser)
```

## Authentication

If your Solr requires authentication:

```python
from taiyo import SolrClient, BasicAuth

client = SolrClient(
    base_url="http://localhost:8983/solr",
    auth=BasicAuth("username", "password")
)
```

## See Also

- [Query Parsers](parsers/overview.md) - Advanced query syntax and parser configuration
- [Faceting](controlling-results/faceting.md) - Result aggregation and filtering
- [Highlighting](controlling-results/highlighting.md) - Text snippet highlighting  
- [Schema Management](schema.md) - Field and type definitions
- [Clients Guide](clients/overview.md) - Client configuration and authentication

## Best Practices

Use context managers to ensure proper connection cleanup:

```python
with SolrClient("http://localhost:8983/solr") as client:
    client.set_collection("books")
    results = client.search("*:*")
```

Commit changes to make them visible in search results:

```python
client.add(documents, commit=True)
# or
client.add(documents)
client.commit()
```

Handle exceptions appropriately:

```python
try:
    results = client.search("field:value")
except Exception as e:
    print(f"Search failed: {e}")
```
