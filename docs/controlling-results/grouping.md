# Grouping

Grouping (also known as field collapsing) groups search results by a field value, useful for de-duplication, entity grouping, or showing representative results from each category.

**Solr Documentation**: [Result Grouping](https://solr.apache.org/guide/solr/latest/query-guide/collapse-and-expand-results.html)

## Configuration Approaches

=== "Constructor"

    ```python
    from taiyo.parsers import ExtendedDisMaxQueryParser
    from taiyo.params import GroupParamsConfig

    parser = ExtendedDisMaxQueryParser(
        query="python programming",
        query_fields={"title": 2.0, "content": 1.0},
        configs=[GroupParamsConfig(by="author", limit=3, ngroups=True)],
    )
    ```

=== "Chaining"

    ```python
    from taiyo.parsers import ExtendedDisMaxQueryParser

    parser = ExtendedDisMaxQueryParser(
        query="python programming", query_fields={"title": 2.0, "content": 1.0}
    ).group(by="author", limit=3, ngroups=True)
    ```

## Basic Usage

```python
parser = ExtendedDisMaxQueryParser(
    query="python", query_fields={"title": 2.0, "content": 1.0}
).group(
    by="author",  # Group by author field
    limit=3,  # Top 3 docs per group
    ngroups=True,  # Return number of groups
)

results = client.search(parser)

# Access grouped results
if results.extra and "grouped" in results.extra:
    for group in results.extra["grouped"]["author"]["groups"]:
        author = group["groupValue"]
        docs = group["doclist"]["docs"]
        print(f"\n{author} ({len(docs)} results)")
        for doc in docs:
            print(f"  - {doc.title}")
```

## Key Parameters

```python
GroupParamsConfig(
    by="author",  # Field to group by (single-valued, indexed)
    limit=3,  # Docs per group
    offset=0,  # Offset within groups
    sort="score desc",  # Sort within groups
    format="grouped",  # Response format: grouped or simple
    main=False,  # Use main result list
    ngroups=True,  # Return total group count
    truncate=False,  # Truncate facets to group leaders
    facet=False,  # Enable group-aware faceting
    # Query-based grouping
    query=["category:programming", "category:databases"],  # Custom query groups
    # Function-based grouping (not supported in SolrCloud)
    func="floor(price)",  # Group by function result
)
```

Refer to the [Apache Solr documentation](https://solr.apache.org/guide/solr/latest/query-guide/result-grouping.html) for the full list of parameters and defaults.

## Handling Results

Grouping responses are available through `SolrResponse.extra["grouped"]`:

- `SolrResponse.docs`: Flattened list of all documents across groups
- `SolrResponse.extra["grouped"][field_name]`: Grouped results by field
- Each group contains `groupValue`, `doclist` with nested documents and counts
- `ngroups`: Total number of unique groups when enabled

Example:

```python
from taiyo.parsers import ExtendedDisMaxQueryParser

parser = ExtendedDisMaxQueryParser(
    query="python", query_fields={"title": 2.0, "content": 1.0}
).group(
    by="author",
    limit=3,
    sort="year desc",
    ngroups=True,
)

results = client.search(parser)

if results.extra and "grouped" in results.extra:
    grouped_data = results.extra["grouped"]["author"]

    # Total number of groups
    if "ngroups" in grouped_data:
        print(f"Found {grouped_data['ngroups']} authors\n")

    # Iterate through groups
    for group in grouped_data["groups"]:
        author = group["groupValue"]
        doclist = group["doclist"]
        total = doclist["numFound"]
        docs = doclist["docs"]

        print(f"\n{author} ({total} total)")
        for doc in docs:
            print(f"  - {doc['title']}")

# Query-based grouping example
parser = ExtendedDisMaxQueryParser(
    query="technology", query_fields={"content": 1.0}
).group(
    query=["category:programming", "category:databases"],
    limit=5,
)

results = client.search(parser)

if results.extra and "grouped" in results.extra:
    for query_str in ["category:programming", "category:databases"]:
        group = results.extra["grouped"][query_str]
        print(f"{query_str}: {group['matches']} matches")
```

## Next Steps

- Learn about [Faceting](faceting.md) for aggregations
- Explore [Highlighting](highlighting.md) for search snippets
- See [Query Parsers](../parsers/overview.md) for search options
