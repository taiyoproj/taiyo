# Highlighting

Highlighting shows matching query terms in context, enabling you to display relevant snippets in search results with matched terms emphasized.

**Solr Documentation**: [Highlighting](https://solr.apache.org/guide/solr/latest/query-guide/highlighting.html)

## Configuration Approaches

There are two ways to configure highlighting:

### Constructor Pattern

Pass `HighlightParamsConfig` objects directly to the parser constructor:

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

### Chaining Pattern

Use the `.highlight()` method on the parser:

```python
from taiyo.parsers import ExtendedDisMaxQueryParser

parser = ExtendedDisMaxQueryParser(
    query="python programming", query_fields={"title": 2.0, "content": 1.0}
).highlight(fields=["title", "content"], fragment_size=150, snippets_per_field=3)
```

Both approaches produce identical results. Use whichever style fits your codebase better.

## Basic Highlighting

```python
# Using chaining
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

## Highlight Parameters

```python
from taiyo.params import HighlightParamsConfig
from taiyo.schema.enums import HighlightMethod

highlight_config = HighlightParamsConfig(
    # Basic
    fields=["title", "content"],  # Fields to highlight
    fragment_size=150,  # Snippet size in characters
    snippets_per_field=3,  # Max snippets per field
    # Tags
    simple_pre="<em>",  # Opening tag
    simple_post="</em>",  # Closing tag
    tag_pre="<mark>",  # Alternative opening tag
    tag_post="</mark>",  # Alternative closing tag
    # Method
    method=HighlightMethod.UNIFIED,  # Method: unified, fastVector, original
    # Boundaries
    boundary_scanner="breakIterator",  # Boundary detection
    bs_language="en",  # Language for boundaries
    bs_country="US",  # Country for boundaries
    # Advanced
    require_field_match=True,  # Only highlight matched fields
    max_analyzed_chars=51200,  # Limit analyzed characters
    fragsize=0,  # 0 = whole field value
    multi_term=True,  # Highlight wildcard/fuzzy
)
```

To vary parameters per field, add additional `HighlightParamsConfig` instances or chain `.highlight(...)` calls for each field you need to tune.

## Highlight Methods

Solr provides three highlighting implementations with different characteristics:

### Unified Highlighter (Recommended)

```python
from taiyo.schema.enums import HighlightMethod

parser = parser.highlight(
    fields=["title", "content"],
    method=HighlightMethod.UNIFIED,  # Fast, accurate, recommended
    fragment_size=150,
    snippets_per_field=3,
)
```

**Advantages:**
- Fast performance
- Accurate phrase highlighting
- Good memory efficiency
- Works well with most query types

**Best for:** Most use cases

### FastVector Highlighter

```python
parser = parser.highlight(
    fields=["content"],
    method=HighlightMethod.FASTVECTOR,  # Requires term vectors
    fragment_size=150,
    snippets_per_field=3,
)
```

**Requirements:** Field must have `termVectors="true"` in schema

**Advantages:**
- Very fast for large documents
- Efficient fragment selection

**Best for:** Large documents with term vectors enabled

### Original Highlighter

```python
parser = parser.highlight(
    fields=["content"],
    method=HighlightMethod.ORIGINAL,  # Legacy implementation
    fragment_size=150,
    snippets_per_field=3,
)
```

**Advantages:**
- Stable, well-tested
- Works without term vectors

**Best for:** Legacy compatibility

## Custom Highlight Tags

### HTML Tags

```python
# Simple emphasis
parser = parser.highlight(
    fields=["title", "content"],
    simple_pre="<em>",
    simple_post="</em>",
    fragment_size=150,
)

# Bold
parser = parser.highlight(
    fields=["content"],
    simple_pre="<strong>",
    simple_post="</strong>",
    fragment_size=150,
)

# Mark element with class
parser = parser.highlight(
    fields=["title", "content"],
    simple_pre="<mark class='highlight'>",
    simple_post="</mark>",
    fragment_size=150,
)

# Span with styling
parser = parser.highlight(
    fields=["content"],
    simple_pre="<span style='background-color: yellow;'>",
    simple_post="</span>",
    fragment_size=200,
)
```

### Multiple Tag Types

```python
# Use tag_pre/tag_post for alternate tagging
parser = parser.highlight(
    fields=["content"],
    tag_pre="<strong class='match'>",
    tag_post="</strong>",
    fragment_size=150,
)
```

## Fragment Configuration

### Fragment Size

Control the length of highlighted snippets:

```python
# Short snippets (good for previews)
parser = parser.highlight(fields=["content"], fragment_size=100, snippets_per_field=5)

# Medium snippets (balanced)
parser = parser.highlight(fields=["content"], fragment_size=200, snippets_per_field=3)

# Long snippets (more context)
parser = parser.highlight(fields=["content"], fragment_size=400, snippets_per_field=2)

# Whole field (no fragmentation)
parser = parser.highlight(
    fields=["title"],
    fragment_size=0,  # Return entire field
    snippets_per_field=1,
)
```

### Number of Snippets

```python
# Single best snippet
parser = parser.highlight(fields=["content"], fragment_size=150, snippets_per_field=1)

# Multiple snippets
parser = parser.highlight(fields=["content"], fragment_size=150, snippets_per_field=5)
```

### Per-Field Configuration

Different settings for different fields by chaining highlight calls:

```python
parser = parser.highlight(
    fields=["title"],
    fragment_size=0,
    snippets_per_field=1,
    simple_pre="<strong>",
    simple_post="</strong>",
).highlight(
    fields=["abstract"],
    fragment_size=300,
    snippets_per_field=2,
    simple_pre="<mark>",
    simple_post="</mark>",
)
```

## Boundary Control

Control where fragments break:

### Sentence Boundaries

```python
parser = parser.highlight(
    fields=["content"],
    fragment_size=200,
    boundary_scanner="breakIterator",  # Use sentence boundaries
    bs_language="en",
    bs_country="US",
)
```

### Word Boundaries

```python
parser = parser.highlight(
    fields=["content"],
    fragment_size=150,
    boundary_scanner="simple",  # Break on whitespace
    bs_max_scan=20,  # How far to scan for boundary
)
```

## Advanced Options

### Require Field Match

Only highlight fields that were actually matched:

```python
parser = parser.highlight(
    fields=["title", "content", "tags"],
    require_field_match=True,  # Only highlight matched fields
    fragment_size=150,
)
```

### Multi-Term Highlighting

Highlight wildcard and fuzzy matches:

```python
# Query: "prog*" or "python~2"
parser = ExtendedDisMaxQueryParser(
    query="prog* python~2", query_fields={"content": 1.0}
).highlight(
    fields=["content"],
    multi_term=True,  # Highlight "program", "programming", etc.
    fragment_size=150,
)
```

### Character Limit

Limit how much text is analyzed:

```python
parser = parser.highlight(
    fields=["content"],
    max_analyzed_chars=100000,  # Process up to 100K chars
    fragment_size=150,
)
```

## Example

```python
from taiyo.parsers import ExtendedDisMaxQueryParser
from taiyo.params import HighlightParamsConfig
from taiyo.schema.enums import HighlightMethod

parser = (
    ExtendedDisMaxQueryParser(
        query="machine learning neural networks",
        query_fields={"title": 3.0, "abstract": 2.0, "content": 1.0},
        configs=[
            HighlightParamsConfig(
                fields=["title", "abstract", "content"],
                method=HighlightMethod.UNIFIED,
                fragment_size=200,
                snippets_per_field=3,
                simple_pre="<mark>",
                simple_post="</mark>",
                require_field_match=True,
                boundary_scanner="breakIterator",
                bs_language="en",
                multi_term=True,
            )
        ],
    )
    .highlight(
        fields=["title"],
        fragment_size=0,
        snippets_per_field=1,
        simple_pre="<strong>",
        simple_post="</strong>",
    )
    .highlight(fields=["abstract"], fragment_size=300, snippets_per_field=2)
    .highlight(fields=["content"], fragment_size=150, snippets_per_field=5)
)

results = client.search(parser)

for doc in results.docs:
    print(f"\n{'=' * 80}")
    print(f"Title: {doc.title}")
    print(f"Score: {doc.score:.3f}\n")

    if results.highlighting and doc.id in results.highlighting:
        highlights = results.highlighting[doc.id]

        # Show title highlight (if matched)
        if "title" in highlights:
            print("Title Match:")
            print(f"  {highlights['title'][0]}\n")

        # Show abstract highlights
        if "abstract" in highlights:
            print("Abstract:")
            for snippet in highlights["abstract"]:
                print(f"  {snippet}")
            print()

        # Show content highlights
        if "content" in highlights:
            print("Content:")
            for i, snippet in enumerate(highlights["content"][:3], 1):
                print(f"  [{i}] ...{snippet}...")
```

## Use Cases

### Search Result Snippets

Show relevant excerpts in search results:

```python
def search_with_snippets(query: str):
    """Search with highlighted snippets."""
    parser = ExtendedDisMaxQueryParser(
        query=query, query_fields={"title": 3.0, "content": 1.0}
    ).highlight(
        fields=["title", "content"],
        fragment_size=150,
        snippets_per_field=2,
        simple_pre="<em class='highlight'>",
        simple_post="</em>",
    )

    results = client.search(parser)

    search_results = []
    for doc in results.docs:
        result = {"id": doc.id, "title": doc.title, "score": doc.score, "snippets": []}

        if results.highlighting and doc.id in results.highlighting:
            hl = results.highlighting[doc.id]
            if "content" in hl:
                result["snippets"] = hl["content"]

        search_results.append(result)

    return search_results
```

### Document Preview

Show preview with all matches highlighted:

```python
def get_document_preview(doc_id: str, query: str):
    """Get document with all matches highlighted."""
    parser = StandardParser(query=f"id:{doc_id}").highlight(
        fields=["title", "content"],
        fragment_size=0,  # Whole content
        snippets_per_field=1,
        simple_pre="<mark>",
        simple_post="</mark>",
        query=query,  # Highlight matches for the original search terms
    )

    results = client.search(parser)

    if results.docs:
        doc = results.docs[0]
        highlighted = results.highlighting.get(doc.id, {})

        return {
            "title": highlighted.get("title", [doc.title])[0],
            "content": highlighted.get("content", [doc.content])[0],
        }
```

### Multi-Language Highlighting

Handle different languages:

```python
def search_multilingual(query: str, language: str):
    """Search with language-specific highlighting."""
    parser = ExtendedDisMaxQueryParser(
        query=query, query_fields={"title": 2.0, "content": 1.0}
    ).highlight(
        fields=["title", "content"],
        fragment_size=200,
        snippets_per_field=3,
        boundary_scanner="breakIterator",
        bs_language=language,  # Language-specific boundaries
        simple_pre="<mark>",
        simple_post="</mark>",
    )

    return client.search(parser)


# Usage
results_en = search_multilingual("machine learning", "en")
results_de = search_multilingual("maschinelles lernen", "de")
results_ja = search_multilingual("機械学習", "ja")
```

## Best Practices

### Choose Appropriate Fragment Size

Adjust fragment size based on field type:

```python
parser = parser.highlight(fields=["title"], fragment_size=0)

parser = parser.highlight(fields=["abstract"], fragment_size=300)

parser = parser.highlight(fields=["content"], fragment_size=150)
```

### Limit Snippets

```python
parser = parser.highlight(fields=["content"], snippets_per_field=3, fragment_size=150)
```

### Use Unified Highlighter

```python
from taiyo.schema.enums import HighlightMethod

parser = parser.highlight(
    fields=["content"], method=HighlightMethod.UNIFIED, fragment_size=150
)
```

The unified highlighter provides the best performance and features for most use cases.

### Set Character Limits

```python
parser = parser.highlight(
    fields=["content"],
    max_analyzed_chars=100000,  # 100K limit
    fragment_size=150,
)
```

### Use Require Field Match

```python
# Only highlight fields that actually matched
parser = parser.highlight(
    fields=["title", "content", "tags"], require_field_match=True, fragment_size=150
)
```

### Optimize Tags

```python
# Use simple, semantic HTML
parser = parser.highlight(
    fields=["content"],
    simple_pre="<mark>",  # Semantic HTML5
    simple_post="</mark>",
    fragment_size=150,
)

# Or use classes for styling
parser = parser.highlight(
    fields=["content"],
    simple_pre="<span class='match'>",
    simple_post="</span>",
    fragment_size=150,
)
```

## Common Patterns

### Context-Aware Snippets

Show snippets with query context:

```python
def get_contextual_snippets(query: str, num_results: int = 10):
    """Get search results with contextual snippets."""
    parser = ExtendedDisMaxQueryParser(
        query=query, query_fields={"title": 3.0, "content": 1.0}, rows=num_results
    ).highlight(
        fields=["content"],
        fragment_size=200,
        snippets_per_field=3,
        boundary_scanner="breakIterator",
        simple_pre="<strong>",
        simple_post="</strong>",
    )

    results = client.search(parser)

    snippets = []
    for doc in results.docs:
        if results.highlighting and doc.id in results.highlighting:
            if "content" in results.highlighting[doc.id]:
                snippets.append(
                    {
                        "doc_id": doc.id,
                        "title": doc.title,
                        "snippets": results.highlighting[doc.id]["content"],
                    }
                )

    return snippets
```

### Highlighting with Facets

Combine highlighting with faceted search:

```python
parser = (
    ExtendedDisMaxQueryParser(
        query="python", query_fields={"title": 2.0, "content": 1.0}
    )
    .highlight(fields=["title", "content"], fragment_size=150, snippets_per_field=2)
    .facet(fields=["category", "author"], mincount=1)
)

results = client.search(parser)

# Show results with snippets and facets
for doc in results.docs:
    print(f"\n{doc.title}")

    if results.highlighting and doc.id in results.highlighting:
        for snippet in results.highlighting[doc.id].get("content", []):
            print(f"  ...{snippet}...")

print("\n\nCategories:")
category_facet = results.facets.fields.get("category") if results.facets else None
if category_facet:
    for bucket in category_facet.buckets:
        print(f"  {bucket.value}: {bucket.count}")
```

### Progressive Highlighting

Show more highlights on demand:

```python
def search_with_progressive_highlights(query: str, detail_level: str = "low"):
    """Adjust highlight detail based on user preference."""
    configs = {
        "low": {"fragment_size": 100, "snippets_per_field": 1},
        "medium": {"fragment_size": 150, "snippets_per_field": 3},
        "high": {"fragment_size": 200, "snippets_per_field": 5},
    }

    config = configs.get(detail_level, configs["medium"])

    parser = ExtendedDisMaxQueryParser(
        query=query, query_fields={"title": 2.0, "content": 1.0}
    ).highlight(
        fields=["title", "content"],
        fragment_size=config["fragment_size"],
        snippets_per_field=config["snippets_per_field"],
        simple_pre="<mark>",
        simple_post="</mark>",
    )

    return client.search(parser)
```

## Next Steps

- Learn about [Faceting](faceting.md) for aggregations
- Explore [Grouping](grouping.md) for result organization
- See [Query Parsers](parsers/query-parsers.md) for search options
