# MoreLikeThis (MLT)

MoreLikeThis (MLT) surfaces documents that share significant terms with a seed document.

**Solr Documentation**: [MoreLikeThis](https://solr.apache.org/guide/solr/latest/query-guide/morelikethis.html)

## Configuration Approaches

=== "Constructor"

    ```python
    from taiyo.parsers import StandardParser
    from taiyo.params import MoreLikeThisParamsConfig

    parser = StandardParser(
        query="id:article-123",
        configs=[
            MoreLikeThisParamsConfig(
                fields=["title", "content"],
                min_term_freq=1,
                min_doc_freq=1,
                max_query_terms=20,
                boost=True,
                match_include=False,
            )
        ],
    )
    ```

=== "Chaining"

    ```python
    from taiyo.parsers import StandardParser

    parser = StandardParser(query="id:article-123", rows=1).more_like_this(
        fields=["title", "content"],
        min_term_freq=1,
        min_doc_freq=1,
        max_query_terms=20,
        boost=True,
        match_include=False,
    )
    ```

## Basic Usage

```python
parser = StandardParser(query=f"id:{target_id}", rows=1).more_like_this(
    fields=["title", "content"],
    min_term_freq=1,
    min_doc_freq=1,
    max_query_terms=20,
    boost=True,
    match_include=False,
)

response = client.search(parser, document_model=Article)
```

## Key Parameters

```python
MoreLikeThisParamsConfig(
    fields=["title", "content"],  # Fields to analyze for similarity
    min_term_freq=1,  # Minimum term frequency in the seed doc
    min_doc_freq=1,  # Minimum document frequency across the index
    max_doc_freq_pct=80,  # (Optional) Percentage threshold for common terms
    max_query_terms=20,  # Cap on interesting terms used for the query
    min_word_len=3,  # Ignore short tokens
    max_num_tokens_parsed=5000,  # Limit analysis for non term-vector fields
    boost=True,  # Boost by term relevance scores
    query_fields="title^2.0 content",  # Optional boosted query fields
    interesting_terms="details",  # Include term provenance in the response
    match_include=False,  # Exclude the seed document from results
)
```

Refer to the [Apache Solr documentation](https://solr.apache.org/guide/solr/latest/query-guide/morelikethis.html) for the full list of parameters and defaults.

## Handling Results

MLT responses are mapped onto typed models in Taiyo to make downstream handling ergonomic:

- `SolrResponse.more_like_this`: a mapping of source document IDs to `SolrMoreLikeThisResult` instances.
- `SolrMoreLikeThisResult.docs`: parsed `SolrDocument` instances representing similar documents.
- `SolrMoreLikeThisResult.interesting_terms`: optional per-document metadata when `interesting_terms` is set to `list` or `details`.

Example:

```python
from taiyo.types import SolrMoreLikeThisResult

mlt_map: dict[str, SolrMoreLikeThisResult[Article]] = response.more_like_this or {}
related = mlt_map.get(target_id)

if related:
    print(f"Found {related.num_found} related docs")
    for doc in related.docs:
        print(doc.id, doc.title)

    if related.interesting_terms:
        print("Interesting terms:")
        if isinstance(related.interesting_terms, dict):
            for term, boost in related.interesting_terms.items():
                print(f"  {term}: {boost}")
        else:
            for term in related.interesting_terms:
                print(f"  {term}")
```

When working with `interesting_terms="details"`, Solr returns a dictionary keyed by term with boost values. Taiyo surfaces those details in the `SolrMoreLikeThisResult` so you can inspect which tokens contributed to the similarity score.

## Next Steps

- Learn about [Faceting](faceting.md) for aggregations
- Explore [Grouping](grouping.md) for result organization
- See [Highlighting](highlighting.md) for search snippets
