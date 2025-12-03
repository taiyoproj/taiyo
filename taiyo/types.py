from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, List, Optional, TypeVar, Generic, Union


def _coerce_int(value: Any) -> int:
    """Best-effort conversion of Solr facet counts into integers."""

    if isinstance(value, bool):
        return int(value)

    if isinstance(value, (int, float)):
        return int(value)

    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            try:
                return int(float(value))
            except ValueError:
                return 0

    return 0


class SolrDocument(BaseModel):
    """Base model for Solr documents."""

    model_config = ConfigDict(extra="allow")


DocumentT = TypeVar("DocumentT", bound=SolrDocument)


InterestingTermsType = Union[List[Any], Dict[str, Any]]


class SolrFacetFieldValue(BaseModel):
    """Single entry inside a field facet result."""

    value: Any
    count: int
    extra: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(populate_by_name=True, validate_by_name=True)


class SolrFacetFieldResult(BaseModel):
    """Parsed representation of a single field facet."""

    buckets: List[SolrFacetFieldValue] = Field(default_factory=list)
    missing: Optional[int] = None
    num_buckets: Optional[int] = Field(default=None, alias="numBuckets")
    metadata: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(populate_by_name=True, validate_by_name=True)


class SolrFacetRangeBucket(BaseModel):
    """Single bucket inside a range facet."""

    value: Any
    count: int
    extra: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(populate_by_name=True, validate_by_name=True)


class SolrFacetRangeResult(BaseModel):
    """Parsed representation of a range facet."""

    buckets: List[SolrFacetRangeBucket] = Field(default_factory=list)
    gap: Optional[Any] = None
    start: Optional[Any] = None
    end: Optional[Any] = None
    before: Optional[int] = None
    after: Optional[int] = None
    between: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(populate_by_name=True, validate_by_name=True)


class SolrJsonFacetBucket(BaseModel):
    """Single bucket from Solr JSON Facet API responses."""

    value: Any
    count: int
    metrics: Dict[str, Any] = Field(default_factory=dict)
    facets: Dict[str, "SolrJsonFacetNode"] = Field(default_factory=dict)

    model_config = ConfigDict(populate_by_name=True, validate_by_name=True)


class SolrJsonFacetNode(BaseModel):
    """Recursive representation of JSON facet responses."""

    count: Optional[int] = None
    missing: Optional[int] = None
    buckets: List[SolrJsonFacetBucket] = Field(default_factory=list)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    facets: Dict[str, "SolrJsonFacetNode"] = Field(default_factory=dict)

    model_config = ConfigDict(populate_by_name=True, validate_by_name=True)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SolrJsonFacetNode":
        buckets: List[SolrJsonFacetBucket] = []
        raw_buckets = data.get("buckets")

        if isinstance(raw_buckets, list):
            for bucket in raw_buckets:
                if not isinstance(bucket, dict):
                    continue

                bucket_metrics: Dict[str, Any] = {}
                bucket_facets: Dict[str, SolrJsonFacetNode] = {}

                for key, value in bucket.items():
                    if key in {"val", "count"}:
                        continue
                    if isinstance(value, dict) and (
                        "buckets" in value or "count" in value
                    ):
                        bucket_facets[key] = cls.from_dict(value)
                    else:
                        bucket_metrics[key] = value

                buckets.append(
                    SolrJsonFacetBucket(
                        value=bucket.get("val"),
                        count=_coerce_int(bucket.get("count")),
                        metrics=bucket_metrics,
                        facets=bucket_facets,
                    )
                )

        metrics: Dict[str, Any] = {}
        facets: Dict[str, SolrJsonFacetNode] = {}

        for key, value in data.items():
            if key in {"count", "missing", "buckets"}:
                continue

            if isinstance(value, dict) and ("buckets" in value or "count" in value):
                facets[key] = cls.from_dict(value)
            else:
                metrics[key] = value

        return cls(
            count=data.get("count"),
            missing=data.get("missing"),
            buckets=buckets,
            metrics=metrics,
            facets=facets,
        )


class SolrFacetResult(BaseModel):
    """Structured Solr facet response supporting classic and JSON facet APIs."""

    queries: Dict[str, int] = Field(default_factory=dict)
    fields: Dict[str, SolrFacetFieldResult] = Field(default_factory=dict)
    ranges: Dict[str, SolrFacetRangeResult] = Field(default_factory=dict)
    intervals: Dict[str, Any] = Field(default_factory=dict)
    pivots: Dict[str, Any] = Field(default_factory=dict)
    heatmaps: Dict[str, Any] = Field(default_factory=dict)
    json_facets: Optional[SolrJsonFacetNode] = None

    model_config = ConfigDict(populate_by_name=True, validate_by_name=True)

    @classmethod
    def from_response(cls, response: Dict[str, Any]) -> Optional["SolrFacetResult"]:
        legacy = response.get("facet_counts")
        json_facets = response.get("facets")

        parsed_legacy = legacy if isinstance(legacy, dict) else {}
        parsed_json = json_facets if isinstance(json_facets, dict) else {}

        if not parsed_legacy and not parsed_json:
            return None

        facet_counts = cls()

        # facet queries
        raw_queries = parsed_legacy.get("facet_queries") if parsed_legacy else {}
        if isinstance(raw_queries, dict):
            facet_counts.queries = {
                str(key): _coerce_int(value)
                for key, value in raw_queries.items()
                if value is not None
            }

        # facet fields
        raw_fields = parsed_legacy.get("facet_fields") if parsed_legacy else {}
        if isinstance(raw_fields, dict):
            for field_name, raw_field in raw_fields.items():
                parsed_field = SolrFacetResult._parse_field_facet(raw_field)
                facet_counts.fields[field_name] = parsed_field

        # facet ranges
        raw_ranges = parsed_legacy.get("facet_ranges") if parsed_legacy else {}
        if isinstance(raw_ranges, dict):
            for range_name, raw_range in raw_ranges.items():
                parsed_range = SolrFacetResult._parse_range_facet(raw_range)
                facet_counts.ranges[range_name] = parsed_range

        # direct passthrough structures
        for attr, key in (
            ("intervals", "facet_intervals"),
            ("pivots", "facet_pivot"),
            ("heatmaps", "facet_heatmaps"),
        ):
            raw_section = parsed_legacy.get(key) if parsed_legacy else {}
            if isinstance(raw_section, dict):
                setattr(facet_counts, attr, raw_section)

        if parsed_json:
            facet_counts.json_facets = SolrJsonFacetNode.from_dict(parsed_json)

        return facet_counts

    @staticmethod
    def _parse_field_facet(raw_field: Any) -> SolrFacetFieldResult:
        buckets: List[SolrFacetFieldValue] = []
        missing: Optional[int] = None
        num_buckets: Optional[int] = None
        metadata: Dict[str, Any] = {}

        if isinstance(raw_field, list):
            if raw_field and isinstance(raw_field[0], list):
                for entry in raw_field:
                    if not isinstance(entry, list) or not entry:
                        continue
                    value = entry[0]
                    count = _coerce_int(entry[1]) if len(entry) > 1 else 0
                    extra_payload = (
                        entry[2]
                        if len(entry) > 2 and isinstance(entry[2], dict)
                        else {}
                    )
                    buckets.append(
                        SolrFacetFieldValue(
                            value=value, count=count, extra=extra_payload
                        )
                    )
            else:
                for index in range(0, len(raw_field), 2):
                    value = raw_field[index]
                    count = raw_field[index + 1] if index + 1 < len(raw_field) else 0
                    buckets.append(
                        SolrFacetFieldValue(value=value, count=_coerce_int(count))
                    )
        elif isinstance(raw_field, dict):
            for key, value in raw_field.items():
                if key == "missing":
                    missing = _coerce_int(value)
                    continue
                if key == "numBuckets":
                    num_buckets = _coerce_int(value)
                    continue

                if isinstance(value, dict):
                    count = _coerce_int(value.get("count"))
                    extra_payload = {k: v for k, v in value.items() if k != "count"}
                    buckets.append(
                        SolrFacetFieldValue(
                            value=key,
                            count=count,
                            extra=extra_payload,
                        )
                    )
                else:
                    buckets.append(
                        SolrFacetFieldValue(value=key, count=_coerce_int(value))
                    )
        else:
            metadata["raw"] = raw_field

        return SolrFacetFieldResult(
            buckets=buckets,
            missing=missing,
            num_buckets=num_buckets,
            metadata=metadata,
        )

    @staticmethod
    def _parse_range_facet(raw_range: Any) -> SolrFacetRangeResult:
        buckets: List[SolrFacetRangeBucket] = []
        gap: Optional[Any] = None
        start: Optional[Any] = None
        end: Optional[Any] = None
        before: Optional[int] = None
        after: Optional[int] = None
        between: Optional[int] = None
        metadata: Dict[str, Any] = {}

        if isinstance(raw_range, dict):
            counts = raw_range.get("counts")
            if isinstance(counts, list):
                if counts and isinstance(counts[0], list):
                    for entry in counts:
                        if not entry:
                            continue
                        value = entry[0]
                        count = _coerce_int(entry[1]) if len(entry) > 1 else 0
                        extra_payload = (
                            entry[2]
                            if len(entry) > 2 and isinstance(entry[2], dict)
                            else {}
                        )
                        buckets.append(
                            SolrFacetRangeBucket(
                                value=value, count=count, extra=extra_payload
                            )
                        )
                else:
                    for index in range(0, len(counts), 2):
                        value = counts[index]
                        count = counts[index + 1] if index + 1 < len(counts) else 0
                        buckets.append(
                            SolrFacetRangeBucket(value=value, count=_coerce_int(count))
                        )
            gap = raw_range.get("gap")
            start = raw_range.get("start")
            end = raw_range.get("end")
            if "before" in raw_range:
                before = _coerce_int(raw_range.get("before"))
            if "after" in raw_range:
                after = _coerce_int(raw_range.get("after"))
            if "between" in raw_range:
                between = _coerce_int(raw_range.get("between"))

            for key in [
                "hardend",
                "other",
                "within",
                "include",
                "mean",
            ]:
                if key in raw_range:
                    metadata[key] = raw_range[key]
        else:
            metadata["raw"] = raw_range

        return SolrFacetRangeResult(
            buckets=buckets,
            gap=gap,
            start=start,
            end=end,
            before=before,
            after=after,
            between=between,
            metadata=metadata,
        )


class SolrMoreLikeThisResult(BaseModel, Generic[DocumentT]):
    """BaseModel for MoreLikeThis matches."""

    num_found: int = Field(default=0, alias="numFound")
    start: int = 0
    num_found_exact: Optional[bool] = Field(default=None, alias="numFoundExact")
    docs: List[DocumentT] = Field(default_factory=list)
    interesting_terms: Optional[InterestingTermsType] = None

    model_config = ConfigDict(populate_by_name=True, validate_by_name=True)


class SolrResponse(BaseModel, Generic[DocumentT]):
    """Model representing a Solr response."""

    status: int
    query_time: int = Field(alias="qtime")
    num_found: int = Field(alias="numFound")
    start: int = 0
    docs: List[DocumentT]
    facets: Optional[SolrFacetResult] = None
    highlighting: Optional[Dict[str, Dict[str, List[str]]]] = None
    more_like_this: Optional[Dict[str, SolrMoreLikeThisResult[DocumentT]]] = Field(
        default=None, alias="moreLikeThis"
    )
    grouping: Optional[SolrGroupingResult] = None

    model_config = ConfigDict(populate_by_name=True, validate_by_name=True)


class SolrError(Exception):
    """Base exception for Solr-related errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class SolrGroup(BaseModel):
    """
    Represents a single group in a Solr grouping response.

    Fields:
        group_value: The value of the group (e.g., the field value grouped by).
        doclist: Document list and metadata for this group, including:
            - numFound: Number of documents in this group.
            - start: Offset of the first document in this group.
            - docs: List of documents in this group.
        group_offset: Optional offset for the document list of this group (from group.offset param).
    """

    group_value: Optional[Any] = Field(
        default=None,
        alias="groupValue",
        description="The value of the group (e.g., the field value grouped by)",
    )
    doclist: Dict[str, Any] = Field(
        description="Document list and metadata for this group, including numFound, start, docs"
    )
    group_offset: Optional[int] = Field(
        default=None,
        description="Offset for the document list of this group (from group.offset param)",
    )


class SolrGroupedField(BaseModel):
    """
    Represents the grouping result for a single field or query.

    Fields:
        matches: Number of matching documents for this group field or query.
        groups: List of groups for this field (present for field grouping).
        doclist: Document list for this group (present for query grouping).
        ngroups: Number of groups that matched the query (if group.ngroups=true).
        facet: Facet counts for this group (if group.facet=true).
    """

    matches: int = Field(
        description="Number of matching documents for this group field or query"
    )
    groups: Optional[List[SolrGroup]] = Field(
        default=None,
        description="List of groups for this field (present for field grouping)",
    )
    doclist: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Document list for this group (present for query grouping)",
    )
    ngroups: Optional[int] = Field(
        default=None,
        description="Number of groups that matched the query (if group.ngroups=true)",
    )
    facet: Optional[Dict[str, Any]] = Field(
        default=None, description="Facet counts for this group (if group.facet=true)"
    )


class SolrGroupingResult(BaseModel):
    """
    Top-level model for Solr grouping responses.

    Fields:
        grouped: Dictionary mapping group field names or queries to their grouping results.
        group_sort: Sort order for groups (from group.sort param).
        group_limit: Number of results to return for each group (from group.limit param).
        group_offset: Initial offset for the document list of each group (from group.offset param).
        group_format: Format of the grouping response (from group.format param).
        distributed_caveats: Notes about distributed grouping limitations.
    """

    grouped: Dict[str, SolrGroupedField] = Field(
        description="Dictionary mapping group field names or queries to their grouping results"
    )
    group_sort: Optional[str] = Field(
        default=None, description="Sort order for groups (from group.sort param)"
    )
    group_limit: Optional[int] = Field(
        default=None,
        description="Number of results to return for each group (from group.limit param)",
    )
    group_offset: Optional[int] = Field(
        default=None,
        description="Initial offset for the document list of each group (from group.offset param)",
    )
    group_format: Optional[str] = Field(
        default=None,
        description="Format of the grouping response (from group.format param)",
    )
    distributed_caveats: Optional[str] = Field(
        default=None, description="Notes about distributed grouping limitations"
    )
