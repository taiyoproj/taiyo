# Overview

Taiyo supports Apache Solr's query parsers with a type-safe Python API.

Query parsers serialize into Solr HTTP query parameters when called with the `.build()` method, returning Python dictionaries that are compatible with any Solr client or HTTP library.

## Available Parsers

### Sparse/Text Query Parsers

For traditional keyword-based search:

- **[StandardParser](sparse.md#standardparser)** (`lucene`): Solr's default Lucene query parser
- **[DisMaxQueryParser](sparse.md#dismaxqueryparser)** (`dismax`): DisjunctionMax parser for simple queries
- **[ExtendedDisMaxQueryParser](sparse.md#extendeddismaxqueryparser)** (`edismax`): Extended DisMax with advanced features

### Dense/Vector Query Parsers

For semantic and vector similarity search:

- **[KNNQueryParser](dense.md#knnqueryparser)** (`knn`): K-Nearest Neighbors search
- **[KNNTextToVectorQueryParser](dense.md#knntexttovectorqueryparser)** (`knn_text_to_vector`): Text-to-vector KNN search
- **[VectorSimilarityQueryParser](dense.md#vectorsimilarityqueryparser)** (`vectorSimilarity`): Vector similarity with thresholds

### Spatial Query Parsers

For location-based search:

- **[GeoFilterQueryParser](spatial.md#geofilterqueryparser)** (`geofilt`): Radial/circle spatial filter
- **[BBoxQueryParser](spatial.md#bboxqueryparser)** (`bbox`): Bounding box spatial filter


### Terms Query Parser

For efficient multi-value term matching (IDs, tags, categories):

- **[TermsQueryParser](terms.md#termsqueryparser)** (`terms`): Efficiently matches documents where a field contains any of a provided list of terms. Supports custom separators, multiple query methods, docValues, and appends the terms filter to any additional filters.

#### Example

```python
from taiyo.parsers import TermsQueryParser

parser = TermsQueryParser(
    field="tags",
    terms=["python", "java", "rust"],
    query="inStock:true",
    filters=["category:books"],
    rows=10,
    sort="price asc",
)

results = client.search(parser)
for doc in results.docs:
    print(doc.product_id, doc.name)
```

- Supports method chaining for faceting, grouping, highlighting, and more.
- See [TermsQueryParser documentation](terms.md#termsqueryparser) for full API, usage, and integration test coverage.

## Quick Start

### Basic Query String

The simplest way to query Solr:

```python
from taiyo import SolrClient

with SolrClient("http://localhost:8983/solr") as client:
    client.set_collection("my_collection")
    results = client.search("title:python")
```

### Using Query Parsers

For more control, use query parser objects:

```python
from taiyo.parsers import StandardParser

parser = StandardParser(
    query="python programming", query_operator="AND", default_field="content"
)

results = client.search(parser)
```

### Using .build() for Compatibility

Get query parameters as a dictionary for use with other Solr clients:

```python
from taiyo.parsers import StandardParser

parser = StandardParser(
    query="python programming",
    query_operator="AND",
    filter_queries=["year:[2020 TO *]"],
    rows=10,
)

# Build query parameters as dictionary
params = parser.build()
# {'q': 'python programming', 'q.op': 'AND', 'fq': ['year:[2020 TO *]'], 'rows': 10, 'defType': 'lucene'}

# Use with httpx or any HTTP library
import httpx

response = httpx.get("http://localhost:8983/solr/my_collection/select", params=params)
```

## Common Patterns

### Chaining with Configs

All parsers support method chaining with configuration objects:

```python
from taiyo.parsers import StandardParser

parser = (
    StandardParser(query="laptop")
    .facet(fields=["category", "brand"], mincount=1)
    .group(by="brand", limit=3)
    .highlight(fields=["title", "description"], fragment_size=150)
)

results = client.search(parser)
```

### Passing Configs in Constructor

Alternatively, pass configs during initialization:

```python
from taiyo import StandardParser
from taiyo.params import FacetParamsConfig, GroupParamsConfig

parser = StandardParser(
    query="laptop",
    configs=[
        FacetParamsConfig(fields=["category", "brand"], mincount=1),
        GroupParamsConfig(by="brand", limit=3),
    ],
)
```

## Parser Components

### Common Parameters

All parsers inherit common search parameters:

```python
parser = StandardParser(
    query="search term",
    rows=10,
    start=0,
    field_list=["id", "title"],
    sort="score desc",
    filters=["status:active", "category:tech"],
)
```

### Result Configs

Add faceting, grouping, highlighting, and more-like-this:

```python
parser.facet(field_list=["category", "author"], mincount=1, limit=10)

parser.group(by="author", limit=3, ngroups=True)

parser.highlight(
    field_list=["title", "content"], fragment_size=150, snippets_per_field=3
)

parser.more_like_this(field_list=["content"], min_term_freq=2, max_query_terms=25)
```

## Building Queries

### Simple Queries

```python
# Text search
parser = StandardParser(query="python")

# Field-specific
parser = StandardParser(query="title:python")

# Boolean
parser = StandardParser(query="python AND programming")

# Phrase
parser = StandardParser(query='"machine learning"')
```

### Complex Queries

```python
# Multiple criteria with boosting
parser = ExtendedDisMaxQueryParser(
    query="python OR java",
    query_fields={"title": 5.0, "content": 1.0, "tags": 2.0},
    boost_queries=["featured:true^10", "recent:true^5"],
)

# With filters
parser = StandardParser(
    query="*:*",
    filters=[
        "status:published",
        "category:programming",
        "published_date:[NOW-1YEAR TO NOW]",
    ],
)

# With faceting and grouping
parser = (
    DisMaxQueryParser(query="laptop")
    .facet(field_list=["brand", "price_range"], mincount=1)
    .group(by="brand", limit=3, sort="price asc")
)
```

## Response Handling

### Basic Response

```python
results = client.search(parser)

print(f"Found {results.num_found} documents")
print(f"Query took {results.query_time}ms")

for doc in results.docs:
    print(f"- {doc.title}")
```

### With Facets

```python
results = client.search(parser.facet(fields=["category"]))

if results.facets:
    category_facet = results.facets.fields.get("category")
    categories = (
        [bucket.value for bucket in category_facet.buckets] if category_facet else []
    )
    print("Categories:", categories)
```

### With Highlighting

```python
results = client.search(parser.highlight(fields=["content"]))

if results.highlighting:
    for doc_id, highlights in results.highlighting.items():
        print(f"Doc {doc_id}:")
        for field, snippets in highlights.items():
            print(f"  {field}: {snippets}")
```

### With Grouping

```python
results = client.search(parser.group(by="category"))

if results.extra and "grouped" in results.extra:
    for category, group_data in results.extra["grouped"].items():
        print(f"{category}: {group_data}")
```

## Performance Tips

### Use Filter Queries for Caching

Filter queries are cached separately:

```python
parser = StandardParser(
    query="python", filters=["status:active", "category:programming"]
)
```

### Limit Returned Fields

```python
parser = StandardParser(query="python", field_list=["id", "title", "score"])
```

### Use Pagination

```python
parser = StandardParser(query="python", rows=20, start=0)
```

### Optimize Faceting

```python
parser.facet(field_list=["category"], limit=10, mincount=5)
```

## Next Steps

Dive deeper into specific parser types:

- **[Sparse Parsers](sparse.md)**: Standard, DisMax, and Extended DisMax
- **[Dense Parsers](dense.md)**: KNN and vector similarity
- **[Spatial Parsers](spatial.md)**: Geographic and location-based search
- **[Controlling Results](../controlling-results/faceting.md)**: Faceting, grouping, highlighting
