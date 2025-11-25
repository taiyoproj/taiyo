# Faceting

Faceting provides aggregated counts of field values in search results, enabling filtering and navigation.

**Solr Documentation**: [Faceting](https://solr.apache.org/guide/solr/latest/query-guide/faceting.html)

## Configuration Approaches

=== "Constructor"

    ```python
    from taiyo.parsers import ExtendedDisMaxQueryParser
    from taiyo.params import FacetParamsConfig

    parser = ExtendedDisMaxQueryParser(
        query="technology",
        query_fields={"title": 2.0, "content": 1.0},
        configs=[FacetParamsConfig(fields=["category", "author"], mincount=1)],
    )
    ```

=== "Chaining"

    ```python
    from taiyo.parsers import ExtendedDisMaxQueryParser

    parser = ExtendedDisMaxQueryParser(
        query="technology", query_fields={"title": 2.0, "content": 1.0}
    ).facet(fields=["category", "author"], mincount=1)
    ```

## Basic Usage

```python
from taiyo.parsers import ExtendedDisMaxQueryParser

parser = ExtendedDisMaxQueryParser(
    query="python", query_fields={"title": 2.0, "content": 1.0}
).facet(fields=["category", "author"], mincount=1)

results = client.search(parser)

# Access facet counts
if results.facets:
    category_facet = results.facets.fields.get("category")
    if category_facet:
        for bucket in category_facet.buckets:
            print(f"{bucket.value}: {bucket.count}")
```

## Key Parameters

```python
FacetParamsConfig(
    fields=["category", "author"],  # Fields to facet on
    mincount=1,  # Minimum count to include
    limit=20,  # Max values per field
    sort="count",  # Sort by count or index
    # Range faceting
    range_field=["price"],  # Fields for range faceting
    range_start={"price": "0"},  # Lower bound per field
    range_end={"price": "1000"},  # Upper bound per field
    range_gap={"price": "100"},  # Range size per field
    # Query faceting
    queries=["price:[0 TO 50]", "price:[50 TO *]"],  # Arbitrary query facets
    # Pivot faceting
    pivot_fields=["category,brand"],  # Hierarchical facets
)
```

Refer to the [Apache Solr documentation](https://solr.apache.org/guide/solr/latest/query-guide/faceting.html) for the full list of parameters and defaults.

## Handling Results

Facet responses are available through `SolrResponse.facets`:

- `SolrResponse.facets.fields`: Field facets with term counts
- `SolrResponse.facets.ranges`: Range facets with bucket counts
- `SolrResponse.facets.queries`: Query facet counts
- `SolrResponse.facets.pivots`: Hierarchical pivot facets

Example:

```python
from taiyo.parsers import ExtendedDisMaxQueryParser

parser = ExtendedDisMaxQueryParser(
    query="products",
    query_fields={"name": 2.0},
).facet(
    fields=["category", "brand"],
    range_field=["price"],
    range_start={"price": "0"},
    range_end={"price": "1000"},
    range_gap={"price": "100"},
    mincount=1,
)

results = client.search(parser)

if results.facets:
    # Field facets
    category_facet = results.facets.fields.get("category")
    if category_facet:
        print("Categories:")
        for bucket in category_facet.buckets:
            print(f"  {bucket.value}: {bucket.count}")

    # Range facets
    price_facet = results.facets.ranges.get("price")
    if price_facet:
        print("\nPrice Ranges:")
        for bucket in price_facet.buckets:
            print(f"  ${bucket.value}: {bucket.count}")
```

## Next Steps

- Learn about [Grouping](grouping.md) for result de-duplication
- Explore [Highlighting](highlighting.md) for search snippets
- See [Query Parsers](parsers/query-parsers.md) for search options
