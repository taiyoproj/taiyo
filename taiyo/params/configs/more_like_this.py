from pydantic import Field
from typing import Optional, Union

from taiyo.params.configs.base import ParamsConfig


class MoreLikeThisParamsConfig(ParamsConfig):
    """Solr MoreLikeThis (MLT) - Find Similar Documents.

    MoreLikeThis finds documents similar to a given document by analyzing
    the terms that make it unique. Common use cases:
    - "Related articles" features
    - Product recommendations
    - Content discovery
    - Duplicate detection

    Official Documentation:
        https://solr.apache.org/guide/solr/latest/query-guide/morelikethis.html

    Basic Example:
        ```python
        config = MoreLikeThisParamsConfig(
            fields=['title', 'content'],  # Analyze these fields
            min_term_freq=2,  # Term must appear 2+ times
            min_doc_freq=5,  # Term must be in 5+ documents
            max_query_terms=25  # Use top 25 most interesting terms
        )
        ```

    Advanced Example:
        ```python
        config = MoreLikeThisParamsConfig(
            fields=['content'],
            min_term_freq=1,
            min_doc_freq=3,
            min_word_len=4,  # Ignore words shorter than 4 chars
            max_doc_freq_pct=80,  # Ignore terms in 80%+ of docs
            interesting_terms='details'  # Show which terms were used
        )
        ```

    Performance Tips:
        - Use fields with term vectors for best performance
        - Adjust min_term_freq and min_doc_freq to filter noise
        - Set max_num_tokens_parsed to limit analysis on large documents
    """

    enable_key: str = "mlt"

    fields: Optional[Union[str, list[str]]] = Field(
        default=None,
        alias="mlt.fl",
        description="Fields to analyze for similarity. Use fields with meaningful content (title, description, body). For best performance, enable term vectors on these fields.",
    )
    min_term_freq: Optional[int] = Field(
        default=None,
        alias="mlt.mintf",
        description="Minimum times a term must appear in the source document to be considered. Default: 2. Lower values include more terms but may add noise.",
    )
    min_doc_freq: Optional[int] = Field(
        default=None,
        alias="mlt.mindf",
        description="Minimum number of documents a term must appear in across the index. Default: 5. Filters out very rare terms.",
    )
    max_doc_freq: Optional[int] = Field(
        default=None,
        alias="mlt.maxdf",
        description="Maximum number of documents a term can appear in. Filters out very common terms (like 'the', 'and'). Use this OR max_doc_freq_pct, not both.",
    )
    max_doc_freq_pct: Optional[int] = Field(
        default=None,
        alias="mlt.maxdfpct",
        description="Maximum document frequency as percentage (0-100). Example: 75 means ignore terms in more than 75% of documents. Use instead of max_doc_freq for relative filtering.",
    )
    min_word_len: Optional[int] = Field(
        default=None,
        alias="mlt.minwl",
        description="Minimum word length in characters. Words shorter than this are ignored. Example: 4 to skip 'the', 'and', 'or'.",
    )
    max_word_len: Optional[int] = Field(
        default=None,
        alias="mlt.maxwl",
        description="Maximum word length in characters. Words longer than this are ignored. Useful to filter out long tokens or URLs.",
    )
    max_query_terms: Optional[int] = Field(
        default=None,
        alias="mlt.maxqt",
        description="Maximum number of interesting terms to use in the MLT query. Default: 25. Higher values = more comprehensive but slower.",
    )
    max_num_tokens_parsed: Optional[int] = Field(
        default=None,
        alias="mlt.maxntp",
        description="Maximum tokens to analyze per field (for fields without term vectors). Default: 5000. Set lower for better performance on large documents.",
    )
    boost: Optional[bool] = Field(
        default=None,
        alias="mlt.boost",
        description="If true, boost the query by each term's relevance/importance. Default: false. Enable for better relevance ranking.",
    )
    query_fields: Optional[str] = Field(
        default=None,
        alias="mlt.qf",
        description="Query fields with optional boosts, like 'title^2.0 content^1.0'. Fields must also be in 'fields' parameter. Use to emphasize certain fields.",
    )
    interesting_terms: Optional[str] = Field(
        default=None,
        alias="mlt.interestingTerms",
        description="Controls what info about matched terms is returned. Options: 'none' (default), 'list' (term names), 'details' (terms with boost values). Use 'details' for debugging.",
    )
    match_include: Optional[bool] = Field(
        default=None,
        alias="mlt.match.include",
        description="If true, includes the source document in results (useful to compare). Default: true for MLT handler, varies for component.",
    )
    match_offset: Optional[int] = Field(
        default=None,
        alias="mlt.match.offset",
        description="When using with a query, specifies which result doc to use for similarity (0 = first result, 1 = second, etc.). Default: 0.",
    )
