# Faceting

Faceting provides aggregated counts of field values in search results, enabling powerful filtering and navigation capabilities for your search application.

**Solr Documentation**: [Faceting](https://solr.apache.org/guide/solr/latest/query-guide/faceting.html)

## Configuration Approaches

There are two ways to configure faceting:

### Constructor Pattern

Pass `FacetParamsConfig` objects directly to the parser constructor:

```python
from taiyo.parsers import ExtendedDisMaxQueryParser
from taiyo.params import FacetParamsConfig

parser = ExtendedDisMaxQueryParser(
    query="machine learning",
    query_fields={"title": 2.0, "content": 1.0},
    configs=[
        FacetParamsConfig(
            fields=["category", "author"],
            mincount=1,
            limit=20
        )
    ]
)
```

### Chaining Pattern

Use the `.facet()` method on the parser:

```python
from taiyo.parsers import ExtendedDisMaxQueryParser

parser = (
    ExtendedDisMaxQueryParser(
        query="machine learning",
        query_fields={"title": 2.0, "content": 1.0}
    )
    .facet(
        fields=["category", "author"],
        mincount=1,
        limit=20
    )
)
```

Both approaches produce identical results. Use whichever style fits your codebase better.

## Basic Faceting

```python
# Using chaining
parser = (
    ExtendedDisMaxQueryParser(
        query="python",
        query_fields={"title": 2.0, "content": 1.0}
    )
    .facet(
        fields=["category", "author", "year"],
        mincount=1,
        limit=20
    )
)

results = client.search(parser)

# Access facet counts
if results.facet_counts:
    category_pairs = results.facet_counts["facet_fields"]["category"]
    for category, count in zip(category_pairs[0::2], category_pairs[1::2]):
        print(f"{category}: {count}")
```

## Facet Parameters

```python
from taiyo.params import FacetParamsConfig

facet_config = FacetParamsConfig(
    # Basic
    fields=["category", "author"],  # Fields to facet on
    mincount=1,                     # Minimum count to include
    limit=20,                       # Max facets per field
    
    # Sorting
    sort="count",                   # Sort by count or index
    
    # Filtering
    prefix="tech",                  # Only values starting with prefix
    contains="python",              # Only values containing string
    
    # Advanced
    missing=False,                  # Include missing/null values
    method="enum",                  # Faceting method: enum, fc, fcs
    offset=0                        # Pagination offset
)
```

To customize individual fields, create additional `FacetParamsConfig` objects—each call to `.facet(...)` appends another configuration.

### Field Facets

The most common type of faceting - count documents by field values:

```python
parser = (
    ExtendedDisMaxQueryParser(
        query="programming",
        query_fields={"title": 2.0, "content": 1.0}
    )
    .facet(
        fields=["category", "author", "tags"],
        mincount=1,
        limit=50,
        sort="count"  # Most common values first
    )
)

results = client.search(parser)

# Show facets
for field in ["category", "author", "tags"]:
    print(f"\n{field.title()}:")
    pairs = results.facet_counts["facet_fields"][field]
    for value, count in zip(pairs[0::2], pairs[1::2]):
        print(f"  {value}: {count}")
```

### Facet Sorting

Control how facet values are sorted:

```python
# Sort by count (most common first)
parser = parser.facet(
    fields=["category"],
    sort="count",
    limit=20
)

# Sort alphabetically
parser = parser.facet(
    fields=["author"],
    sort="index",
    limit=20
)

# Per-field sorting (apply separate configurations)
parser = parser.facet(fields=["category"], sort="count", limit=20)
parser = parser.facet(fields=["author"], sort="index", limit=20)
```

### Filtering Facets

Narrow down which facet values are returned:

```python
# Only values starting with a prefix
parser = parser.facet(
    fields=["category"],
    prefix="tech",  # Only categories starting with "tech"
    mincount=1
)

# Only values containing a string
parser = parser.facet(
    fields=["title"],
    contains="python",  # Only titles containing "python"
    mincount=1
)

# Exclude low-count values
parser = parser.facet(
    fields=["author"],
    mincount=5,  # Only authors with 5+ documents
    limit=20
)
```

### Facet Pagination

Paginate through facet values:

```python
# Get first 20 facets
parser = parser.facet(
    fields=["author"],
    limit=20,
    offset=0
)

# Get next 20 facets
parser = parser.facet(
    fields=["author"],
    limit=20,
    offset=20
)
```

### Per-Field Configuration

Apply different settings by adding multiple facet configurations—each call targets a specific field:

```python
parser = parser.facet(fields=["category"], limit=50, sort="count", mincount=5)
parser = parser.facet(fields=["author"], limit=20, sort="index", prefix="A")
parser = parser.facet(fields=["tags"], limit=100, sort="count")
```

## Range Faceting

Facet on numeric or date ranges:

```python
# Using constructor
from taiyo.params import FacetParamsConfig

parser = ExtendedDisMaxQueryParser(
    query="products",
    query_fields={"name": 2.0, "description": 1.0},
    configs=[
        FacetParamsConfig(
            range_facets={
                "price": {
                    "start": 0,
                    "end": 1000,
                    "gap": 100
                },
                "published_date": {
                    "start": "NOW-1YEAR",
                    "end": "NOW",
                    "gap": "+1MONTH"
                }
            }
        )
    ]
)

results = client.search(parser)

# Access range facets
price_counts = results.facet_counts["facet_ranges"]["price"]["counts"]
for bucket, count in zip(price_counts[0::2], price_counts[1::2]):
    print(f"${bucket}: {count} products")
```

### Numeric Ranges

```python
parser = parser.facet(
    range_facets={
        "price": {
            "start": 0,
            "end": 1000,
            "gap": 100  # $0-100, $100-200, etc.
        },
        "rating": {
            "start": 0,
            "end": 5,
            "gap": 0.5  # 0-0.5, 0.5-1.0, etc.
        },
        "views": {
            "start": 0,
            "end": 10000,
            "gap": 1000
        }
    }
)

results = client.search(parser)

# Show price ranges
print("Price Distribution:")
price_counts = results.facet_counts["facet_ranges"]["price"]["counts"]
for bucket, count in zip(price_counts[0::2], price_counts[1::2]):
    print(f"  {bucket}: {count}")
```

### Date Ranges

```python
parser = parser.facet(
    range_facets={
        "published_date": {
            "start": "NOW-1YEAR",
            "end": "NOW",
            "gap": "+1MONTH"
        },
        "last_modified": {
            "start": "NOW-30DAYS",
            "end": "NOW",
            "gap": "+1DAY"
        },
        "created_date": {
            "start": "2020-01-01T00:00:00Z",
            "end": "2025-01-01T00:00:00Z",
            "gap": "+1YEAR"
        }
    }
)

results = client.search(parser)

# Show date ranges
print("Published by Month:")
date_counts = results.facet_counts["facet_ranges"]["published_date"]["counts"]
for bucket, count in zip(date_counts[0::2], date_counts[1::2]):
    print(f"  {bucket}: {count} documents")
```

## Query Faceting

Facet on arbitrary queries:

```python
parser = (
    ExtendedDisMaxQueryParser(
        query="products",
        query_fields={"name": 2.0}
    )
    .facet(
        queries=[
            "price:[0 TO 50]",
            "price:[50 TO 100]",
            "price:[100 TO 500]",
            "price:[500 TO *]"
        ]
    )
)

results = client.search(parser)

# Access query facets
for query, count in results.facet_counts["facet_queries"].items():
    print(f"{query}: {count}")
```

### Complex Query Facets

```python
parser = parser.facet(
    queries=[
        # Price tiers
        "price:[* TO 50] AND rating:[4 TO *]",  # Budget + Highly rated
        "price:[50 TO 100] AND rating:[3 TO *]",  # Mid-range + Good
        "price:[100 TO *] AND rating:[4.5 TO *]",  # Premium + Excellent
        
        # Recency
        "published_date:[NOW-7DAYS TO NOW]",  # This week
        "published_date:[NOW-30DAYS TO NOW-7DAYS]",  # Last month
        "published_date:[* TO NOW-30DAYS]",  # Older
        
        # Popularity
        "views:[1000 TO *]",  # Popular
        "views:[100 TO 1000]",  # Moderate
        "views:[* TO 100]"  # New/Unpopular
    ]
)

results = client.search(parser)

# Organize results
print("Price Tiers:")
for query, count in results.facet_counts["facet_queries"].items():
    if "price" in query:
        print(f"  {query}: {count}")
```

## Pivot Faceting

Create hierarchical facets (nested facets):

```python
from taiyo.params import FacetParamsConfig

parser = ExtendedDisMaxQueryParser(
    query="books",
    query_fields={"title": 2.0},
    configs=[
        FacetParamsConfig(
            pivot=["category,author", "year,category"],
            mincount=1
        )
    ]
)

results = client.search(parser)

# Navigate hierarchical facets
for pivot in results.facet_counts["facet_pivot"]["category,author"]:
    category = pivot["value"]
    category_count = pivot["count"]
    print(f"{category} ({category_count})")
    
    for author_pivot in pivot.get("pivot", []):
        author = author_pivot["value"]
        author_count = author_pivot["count"]
        print(f"  {author} ({author_count})")
```

### Multi-Level Pivots

```python
parser = parser.facet(
    pivot=[
        "category,subcategory,brand",  # Three levels
        "year,month,day"  # Date hierarchy
    ],
    mincount=2
)

results = client.search(parser)

# Navigate three-level hierarchy
def print_pivot(pivots, indent=0):
    for pivot in pivots:
        value = pivot["value"]
        count = pivot["count"]
        print("  " * indent + f"{value} ({count})")
        
        if "pivot" in pivot:
            print_pivot(pivot["pivot"], indent + 1)

print("Category Hierarchy:")
print_pivot(results.facet_counts["facet_pivot"]["category,subcategory,brand"])
```

## Complete Example

```python
from taiyo.parsers import ExtendedDisMaxQueryParser
from taiyo.params import FacetParamsConfig

parser = ExtendedDisMaxQueryParser(
    query="python programming",
    query_fields={"title": 3.0, "content": 1.0},
    configs=[
        FacetParamsConfig(
            # Field facets
            fields=["category", "author", "difficulty"],
            mincount=1,
            limit=20,
            sort="count",
            
            # Range facets
            range_facets={
                "published_year": {
                    "start": 2015,
                    "end": 2025,
                    "gap": 1
                },
                "page_count": {
                    "start": 0,
                    "end": 1000,
                    "gap": 100
                }
            },
            
            # Query facets
            queries=[
                "rating:[9 TO *]",
                "rating:[7 TO 9]",
                "rating:[* TO 7]"
            ],
            
            # Pivot facets
            pivot=["category,difficulty"]
        )
    ]
)

results = client.search(parser)

# Process all facet types
print("=== Field Facets ===")
print("\nCategories:")
category_pairs = results.facet_counts["facet_fields"]["category"]
for value, count in zip(category_pairs[0::2], category_pairs[1::2]):
    print(f"  {value}: {count}")

print("\n=== Range Facets ===")
print("\nBy Year:")
year_counts = results.facet_counts["facet_ranges"]["published_year"]["counts"]
for bucket, count in zip(year_counts[0::2], year_counts[1::2]):
    print(f"  {bucket}: {count}")

print("\n=== Query Facets ===")
print("\nBy Rating:")
for query, count in results.facet_counts["facet_queries"].items():
    print(f"  {query}: {count}")

print("\n=== Pivot Facets ===")
print("\nCategory → Difficulty:")
for category_pivot in results.facet_counts["facet_pivot"]["category,difficulty"]:
    category = category_pivot["value"]
    cat_count = category_pivot["count"]
    print(f"\n{category} ({cat_count})")
    
    for diff_pivot in category_pivot.get("pivot", []):
        difficulty = diff_pivot["value"]
        diff_count = diff_pivot["count"]
        print(f"  {difficulty}: {diff_count}")
```

## Best Practices

### Limit Facet Values

```python
# Don't request unlimited facets
parser = parser.facet(
    fields=["category"],
    limit=50,        # Top 50 values
    mincount=1,      # Exclude zero counts
    sort="count"     # Most common first
)
```

### Layer Configurations

```python
# Different fields need different settings—stack facet configs
parser = parser.facet(fields=["category"], limit=20, sort="count")
parser = parser.facet(fields=["author"], limit=10, sort="index")
parser = parser.facet(fields=["tags"], limit=100, mincount=5)
```

### Filter Before Faceting

```python
# Apply filters to reduce faceting work
parser = (
    ExtendedDisMaxQueryParser(
        query="programming",
        query_fields={"title": 2.0},
        filters=[
            "status:published",
            "language:en"
        ]
    )
    .facet(
        fields=["category", "author"],
        mincount=1
    )
)
```

### Choose Appropriate Facet Methods

```python
# For low-cardinality fields (few unique values)
parser = parser.facet(
    fields=["category"],
    method="enum",  # Good for low cardinality
    limit=20
)

# For high-cardinality fields (many unique values)
parser = parser.facet(
    fields=["author"],
    method="fc",  # Better for high cardinality
    limit=50
)
```

### Use Range Facets for Continuous Data

Use range facets for continuous numeric fields:

```python
parser = parser.facet(
    range_facets={
        "price": {
            "start": 0,
            "end": 1000,
            "gap": 50
        }
    }
)
```

Avoid faceting directly on high-cardinality numeric fields without ranges.
```

## Common Patterns

### E-commerce Filters

```python
def search_products(query: str, category: str = None):
    """Product search with faceted filters."""
    # Apply category filter if specified
    filters = ["status:available"]
    if category:
        filters.append(f"category:{category}")

    base_parser = ExtendedDisMaxQueryParser(
        query=query,
        query_fields={"name": 3.0, "description": 1.0},
        filters=filters
    )

    parser = (
        base_parser
        .facet(
            fields=["category", "brand", "color", "size"],
            range_facets={
                "price": {
                    "start": 0,
                    "end": 1000,
                    "gap": 50
                }
            },
            queries=[
                "rating:[4 TO *]",  # Highly rated
                "in_stock:true",     # Available
                "on_sale:true"       # On sale
            ],
            mincount=1,
            limit=50
        )
    )
    
    return client.search(parser)
```

### Document Library

```python
def search_documents(query: str):
    """Document search with faceted navigation."""
    parser = (
        ExtendedDisMaxQueryParser(
            query=query,
            query_fields={"title": 3.0, "content": 1.0, "author": 2.0}
        )
        .facet(
            fields=["category", "author", "document_type"],
            range_facets={
                "published_date": {
                    "start": "NOW-5YEARS",
                    "end": "NOW",
                    "gap": "+1YEAR"
                }
            },
            pivot=["category,document_type"],
            mincount=1
        )
        .facet(fields=["category"], limit=20, sort="count")
        .facet(fields=["author"], limit=50, sort="index")
    )
    
    return client.search(parser)
```

### Blog/News Site

```python
def search_articles(query: str):
    """Article search with temporal facets."""
    parser = (
        ExtendedDisMaxQueryParser(
            query=query,
            query_fields={"title": 3.0, "body": 1.0, "tags": 2.0}
        )
        .facet(
            fields=["category", "author", "tags"],
            range_facets={
                "published_date": {
                    "start": "NOW-1YEAR",
                    "end": "NOW",
                    "gap": "+1MONTH"
                }
            },
            queries=[
                "published_date:[NOW-7DAYS TO NOW]",   # This week
                "published_date:[NOW-30DAYS TO NOW]",  # This month
                "featured:true",                       # Featured
                "views:[1000 TO *]"                    # Popular
            ],
            mincount=1
        )
    )
    
    return client.search(parser)
```

## Next Steps

- Learn about [Grouping](grouping.md) for result de-duplication
- Explore [Highlighting](highlighting.md) for search snippets
- See [Query Parsers](parsers/query-parsers.md) for search options
