"""Solr faceting models.

This module provides Pydantic models for Solr's faceting functionality, including:
- General facet parameters
- Field-value faceting
- Range faceting
- Pivot (Decision Tree) faceting
"""

from enum import Enum
from typing import Dict, List, Optional

from pydantic import Field
from taiyo.params.configs.base import ParamsConfig


class FacetMethod(str, Enum):
    """Available faceting methods."""

    ENUM = "enum"
    FIELD_CACHE = "fc"
    PER_SEGMENT = "fcs"


class FacetSort(str, Enum):
    """Facet sorting options."""

    COUNT = "count"
    INDEX = "index"


class RangeOther(str, Enum):
    """Range faceting 'other' options."""

    BEFORE = "before"
    AFTER = "after"
    BETWEEN = "between"
    NONE = "none"
    ALL = "all"


class RangeInclude(str, Enum):
    """Range faceting 'include' options."""

    LOWER = "lower"
    UPPER = "upper"
    EDGE = "edge"
    OUTER = "outer"
    ALL = "all"


class RangeMethod(str, Enum):
    """Range faceting method options."""

    FILTER = "filter"
    DV = "dv"


class FacetParamsConfig(ParamsConfig):
    """Comprehensive Solr faceting parameters."""

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
