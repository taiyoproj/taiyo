# Data Models

Taiyo uses Pydantic models for type-safe document handling. Documents provide validation, serialization, and IDE type support.

## SolrDocument Base Class

All documents in Taiyo inherit from `SolrDocument`, which is a Pydantic `BaseModel` with special configuration for Solr.

### Basic Usage

```python
from taiyo import SolrDocument

doc = SolrDocument(
    title="Example Document", content="This is the content", tags=["python", "solr"]
)
```

### Features

- Extra fields allowed (supports dynamic schemas)
- Runtime type validation
- JSON serialization
- IDE autocomplete and type checking

## Creating Custom Models

Define custom document models for type safety and validation:

### Basic Custom Model

```python
from taiyo import SolrDocument


class Article(SolrDocument):
    title: str
    author: str
    content: str
    published_date: str
    category: str
    tags: list[str] = []
    views: int = 0


article = Article(
    title="Getting Started with Solr",
    author="John Doe",
    content="Solr is a powerful search platform...",
    published_date="2025-01-01",
    category="tutorials",
    tags=["solr", "search", "tutorial"],
    views=1000,
)
```

### With Validation

```python
from taiyo import SolrDocument
from pydantic import Field, field_validator


class User(SolrDocument):
    username: str = Field(min_length=3, max_length=50)
    email: str = Field(pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    age: int = Field(ge=0, le=150)
    roles: list[str] = []

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v):
        assert v.isalnum(), "must be alphanumeric"
        return v
```

## Working with Documents

### Creating Documents

```python
# From keyword arguments
doc = Article(
    title="Title",
    author="Author",
    content="Content",
    published_date="2025-01-01",
    category="tech",
)

# From dictionary
data = {
    "title": "Title",
    "author": "Author",
    "content": "Content",
    "published_date": "2025-01-01",
    "category": "tech",
}
doc = Article(**data)

# From JSON
import json

json_str = '{"title": "Title", "author": "Author"}'
doc = Article(**json.loads(json_str))
```

### Aliases for Solr Fields

Map Solr field names to Python field names:

```python
from pydantic import Field


class Product(SolrDocument):
    """Product with field aliases."""

    name: str
    price: float
    product_id: str = Field(alias="sku")  # Maps to 'sku' in Solr
    in_stock_flag: bool = Field(alias="inStock")  # Maps to 'inStock'


# Use Python names in code
product = Product(name="Laptop", price=999.99, product_id="LAP-001", in_stock_flag=True)

# Solr gets: {"name": "Laptop", price: 999.99, "sku": "LAP-001", "inStock": true}
```

### Indexing Documents

```python
from taiyo import SolrClient

with SolrClient("http://localhost:8983/solr") as client:
    client.set_collection("articles")
    
    # Index single document
    article = Article(
        title="First Article",
        author="Jane Doe",
        content="Article content here",
        published_date="2025-01-01",
        category="tech"
    )
    client.add(article, commit=True)
    
    # Index multiple documents
    articles = [
        Article(title="First", author="Jane", ...),
        Article(title="Second", author="John", ...),
        Article(title="Third", author="Alice", ...)
    ]
    client.add(articles, commit=True)
```

### Searching with Custom Models

```python
# Search returns typed results
results = client.search("category:tech", document_model=Article)

# Access typed documents
for article in results.docs:
    print(f"{article.title} by {article.author}")
    print(f"Tags: {', '.join(article.tags)}")
    print(f"Views: {article.views}")
```

## SolrResponse

Search results are returned as `SolrResponse` objects with an optional generics type. Facet metadata is exposed via the structured `SolrFacetResult` model if configured, and MoreLikeThis payloads are parsed into `SolrMoreLikeThisResult` instances keyed by the source document ID.

### Response Structure

```python
from taiyo import SolrResponse

results: SolrResponse[Article] = client.search("*:*", document_model=Article)

# Core fields
print(f"Status: {results.status}")  # HTTP status code
print(f"Query time: {results.query_time}ms")  # Query execution time
print(f"Total found: {results.num_found}")  # Total matching docs
print(f"Start: {results.start}")  # Pagination start
print(f"Returned: {len(results.docs)}")  # Docs in this response

# Documents (typed)
for doc in results.docs:
    # doc is of type Article
    print(doc.title)
```

### Optional Response Fields

`SolrResponse.facets` is `Optional[SolrFacetResult]`. Each field facet is represented by a
`SolrFacetFieldResult` with typed buckets, and range facets return `SolrFacetRangeResult` data.
`SolrResponse.more_like_this` is an optional mapping of document IDs to `SolrMoreLikeThisResult`
models that expose typed similar-document matches.

```python
# Facet counts (if faceting enabled)
if results.facets:
    facets = results.facets

    category_facet = facets.fields.get("category")
    if category_facet:
        print("Category facets:")
        for bucket in category_facet.buckets:
            print(f"  {bucket.value}: {bucket.count}")

    # Query facets and JSON facets remain available via typed accessors
    print("Facet queries:", facets.queries)
    if facets.json_facets:
        print("JSON facet bucket count:", len(facets.json_facets.buckets))

# Highlighting (if highlighting enabled)
if results.highlighting:
    for doc_id, highlights in results.highlighting.items():
        print(f"Doc {doc_id} highlights:", highlights)

# MoreLikeThis matches (if MLT was requested)
if results.more_like_this:
    for doc_id, mlt_result in results.more_like_this.items():
        print(f"Doc {doc_id} has {mlt_result.num_found} similar docs")
        for similar in mlt_result.docs:
            print("  →", similar.title)

# Extra fields (grouped results, stats, etc.)
if results.extra:
    print("Extra data:", results.extra)
```

## Type Safety Benefits

### IDE Autocomplete

```python
article = Article(...)

# IDE knows all fields
article.title  # ✓ Autocomplete works
article.author  # ✓ Autocomplete works
article.invalid  # ✗ IDE shows error
```

### Type Checking

```python
# mypy and other type checkers work
article: Article = client.search("*:*", document_model=Article).docs[0]

# Type error caught
article.views = "not a number"  # ✗ Type checker error
```

### Runtime Validation

```python
from pydantic import ValidationError

try:
    # Invalid data raises error
    article = Article(
        title="Title",
        author="Author",
        views="not a number",  # ✗ Should be int
    )
except ValidationError as e:
    print(f"Validation error: {e}")
```

## Working with Dynamic Fields

Solr's dynamic fields are fully supported:

```python
# SolrDocument allows extra fields
doc = SolrDocument(
    title_en="English Title",  # Dynamic field *_en
    title_es="Título Español",  # Dynamic field *_es
    price_usd=99.99,  # Dynamic field *_usd
    tags_ss=["tag1", "tag2"],  # Dynamic field *_ss
)

client.add(doc)
```

## Best Practices

### Define Models for Known Schemas

```python
class Article(SolrDocument):
    title: str
    author: str
    content: str
```

Models provide type safety and validation. Use generic `SolrDocument` only for dynamic schemas.

### Use Optional for Nullable Fields

```python
from typing import Optional


class Document(SolrDocument):
    title: str  # Required
    description: Optional[str] = None  # Optional
    tags: list[str] = []  # Default empty list
```

### Document Your Models

```python
class Article(SolrDocument):
    """Article document for the blog system.

    Attributes:
        title: Article title (required, max 200 chars)
        author: Author name (required)
        content: Article body content
        category: Article category (one of: tech, science, arts)
        tags: List of tags for categorization
        published: Whether the article is published
    """

    title: str = Field(max_length=200, description="Article title")
    author: str = Field(description="Author name")
    content: str = Field(description="Article body")
    category: str = Field(description="Article category")
    tags: list[str] = Field(default_factory=list, description="Tags")
    published: bool = Field(default=False, description="Publication status")
```

## Next Steps

- Learn about [Schema Management](../indexing/schema.md) to define your Solr schema
- Explore [Query Parsers](../parsers/overview.md) for searching documents
- See [Clients](overview.md) for indexing and retrieving documents
