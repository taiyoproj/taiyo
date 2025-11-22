# Grouping

Grouping (also known as field collapsing) groups search results by a field value, useful for de-duplication, entity grouping, or showing representative results from each category.

**Solr Documentation**: [Result Grouping](https://solr.apache.org/guide/solr/latest/query-guide/collapse-and-expand-results.html)

## Configuration Approaches

There are two ways to configure grouping:

### Constructor Pattern

Pass `GroupParamsConfig` objects directly to the parser constructor:

```python
from taiyo.parsers import ExtendedDisMaxQueryParser
from taiyo.params import GroupParamsConfig

parser = ExtendedDisMaxQueryParser(
    query="python programming",
    query_fields={"title": 2.0, "content": 1.0},
    configs=[
        GroupParamsConfig(
            by="author",
            limit=3,
            ngroups=True
        )
    ]
)
```

### Chaining Pattern

Use the `.group()` method on the parser:

```python
from taiyo.parsers import ExtendedDisMaxQueryParser

parser = (
    ExtendedDisMaxQueryParser(
        query="python programming",
        query_fields={"title": 2.0, "content": 1.0}
    )
    .group(
        by="author",
        limit=3,
        ngroups=True
    )
)
```

Both approaches produce identical results. Use whichever style fits your codebase better.

## Basic Grouping

```python
# Using chaining
parser = (
    ExtendedDisMaxQueryParser(
        query="python",
        query_fields={"title": 2.0, "content": 1.0}
    )
    .group(
        by="author",      # Group by author field
        limit=3,          # Top 3 docs per group
        ngroups=True      # Return number of groups
    )
)

results = client.search(parser)

# Access grouped results
if results.grouped:
    for group in results.grouped["author"]["groups"]:
        author = group["groupValue"]
        docs = group["doclist"]["docs"]
        print(f"\n{author} ({len(docs)} results)")
        for doc in docs:
            print(f"  - {doc.title}")
```

## Group Parameters

```python
from taiyo.params import GroupParamsConfig

group_config = GroupParamsConfig(
    by="author",              # Field to group by
    limit=3,                  # Docs per group
    offset=0,                 # Offset within groups
    sort="score desc",        # Sort within groups
    format="grouped",         # Response format: grouped or simple
    main=False,               # Use main result list
    ngroups=True,            # Return total group count
    truncate=True,           # Truncate facets to group leaders
    facet=True               # Enable group.facet
)
```

### Field Grouping

Group results by a single field value:

```python
# Group by author
parser = (
    ExtendedDisMaxQueryParser(
        query="web development",
        query_fields={"title": 2.0, "content": 1.0}
    )
    .group(
        by="author",
        limit=5,           # Top 5 articles per author
        ngroups=True       # Count total authors
    )
)

results = client.search(parser)

print(f"Found {results.grouped['author']['ngroups']} authors")

for group in results.grouped["author"]["groups"]:
    author = group["groupValue"]
    total = group["doclist"]["numFound"]
    docs = group["doclist"]["docs"]
    
    print(f"\n{author} ({total} total)")
    for doc in docs:
        print(f"  {doc.title}")
```

### Group Sorting

Control how documents are sorted within each group:

```python
# Sort by relevance within groups
parser = parser.group(
    by="category",
    limit=3,
    sort="score desc"  # Most relevant first
)

# Sort by date within groups
parser = parser.group(
    by="author",
    limit=5,
    sort="published_date desc"  # Newest first
)

# Complex sorting
parser = parser.group(
    by="category",
    limit=3,
    sort="rating desc, published_date desc"  # Best rated, then newest
)
```

### Group Pagination

Paginate through documents within groups:

```python
# First 3 docs per group
parser = parser.group(
    by="author",
    limit=3,
    offset=0
)

# Next 3 docs per group
parser = parser.group(
    by="author",
    limit=3,
    offset=3
)
```

### Number of Groups

Get the total count of unique groups:

```python
parser = parser.group(
    by="category",
    limit=5,
    ngroups=True  # Return total number of categories
)

results = client.search(parser)

# Access group count
total_categories = results.grouped["category"]["ngroups"]
print(f"Found {total_categories} categories")
```

## Group by Query

Group by query matches instead of field values:

```python
parser = (
    ExtendedDisMaxQueryParser(
        query="technology",
        query_fields={"content": 1.0}
    )
    .group(
        queries=[
            "category:programming",
            "category:databases",
            "category:networking"
        ],
        limit=5
    )
)

results = client.search(parser)

# Access query groups
for query in ["category:programming", "category:databases", "category:networking"]:
    group = results.grouped[query]
    print(f"\n{query}: {group['matches']} matches")
    for doc in group["doclist"]["docs"]:
        print(f"  - {doc.title}")
```

### Multiple Query Groups

Create multiple arbitrary groupings:

```python
parser = parser.group(
    queries=[
        # By recency
        "published_date:[NOW-7DAYS TO NOW]",
        "published_date:[NOW-30DAYS TO NOW-7DAYS]",
        "published_date:[* TO NOW-30DAYS]",
        
        # By popularity
        "views:[1000 TO *]",
        "views:[100 TO 1000]",
        "views:[* TO 100]",
        
        # By rating
        "rating:[8 TO *]",
        "rating:[5 TO 8]",
        "rating:[* TO 5]"
    ],
    limit=10
)

results = client.search(parser)

# Show results by recency
print("By Recency:")
for query in ["published_date:[NOW-7DAYS TO NOW]", 
              "published_date:[NOW-30DAYS TO NOW-7DAYS]"]:
    count = results.grouped[query]["matches"]
    print(f"  {query}: {count}")
```

## Response Format

Control how grouped results are returned:

```python
# Grouped format (default)
parser = parser.group(
    by="author",
    limit=3,
    format="grouped"  # Returns nested structure
)

# Simple format (flat list with group field)
parser = parser.group(
    by="author",
    limit=3,
    format="simple",  # Returns flat list
    main=True         # Use main result list
)
```

### Grouped Format Example

```python
results = client.search(parser)

# Navigate grouped structure
for group in results.grouped["author"]["groups"]:
    author = group["groupValue"]
    docs = group["doclist"]["docs"]
    total = group["doclist"]["numFound"]
    
    print(f"{author}: {len(docs)} of {total}")
```

### Simple Format Example

```python
results = client.search(parser)

# Flat list with group information
for doc in results.docs:
    print(f"{doc.title} by {doc.author}")
```

## Combining with Facets

Grouping works well with faceting:

```python
parser = (
    ExtendedDisMaxQueryParser(
        query="python",
        query_fields={"title": 2.0, "content": 1.0}
    )
    .group(
        by="author",
        limit=3,
        truncate=True,  # Facets based on group heads
        facet=True      # Enable group-aware faceting
    )
    .facet(
        fields=["category", "year"],
        mincount=1
    )
)

results = client.search(parser)

# Show groups
for group in results.grouped["author"]["groups"]:
    print(f"\n{group['groupValue']}:")
    for doc in group["doclist"]["docs"]:
        print(f"  {doc.title}")

# Show facets (based on group heads)
print("\n\nCategories:")
for category, count in results.facet_counts["facet_fields"]["category"]:
    print(f"  {category}: {count}")
```

## Complete Example

```python
from taiyo.parsers import ExtendedDisMaxQueryParser

parser = (
    ExtendedDisMaxQueryParser(
        query="web development",
        query_fields={"title": 3.0, "content": 1.0, "tags": 2.0},
        rows=100  # Max groups to return
    )
    .group(
        by="author",
        limit=3,              # Top 3 articles per author
        sort="published_date desc",  # Newest first within group
        ngroups=True          # Count total authors
    )
    .facet(
        fields=["category", "year"],
        mincount=1
    )
    .with_params(
        fields=["id", "title", "author", "published_date", "category"],
        filter_query=["status:published", "language:en"]
    )
)

results = client.search(parser)

print(f"Found articles from {results.grouped['author']['ngroups']} authors\n")

for group in results.grouped["author"]["groups"]:
    author = group["groupValue"]
    doclist = group["doclist"]
    total = doclist["numFound"]
    docs = doclist["docs"]
    
    print(f"\n{author} ({total} articles)")
    for doc in docs:
        print(f"  - {doc.title}")
        print(f"    Published: {doc.published_date}")
        print(f"    Category: {doc.category}")

# Show category distribution
print("\n\nCategories:")
for category, count in results.facet_counts["facet_fields"]["category"]:
    print(f"  {category}: {count}")
```

## Use Cases

### De-duplication

Show one result per duplicate group:

```python
# Remove duplicate products (same ISBN)
parser = (
    ExtendedDisMaxQueryParser(
        query="python programming",
        query_fields={"title": 2.0}
    )
    .group(
        by="isbn",
        limit=1,  # One per ISBN
        main=True  # Flat result list
    )
)

results = client.search(parser)

# Get de-duplicated results
for doc in results.docs:
    print(doc.title)
```

### Entity Grouping

Show results grouped by related entity:

```python
# Group news articles by company
parser = (
    ExtendedDisMaxQueryParser(
        query="technology merger",
        query_fields={"headline": 3.0, "body": 1.0}
    )
    .group(
        by="company",
        limit=5,  # Top 5 articles per company
        sort="published_date desc",
        ngroups=True
    )
)

results = client.search(parser)

for group in results.grouped["company"]["groups"]:
    company = group["groupValue"]
    articles = group["doclist"]["docs"]
    
    print(f"\n{company}:")
    for article in articles:
        print(f"  {article.headline} - {article.published_date}")
```

### Category Preview

Show sample results from each category:

```python
# Show top result from each category
parser = (
    ExtendedDisMaxQueryParser(
        query="smartphones",
        query_fields={"name": 2.0, "description": 1.0}
    )
    .group(
        by="brand",
        limit=1,  # Top product per brand
        sort="rating desc, price asc",
        ngroups=True
    )
)

results = client.search(parser)

print(f"Found {results.grouped['brand']['ngroups']} brands\n")

for group in results.grouped["brand"]["groups"]:
    brand = group["groupValue"]
    product = group["doclist"]["docs"][0]
    
    print(f"{brand}: {product.name}")
    print(f"  Rating: {product.rating}/5")
    print(f"  Price: ${product.price}")
```

### Author Portfolio

Show author's best work:

```python
# Show top articles per author
parser = (
    ExtendedDisMaxQueryParser(
        query="machine learning",
        query_fields={"title": 3.0, "abstract": 2.0}
    )
    .group(
        by="author",
        limit=3,  # Top 3 papers per author
        sort="citations desc",  # Most cited first
        ngroups=True
    )
)

results = client.search(parser)

for group in results.grouped["author"]["groups"]:
    author = group["groupValue"]
    papers = group["doclist"]["docs"]
    total = group["doclist"]["numFound"]
    
    print(f"\n{author} ({total} papers)")
    for paper in papers:
        print(f"  {paper.title}")
        print(f"    Citations: {paper.citations}")
```

## Best Practices

### Balance Group Size

```python
parser = parser.group(
    by="author",
    limit=3,
    ngroups=True,
    truncate=True
)
```

### Choose Appropriate Fields

Group on fields with reasonable cardinality:

```python
parser = parser.group(by="author", limit=3)
```

Suitable fields: author, category, brand (hundreds to thousands of values)
Avoid: timestamp, id (too many unique values)

### Use with Pagination

```python
parser = (
    ExtendedDisMaxQueryParser(
        query="search",
        query_fields={"title": 2.0}
    )
    .group(by="category", limit=5)
    .with_params(rows=20)
)
```

### Combine with Filters

Filter before grouping to reduce processing:

```python
parser = (
    ExtendedDisMaxQueryParser(
        query="products",
        query_fields={"name": 2.0}
    )
    .with_params(
        filter_query=[
            "status:active",
            "in_stock:true"
        ]
    )
    .group(by="brand", limit=5)
)
```

### Optimize Facets

```python
# Use truncate=True for better facet performance
parser = (
    parser
    .group(
        by="author",
        limit=3,
        truncate=True,  # Facets only on group heads
        facet=True
    )
    .facet(fields=["category"])
)
```

## Common Patterns

### Search Result Diversity

Show diverse results (one per category):

```python
def diverse_search(query: str):
    """Return diverse results across categories."""
    parser = (
        ExtendedDisMaxQueryParser(
            query=query,
            query_fields={"title": 3.0, "content": 1.0}
        )
        .group(
            by="category",
            limit=1,  # One per category
            sort="score desc",
            ngroups=True
        )
        .with_params(rows=10)
    )
    
    results = client.search(parser)
    
    # Return one result per category
    diverse_results = []
    for group in results.grouped["category"]["groups"]:
        diverse_results.append(group["doclist"]["docs"][0])
    
    return diverse_results
```

### Related Items

Show related items grouped by type:

```python
def find_related(item_id: str):
    """Find related items grouped by type."""
    parser = (
        StandardParser(query=f"related_to:{item_id}")
        .group(
            by="item_type",
            limit=5,
            sort="relevance_score desc"
        )
    )
    
    results = client.search(parser)
    
    related = {}
    for group in results.grouped["item_type"]["groups"]:
        item_type = group["groupValue"]
        items = group["doclist"]["docs"]
        related[item_type] = items
    
    return related
```

### Duplicate Detection

Find and show duplicates:

```python
def find_duplicates(query: str, field: str = "content_hash"):
    """Find duplicate documents."""
    parser = (
        ExtendedDisMaxQueryParser(
            query=query,
            query_fields={"title": 2.0, "content": 1.0}
        )
        .group(
            by=field,
            limit=10,  # All duplicates
            ngroups=True
        )
    )
    
    results = client.search(parser)
    
    # Only show groups with duplicates
    duplicates = []
    for group in results.grouped[field]["groups"]:
        if group["doclist"]["numFound"] > 1:
            duplicates.append({
                "hash": group["groupValue"],
                "count": group["doclist"]["numFound"],
                "docs": group["doclist"]["docs"]
            })
    
    return duplicates
```

## Next Steps

- Learn about [Faceting](faceting.md) for aggregations
- Explore [Highlighting](highlighting.md) for search snippets
- See [Query Parsers](parsers/query-parsers.md) for search options
