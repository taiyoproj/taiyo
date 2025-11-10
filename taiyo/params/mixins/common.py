from pydantic import Field
from typing import Optional, List, Union
from taiyo.params.mixins.base import ParamsMixin


class CommonParamsMixin(ParamsMixin):
    """
    Common query parameters:
    https://solr.apache.org/guide/solr/latest/query-guide/common-query-parameters.html
    """

    sort: Optional[str] = Field(
        default="score desc",
        description="Sort order for results (e.g., 'score desc', 'price asc'). Default: score desc.",
    )
    start: Optional[int] = Field(
        default=0, description="Offset into the result set for paging. Default: 0."
    )
    rows: Optional[int] = Field(
        default=10, description="Number of documents to return. Default: 10."
    )
    can_cancel: Optional[bool] = Field(
        default=False,
        alias="canCancel",
        description="Whether the query can be cancelled. Default: false.",
    )
    query_uuid: Optional[str] = Field(
        default=None,
        alias="queryUUID",
        description="Custom UUID for cancellable queries.",
    )
    filters: Optional[List[str]] = Field(
        default=None,
        alias="fq",
        description="Filter queries to restrict results. Can be specified multiple times.",
    )
    field_list: Optional[Union[str, list[str]]] = Field(
        default="*",
        alias="fl",
        description="Fields to return (comma- or space-separated, or list). Default: *.",
    )
    debug: Optional[Union[str, List[str]]] = Field(
        default=None,
        description="Debug options (e.g., 'query', 'timing', 'results', 'all').",
    )
    explain_other: Optional[str] = Field(
        default=None,
        alias="explainOther",
        description="Lucene query for additional explain info.",
    )
    partial_results: Optional[bool] = Field(
        default=True,
        alias="partialResults",
        description="Return partial results if a limit is reached. Default: true.",
    )
    time_allowed: Optional[int] = Field(
        default=None,
        alias="timeAllowed",
        description="Max time (ms) allowed for search.",
    )
    cpu_allowed: Optional[int] = Field(
        default=None,
        alias="cpuAllowed",
        description="Max CPU time (ms) allowed for search.",
    )
    max_hits_allowed: Optional[int] = Field(
        default=None,
        alias="maxHitsAllowed",
        description="Max number of hits to iterate through.",
    )
    mem_allowed: Optional[float] = Field(
        default=None,
        alias="memAllowed",
        description="Max memory (MiB) allowed for search thread.",
    )
    segment_terminate_early: Optional[bool] = Field(
        default=False,
        alias="segmentTerminateEarly",
        description="Enable early segment termination. Default: false.",
    )
    multi_threaded: Optional[bool] = Field(
        default=False,
        alias="multiThreaded",
        description="Allow multi-threaded search. Default: false.",
    )
    omit_header: Optional[bool] = Field(
        default=False,
        alias="omitHeader",
        description="Exclude header from results. Default: false.",
    )
    writer_type: Optional[str] = Field(
        default="json",
        description="Response writer type (e.g., 'json'). Default: json.",
    )
    log_params_list: Optional[str] = Field(
        default=None,
        alias="logParamsList",
        description="Comma-separated allowlist of parameter names to log.",
    )
    echo_params: Optional[str] = Field(
        default=None,
        alias="echoParams",
        description="Controls what request params are echoed in the response header ('explicit', 'all', 'none').",
    )
    min_exact_count: Optional[int] = Field(
        default=None,
        alias="minExactCount",
        description="Count hits exactly up to this value, then allow approximation.",
    )
