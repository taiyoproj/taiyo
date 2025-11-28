# Sparse Query Parsers

Sparse query parsers are traditional keyword-based search parsers that work with text analysis and inverted indexes. Taiyo supports all three major Solr sparse parsers.

## StandardParser (Lucene)

The `StandardParser` uses Solr's default Lucene query syntax, providing powerful and precise query capabilities.

**Solr Documentation**: [Standard Query Parser](https://solr.apache.org/guide/solr/latest/query-guide/standard-query-parser.html)

### Basic Usage

```python
from taiyo.parsers import StandardParser

parser = StandardParser(
    query="python programming", query_operator="AND", default_field="content"
)

results = client.search(parser)
```

### Parameters

```python
parser = StandardParser(
    query="search term",  # Query string
    query_operator="OR",  # Default operator: OR or AND
    default_field="content",  # Default field when not specified
    split_on_whitespace=True,  # Split query on whitespace
    # Common parameters
    rows=10,
    start=0,
    field_list=["id", "title"],
    sort="score desc",
    filters=["status:active"],
)
```

### Query Syntax Examples

```python
# Simple term
parser = StandardParser(query="python")

# Field-specific search
parser = StandardParser(query="title:python")

# Boolean operators
parser = StandardParser(query="python AND programming")
parser = StandardParser(query="python OR java")
parser = StandardParser(query="python NOT perl")

# Phrase search
parser = StandardParser(query='"machine learning"')

# Proximity search (within 5 words)
parser = StandardParser(query='"apache solr"~5')

# Wildcard search
parser = StandardParser(query="prog*")
parser = StandardParser(query="te?t")

# Fuzzy search (edit distance)
parser = StandardParser(query="python~2")

# Range queries
parser = StandardParser(query="price:[100 TO 500]")
parser = StandardParser(query="date:[NOW-1YEAR TO NOW]")

# Boost terms
parser = StandardParser(query="python^2 java")

# Grouped queries
parser = StandardParser(query="(python OR java) AND programming")

# Field exists
parser = StandardParser(query="description:*")

# Field doesn't exist
parser = StandardParser(query="-description:*")
```

### Example

```python
from taiyo.parsers import StandardParser

parser = (
    StandardParser(
        query='(title:"machine learning" OR content:AI) AND category:tech',
        query_operator="AND",
        default_field="content",
        rows=20,
        field_list=["id", "title", "author", "published_date"],
        sort="published_date desc",
        filters=["status:published", "published_date:[NOW-1YEAR TO NOW]"],
    )
    .facet(field_list=["category", "author"], mincount=1)
    .highlight(field_list=["title", "content"], fragment_size=150)
)

results = client.search(parser)
```

## DisMaxQueryParser

The `DisMaxQueryParser` (DisjunctionMax) is designed for simple, user-entered queries. It searches across multiple fields and returns the best matching field score.

**Solr Documentation**: [DisMax Query Parser](https://solr.apache.org/guide/solr/latest/query-guide/dismax-query-parser.html)

### Basic Usage

```python
from taiyo.parsers import DisMaxQueryParser

parser = DisMaxQueryParser(
    query="python programming",
    query_fields={"title": 3.0, "content": 1.0},
    min_match="75%",
)

results = client.search(parser)
```

### Parameters

```python
parser = DisMaxQueryParser(
    query="search term",  # User query
    query_fields={"title": 2.0, "content": 1.0},  # Fields to search with boosts
    query_slop=0,  # Phrase slop
    phrase_fields={"title": 3.0},  # Phrase boosting
    phrase_slop=0,  # Phrase proximity slop
    tie_breaker=0.1,  # How to combine field scores
    min_match="75%",  # Minimum should match
    boost_queries=["featured:true^5"],  # Additional query boosts
    boost_functons=["recip(ms(NOW,date),3.16e-11,1,1)"],  # Function boosts
)
```

### Query Fields

Weight different fields differently:

```python
parser = DisMaxQueryParser(
    query="python programming",
    query_fields={
        "title": 5.0,  # Title matches are most important
        "abstract": 3.0,  # Abstract matches are important
        "content": 1.0,  # Body matches are standard
        "tags": 2.0,  # Tag matches are moderately important
    },
)
```

### Minimum Match

Control how many terms must match:

```python
# At least 75% of query terms must match
parser = DisMaxQueryParser(
    query="python programming language",
    query_fields={"title": 2.0, "content": 1.0},
    min_match="75%",  # 3 terms → 2 must match
)

# Absolute number
parser = DisMaxQueryParser(
    query="python programming language",
    query_fields={"title": 2.0, "content": 1.0},
    min_match="2",  # At least 2 terms must match
)

# Complex conditional
parser = DisMaxQueryParser(
    query="search terms here",
    query_fields={"title": 2.0, "content": 1.0},
    min_match="2<-25% 9<-3",  # Complex rules
)
```

### Phrase Boosting

Boost documents where terms appear together:

```python
parser = DisMaxQueryParser(
    query="machine learning",
    query_fields={"title": 2.0, "content": 1.0},
    phrase_fields={"title": 10.0},  # Boost exact phrase in title
    phrase_slop=2,  # Allow 2 words between terms
)
```

### Tie Breaker

Control how scores from different fields combine:

```python
# tie_breaker=0: Only use highest field score (default DisMax behavior)
# tie_breaker=1: Sum all field scores
# tie_breaker=0.1: Mostly use highest, slightly influenced by others

parser = DisMaxQueryParser(
    query="python",
    query_fields={"title": 2.0, "content": 1.0},
    tie_breaker=0.1,  # Slight influence from lower-scoring fields
)
```

### Example

```python
from taiyo.parsers import DisMaxQueryParser

parser = DisMaxQueryParser(
    query="python web framework",
    query_fields={"title": 5.0, "description": 3.0, "content": 1.0, "tags": 2.0},
    phrase_fields={
        "title": 10.0,  # Phrase in title = big boost
        "description": 5.0,
    },
    phrase_slop=2,
    min_match="75%",
    tie_breaker=0.1,
    boost_queries=[
        "featured:true^10",  # Featured items boosted
        "recent:true^5",  # Recent items boosted
    ],
    rows=20,
    filters=["status:published"],
).facet(field_list=["category", "author"], mincount=1)

results = client.search(parser)
```

## ExtendedDisMaxQueryParser

The `ExtendedDisMaxQueryParser` (eDisMax) extends DisMax with more advanced features while maintaining user-friendliness.

**Solr Documentation**: [Extended DisMax Query Parser](https://solr.apache.org/guide/solr/latest/query-guide/edismax-query-parser.html)

### Basic Usage

```python
from taiyo.parsers import ExtendedDisMaxQueryParser

parser = ExtendedDisMaxQueryParser(
    query="python programming",
    query_fields={"title": 3.0, "content": 1.0},
    min_match="75%",
)

results = client.search(parser)
```

### All DisMax Features Plus...

eDisMax includes all DisMax parameters and adds:

```python
parser = ExtendedDisMaxQueryParser(
    # All DisMax parameters
    query="python programming",
    query_fields={"title": 3.0, "content": 1.0},
    min_match="75%",
    tie_breaker=0.1,
    # Extended features
    stop_words=True,  # Remove stop words
    lowercase_operators=True,  # Allow 'and', 'or', 'not' (lowercase)
    user_fields={"author": 2.0},  # Additional searchable fields
    boost_params=["featured^10"],  # Additional boost parameters
)
```

### User Fields

Allow users to search additional fields:

```python
parser = ExtendedDisMaxQueryParser(
    query="python programming author:guido",
    query_fields={"title": 3.0, "content": 1.0},
    user_fields={"author": 2.0},  # Allow searching author field
)
```

### Phrase Fields with Slop Variants

Different phrase proximity levels:

```python
parser = ExtendedDisMaxQueryParser(
    query="machine learning",
    query_fields={"title": 2.0, "content": 1.0},
    # Exact phrase boost
    phrase_fields={"title": 10.0},
    # Near-phrase boost (2-word slop)
    phrase_slop_2_fields={"title": 5.0, "content": 2.0},
    # Looser phrase boost (5-word slop)
    phrase_slop_3_fields={"title": 3.0, "content": 1.5},
)
```

### Boost Functions

Apply function-based boosts:

```python
parser = ExtendedDisMaxQueryParser(
    query="python",
    query_fields={"title": 2.0, "content": 1.0},
    boost_functons=[
        "recip(ms(NOW,published_date),3.16e-11,1,1)",  # Boost recent docs
        "log(views)",  # Boost by popularity
        "product(rating,10)",  # Boost by rating
    ],
)
```

### Field Aliasing

Allow users to use aliases for fields:

```python
parser = ExtendedDisMaxQueryParser(
    query="t:python c:web",  # t = title, c = content
    field_aliases={"t": "title", "c": "content", "a": "author"},
)
```

### Example

```python
from taiyo.parsers import ExtendedDisMaxQueryParser

parser = (
    ExtendedDisMaxQueryParser(
        query="python web framework -php",
        query_fields={"title": 5.0, "description": 3.0, "content": 1.0, "tags": 2.0},
        phrase_fields={"title": 10.0, "description": 5.0},
        phrase_slop=2,
        user_fields={"author": 2.0, "category": 1.5},
        min_match="75%",
        tie_breaker=0.1,
        boost_queries=["featured:true^20", "quality_score:[8 TO *]^10"],
        boost_functons=[
            "recip(ms(NOW,published_date),3.16e-11,1,1)",  # Recency
            "log(popularity)",  # Popularity
        ],
        stop_words=True,
        lowercase_operators=True,
        rows=20,
        field_list=["id", "title", "author", "published_date", "score"],
        sort="score desc, published_date desc",
        filters=["status:published", "language:en"],
    )
    .facet(field_list=["category", "author", "year"], mincount=1, limit=20)
    .group(by="author", limit=3, ngroups=True)
    .highlight(
        field_list=["title", "description", "content"],
        fragment_size=150,
        snippets_per_field=3,
        simple_pre="<mark>",
        simple_post="</mark>",
    )
)

results = client.search(parser)

# Process results
print(f"Found {results.num_found} documents in {results.query_time}ms")

for doc in results.docs:
    print(f"\n{doc.title} by {doc.author}")

    # Show highlights if available
    if results.highlighting and doc.id in results.highlighting:
        for field, snippets in results.highlighting[doc.id].items():
            print(f"  {field}: {', '.join(snippets)}")

# Show facets
if results.facets:
    print("\nCategories:")
    category_facet = results.facets.fields.get("category")
    if category_facet:
        for bucket in category_facet.buckets:
            print(f"  {bucket.value}: {bucket.count}")
```

## Comparison

| Feature | Standard | DisMax | eDisMax |
|---------|----------|--------|---------|
| **User-friendly** | No | Yes | Yes |
| **Boolean operators** | Yes | No | Yes (optional) |
| **Field queries** | Yes | No | Yes (with user_fields) |
| **Multi-field search** | Manual | Yes | Yes |
| **Field boosting** | Manual | Yes | Yes |
| **Phrase boosting** | Manual | Yes | Yes |
| **Function boosting** | Manual | Yes | Yes |
| **Minimum match** | Manual | Yes | Yes |
| **Nested queries** | Yes | Limited | Yes |
| **Best for** | Experts | Simple UI | Power users |

## Best Practices

### Choose the Right Parser

For complex boolean queries:

```python
parser = StandardParser(
    query='(title:"machine learning" OR tags:ml) AND category:tech NOT deprecated:true'
)
```

For simple search interfaces:

```python
parser = DisMaxQueryParser(
    query="machine learning", query_fields={"title": 3.0, "content": 1.0}
)
```

For flexible user queries:

```python
parser = ExtendedDisMaxQueryParser(
    query="machine learning -deprecated", query_fields={"title": 3.0, "content": 1.0}
)
```

### Use Appropriate Field Weights

```python
# Consider field importance
parser = DisMaxQueryParser(
    query="search term",
    query_fields={
        "title": 10.0,  # Most important
        "headline": 5.0,  # Very important
        "abstract": 3.0,  # Important
        "content": 1.0,  # Normal importance
        "metadata": 0.5,  # Less important
    },
)
```

### Tune Minimum Match

```python
# Strict matching (all terms)
parser = DisMaxQueryParser(query="python web framework", min_match="100%")

# Balanced (most terms)
parser = DisMaxQueryParser(query="python web framework", min_match="75%")

# Loose (any terms)
parser = DisMaxQueryParser(query="python web framework", min_match="1")
```

### Use Phrase Boosting Strategically

```python
# Boost exact phrases significantly
parser = ExtendedDisMaxQueryParser(
    query="machine learning",
    query_fields={"title": 2.0, "content": 1.0},
    phrase_fields={"title": 10.0, "content": 5.0},  # 5x-10x boost
    phrase_slop=0,  # Exact phrase only
)
```

### Combine with Filters

```python
# Use filter_query for constraints (cached)
parser = DisMaxQueryParser(
    query="python",
    query_fields={"title": 2.0, "content": 1.0},
    filters=[
        "status:active",  # Cached
        "published_date:[NOW-1YEAR TO NOW]",  # Cached
        "language:en",  # Cached
    ],
)
```

## Next Steps

- Learn about [Dense Parsers](dense.md) for vector similarity search
- Explore [Spatial Parsers](spatial.md) for geographic queries
- Add [Faceting](../controlling-results/faceting.md) for aggregations and filters
- Use [Grouping](../controlling-results/grouping.md) for result organization
- Enable [Highlighting](../controlling-results/highlighting.md) for search snippets
