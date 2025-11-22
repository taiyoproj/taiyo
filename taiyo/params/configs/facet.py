"""Solr Faceting Configuration.

Faceting allows you to categorize search results into groups with counts,
enabling users to refine searches by drilling down into categories.

Common use cases:
- Product filtering (category, brand, price range)
- Search refinement (date ranges, locations)
- Analytics and reporting

Official Documentation:
    https://solr.apache.org/guide/solr/latest/query-guide/faceting.html

Example:
    ```python
    facet_config = FacetParamsConfig(
        fields=['category', 'brand'],  # Facet by category and brand
        limit=10,  # Show top 10 values per facet
        mincount=1,  # Only show facets with at least 1 match
        sort=FacetSort.COUNT  # Sort by count (highest first)
    )
    ```
"""

from enum import Enum
from typing import Dict, List, Optional

from pydantic import Field
from taiyo.params.configs.base import ParamsConfig


class FacetMethod(str, Enum):
    """Faceting algorithm methods.

    Choose based on your field characteristics:
    - ENUM: Best for fields with few distinct values (enumerates all terms)
    - FIELD_CACHE: Best for fields with many unique terms but few per document
    - PER_SEGMENT: Best for single-valued strings with frequent index updates

    Reference: https://solr.apache.org/guide/solr/latest/query-guide/faceting.html#the-facet-method-parameter
    """

    ENUM = "enum"  # Enumerate all terms, good for low-cardinality fields
    FIELD_CACHE = "fc"  # Use field cache, good for high-cardinality fields
    PER_SEGMENT = "fcs"  # Per-segment faceting for faster index updates


class FacetSort(str, Enum):
    """How to order facet results.

    - COUNT: Sort by frequency (most common first) - default for most use cases
    - INDEX: Sort lexicographically (alphabetically)
    """

    COUNT = "count"  # Sort by count (highest first)
    INDEX = "index"  # Sort alphabetically/lexicographically


class RangeOther(str, Enum):
    """Additional range buckets to include beyond start/end.

    - BEFORE: Count docs below the first range
    - AFTER: Count docs above the last range
    - BETWEEN: Count docs within start and end bounds
    - NONE: No additional counts
    - ALL: Include all (before, after, between)
    """

    BEFORE = "before"  # Docs below first range's lower bound
    AFTER = "after"  # Docs above last range's upper bound
    BETWEEN = "between"  # Docs between start and end
    NONE = "none"  # No additional buckets
    ALL = "all"  # All additional buckets


class RangeInclude(str, Enum):
    """Control which range boundaries are inclusive/exclusive.

    By default, ranges are [lower, upper) - include lower, exclude upper.

    - LOWER: All ranges include their lower bound
    - UPPER: All ranges include their upper bound
    - EDGE: First and last ranges include their edge bounds
    - OUTER: 'before' and 'after' ranges are inclusive
    - ALL: Shorthand for all of the above
    """

    LOWER = "lower"  # Include lower bound [x, y)
    UPPER = "upper"  # Include upper bound (x, y]
    EDGE = "edge"  # First/last ranges include edges
    OUTER = "outer"  # before/after ranges are inclusive
    ALL = "all"  # All boundaries inclusive


class RangeMethod(str, Enum):
    """Range faceting method options."""

    FILTER = "filter"
    DV = "dv"


class FacetParamsConfig(ParamsConfig):
    """Solr Faceting Configuration - Categorize and Count Search Results.

    Faceting breaks down search results into categories with counts, enabling
    drill-down navigation and data analysis.

    Official Documentation:
        https://solr.apache.org/guide/solr/latest/query-guide/faceting.html

    Common Patterns:

        Basic Field Faceting:
        ```python
        config = FacetParamsConfig(
            fields=['category', 'brand'],  # Fields to facet on
            limit=10,  # Top 10 values
            mincount=1  # Skip empty facets
        )
        ```

        Range Faceting (Prices, Dates):
        ```python
        config = FacetParamsConfig(
            range_field=['price'],
            range_start={'price': '0'},
            range_end={'price': '1000'},
            range_gap={'price': '100'}  # $0-100, $100-200, etc.
        )
        ```

        Filtered Facets:
        ```python
        config = FacetParamsConfig(
            fields=['color'],
            prefix='bl',  # Only colors starting with 'bl' (blue, black)
            mincount=5  # Only show if 5+ matches
        )
        ```

    Performance Tips:
        - Use appropriate 'method' for your field type
        - Set 'mincount' to reduce result size
        - Consider 'threads' for parallel faceting on large datasets
    """

    enable_key: str = "facet"

    queries: Optional[List[str]] = Field(
        default=None,
        alias="facet.query",
        description="Arbitrary queries to generate facet counts for specific terms/expressions.",
    )
    fields: Optional[List[str]] = Field(
        default=None, alias="facet.field", description="Fields to be treated as facets."
    )
    prefix: Optional[str] = Field(
        default=None,
        alias="facet.prefix",
        description="Limits facet terms to those starting with the given prefix.",
    )
    contains: Optional[str] = Field(
        default=None,
        alias="facet.contains",
        description="Limits facet terms to those containing the given substring.",
    )
    contains_ignore_case: Optional[bool] = Field(
        default=None,
        alias="facet.contains.ignoreCase",
        description="If true, ignores case when matching facet.contains.",
    )
    matches: Optional[str] = Field(
        default=None,
        alias="facet.matches",
        description="Only returns facets matching this regular expression.",
    )
    sort: Optional[FacetSort] = Field(
        default=None,
        alias="facet.sort",
        description="Ordering of facet field terms (count or index).",
    )
    limit: Optional[int] = Field(
        default=None,
        alias="facet.limit",
        description="Number of facet counts to return (-1 for all).",
    )
    offset: Optional[int] = Field(
        default=None,
        alias="facet.offset",
        description="Offset into the facet list for paging.",
    )
    mincount: Optional[int] = Field(
        default=None,
        alias="facet.mincount",
        description="Minimum count for facets to be included in response.",
    )
    missing: Optional[bool] = Field(
        default=None,
        alias="facet.missing",
        description="Include count of results with no facet value.",
    )
    method: Optional[FacetMethod] = Field(
        default=None,
        alias="facet.method",
        description="Algorithm/method to use for faceting.",
    )
    enum_cache_min_df: Optional[int] = Field(
        default=None,
        alias="facet.enum.cache.minDf",
        description="Minimum document frequency for filterCache usage with enum method.",
    )
    exists: Optional[bool] = Field(
        default=None,
        alias="facet.exists",
        description="Cap facet counts by 1 (only for non-trie fields).",
    )
    exclude_terms: Optional[str] = Field(
        default=None,
        alias="facet.excludeTerms",
        description="Terms to remove from facet counts.",
    )
    overrequest_count: Optional[int] = Field(
        default=None,
        alias="facet.overrequest.count",
        description="Extra facets to request from each shard.",
    )
    overrequest_ratio: Optional[float] = Field(
        default=None,
        alias="facet.overrequest.ratio",
        description="Ratio for overrequesting facets from shards.",
    )
    threads: Optional[int] = Field(
        default=None,
        alias="facet.threads",
        description="Number of threads for parallel facet loading.",
    )

    range_field: Optional[List[str]] = Field(
        default=None, alias="facet.range", description="Fields for range faceting."
    )
    range_start: Optional[Dict[str, str]] = Field(
        default=None,
        alias="facet.range.start",
        description="Lower bound of ranges per field.",
    )
    range_end: Optional[Dict[str, str]] = Field(
        default=None,
        alias="facet.range.end",
        description="Upper bound of ranges per field.",
    )
    range_gap: Optional[Dict[str, str]] = Field(
        default=None,
        alias="facet.range.gap",
        description="Size of each range span per field.",
    )
    range_hardend: Optional[bool] = Field(
        default=None,
        alias="facet.range.hardend",
        description="Whether to use exact range.end as upper bound.",
    )
    range_include: Optional[List[RangeInclude]] = Field(
        default=None,
        alias="facet.range.include",
        description="Range bounds to include in faceting.",
    )
    range_other: Optional[List[RangeOther]] = Field(
        default=None,
        alias="facet.range.other",
        description="Additional range counts to compute.",
    )
    range_method: Optional[RangeMethod] = Field(
        default=None,
        alias="facet.range.method",
        description="Method to use for range faceting.",
    )

    pivot_fields: Optional[List[str]] = Field(
        default=None,
        alias="facet.pivot",
        description="Fields to use for pivot faceting.",
    )
    pivot_mincount: Optional[int] = Field(
        default=None,
        alias="facet.pivot.mincount",
        description="Minimum count for pivot facet inclusion.",
    )
