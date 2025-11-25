# Highlighting

Highlighting shows matching query terms in context, enabling you to display relevant snippets in search results with matched terms emphasized.

**Solr Documentation**: [Highlighting](https://solr.apache.org/guide/solr/latest/query-guide/highlighting.html)

## Configuration Approaches

=== "Constructor"

    ```python
    from taiyo.parsers import ExtendedDisMaxQueryParser
    from taiyo.params import HighlightParamsConfig

    parser = ExtendedDisMaxQueryParser(
        query="python programming",
        query_fields={"title": 2.0, "content": 1.0},
        configs=[
            HighlightParamsConfig(
                fields=["title", "content"], fragment_size=150, snippets_per_field=3
            )
        ],
    )
    ```

=== "Chaining"

    ```python
    from taiyo.parsers import ExtendedDisMaxQueryParser

    parser = ExtendedDisMaxQueryParser(
        query="python programming", query_fields={"title": 2.0, "content": 1.0}
    ).highlight(fields=["title", "content"], fragment_size=150, snippets_per_field=3)
    ```

## Basic Usage

```python
parser = ExtendedDisMaxQueryParser(
    query="python programming", query_fields={"title": 2.0, "content": 1.0}
).highlight(fields=["title", "content"], fragment_size=150, snippets_per_field=3)

results = client.search(parser)

# Access highlights
for doc in results.docs:
    print(f"\n{doc.title}")

    if results.highlighting and doc.id in results.highlighting:
        highlights = results.highlighting[doc.id]
        if "content" in highlights:
            for snippet in highlights["content"]:
                print(f"  ...{snippet}...")
```

## Key Parameters

```python
HighlightParamsConfig(
    fields=["title", "content"],  # Fields to highlight
    fragment_size=150,  # Snippet size in characters
    snippets_per_field=3,  # Max snippets per field
    simple_pre="<em>",  # Opening tag
    simple_post="</em>",  # Closing tag
    require_field_match=True,  # Only highlight matched fields
    method="unified",  # Highlighter method: unified, original, fastVector
    max_analyzed_chars=51200,  # Maximum characters to analyze
    # Unified Highlighter options
    bs_type="SENTENCE",  # Boundary scanner type
    bs_language="en",  # Language for boundary detection
    # Multi-term support
    multiterm=True,  # Highlight wildcard/fuzzy matches
)
```

Refer to the [Apache Solr documentation](https://solr.apache.org/guide/solr/latest/query-guide/highlighting.html) for the full list of parameters and defaults.

## Handling Results

Highlighting responses are available through `SolrResponse.highlighting`:

- `SolrResponse.highlighting`: Dictionary mapping document IDs to highlighted field snippets
- Each document's highlights contain field names mapped to lists of snippet strings
- Query terms are wrapped in the configured tags (default: `<em>` tags)

Example:

```python
from taiyo.parsers import ExtendedDisMaxQueryParser

parser = ExtendedDisMaxQueryParser(
    query="python programming", query_fields={"title": 2.0, "content": 1.0}
).highlight(
    fields=["title", "content"],
    fragment_size=150,
    snippets_per_field=3,
    simple_pre="<mark>",
    simple_post="</mark>",
)

results = client.search(parser)

for doc in results.docs:
    print(f"\nDocument: {doc.id}")
    print(f"Title: {doc.title}")

    if results.highlighting and doc.id in results.highlighting:
        highlights = results.highlighting[doc.id]

        # Title highlights
        if "title" in highlights:
            print("\nTitle Match:")
            print(f"  {highlights['title'][0]}")

        # Content highlights
        if "content" in highlights:
            print("\nContent Snippets:")
            for i, snippet in enumerate(highlights["content"], 1):
                print(f"  [{i}] ...{snippet}...")
```

## Next Steps

- Learn about [Faceting](faceting.md) for aggregations
- Explore [Grouping](grouping.md) for result organization
- See [Query Parsers](parsers/query-parsers.md) for search options
