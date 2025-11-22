from typing import Optional, List, Union
from pydantic import Field
from taiyo.params.configs.base import ParamsConfig


class GroupParamsConfig(ParamsConfig):
    """Solr Result Grouping - Collapse Results by Common Values.

    Result grouping (also known as field collapsing) combines documents that share
    a common field value. Useful for:
    - Showing one result per author, category, or domain
    - Preventing duplicate-like results from dominating
    - Creating grouped summaries of search results

    Official Documentation:
        https://solr.apache.org/guide/solr/latest/query-guide/result-grouping.html

    Example - Group by Author:
        ```python
        config = GroupParamsConfig(
            by='author',  # Group documents by author
            limit=3,  # Show up to 3 docs per author
            sort='date desc',  # Newest first within each group
            ngroups=True  # Include count of total groups
        )
        ```

    Example - Group by Price Range:
        ```python
        config = GroupParamsConfig(
            query=['price:[0 TO 50]', 'price:[50 TO 100]'],  # Custom groups
            limit=5  # Up to 5 docs per price range
        )
        ```

    Important Notes:
        - Grouped fields must be single-valued and indexed
        - group.func doesn't work in distributed (SolrCloud) searches
        - Use 'format="simple"' for flat response structure
        - 'ngroups' and 'facet' require documents co-located on same shard
    """

    enable_key: str = "group"

    by: Optional[Union[str, List[str]]] = Field(
        default=None,
        alias="group.field",
        description="""Field(s) to group results by. Shows one representative doc per unique field value.
        
        Example: by='author' shows one document per author.
        
        Requirements:
        - Must be single-valued (not multi-valued)
        - Must be indexed
        - String-based fields (StrField or TextField) work best
        
        Can specify multiple fields to create separate groupings.""",
    )
    func: Optional[str] = Field(
        default=None,
        alias="group.func",
        description="""Group by the result of a function query.
        
        Example: 'floor(price)' groups by rounded price values.
        
        **Important**: Not supported in SolrCloud/distributed searches.
        Only works with standalone Solr or single-shard collections.""",
    )
    query: Optional[Union[str, List[str]]] = Field(
        default=None,
        alias="group.query",
        description="""Create custom groups using arbitrary queries.
        
        Example: ['price:[0 TO 50]', 'price:[50 TO 100]', 'price:[100 TO *]']
        creates three price range groups.
        
        Each query defines one group. Documents matching the query are grouped together.
        Can specify multiple queries for multiple custom groups.""",
    )
    limit: Optional[int] = Field(
        default=1,
        alias="group.limit",
        description="""Number of documents to return per group.
        
        Example: limit=5 returns up to 5 docs from each group.
        
        Default: 1 (only the top document per group)
        Set higher to see more examples from each group.""",
    )
    offset: Optional[int] = Field(
        default=None,
        alias="group.offset",
        description="""Skip the first N documents within each group.
        
        Example: offset=2, limit=5 returns documents 3-7 from each group.
        
        Useful for pagination within groups.""",
    )
    sort: Optional[str] = Field(
        default=None,
        alias="group.sort",
        description="""How to sort documents within each group.
        
        Example: 'date desc' shows newest first within each group.
        
        If not specified, uses the main sort parameter (which sorts the groups themselves).
        Format: 'field direction' like 'price asc' or 'date desc'.""",
    )
    format: Optional[str] = Field(
        default="grouped",
        alias="group.format",
        description="""Response structure format.
        
        - 'grouped': Nested structure showing groups explicitly (default, recommended)
        - 'simple': Flat document list (easier for some clients to parse)
        
        Default: 'grouped'""",
    )
    main: Optional[bool] = Field(
        default=None,
        alias="group.main",
        description="""Return first field grouping as main result list.
        
        If true, flattens the response structure (similar to format='simple').
        Useful for simpler client code when you only care about one grouping.
        
        Default: false""",
    )
    ngroups: Optional[bool] = Field(
        default=False,
        alias="group.ngroups",
        description="""Include the total number of unique groups in response.
        
        Example: Shows "25 authors matched" even if only showing 10 groups.
        
        Useful for pagination and showing total counts.
        Default: false
        
        **Note**: In SolrCloud, requires all docs with same field value on same shard.""",
    )
    truncate: Optional[bool] = Field(
        default=False,
        alias="group.truncate",
        description="""Base facet counts on one document per group only.
        
        If true, faceting counts each group once (the top doc).
        If false, faceting counts all matching documents.
        
        Example: 10 books by same author count as 1 (true) or 10 (false) for author facet.
        Default: false""",
    )
    facet: Optional[bool] = Field(
        default=False,
        alias="group.facet",
        description="""Enable grouped faceting.
        
        Computes facets for groups (based on first specified group field).
        Can be expensive - use with caution on large result sets.
        
        Default: false
        
        **Note**: Fields must not be tokenized. Requires co-location in SolrCloud.""",
    )
    cache_percent: Optional[int] = Field(
        default=0,
        alias="group.cache.percent",
        description="""Enable result grouping cache (0-100).
        
        Caches the second-pass search in grouping.
        
        Performance impact:
        - Improves: Boolean queries, wildcards, fuzzy queries
        - Degrades: Simple exact-match queries
        
        Set to 0 to disable caching (default).
        Try values like 50 or 100 if you have complex queries.
        
        Default: 0 (disabled)""",
    )
