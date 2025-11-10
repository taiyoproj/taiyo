from typing import Optional, List, Union
from pydantic import Field, computed_field
from taiyo.params.configs.base import ParamsConfig


class GroupParamsConfig(ParamsConfig):
    """
    Solr Result Grouping parameters.
    https://solr.apache.org/guide/solr/latest/query-guide/result-grouping.html
    """

    field: Optional[Union[str, List[str]]] = Field(
        default=None,
        alias="group.field",
        description="Field(s) by which to group results. Must be single-valued and indexed.",
    )
    func: Optional[str] = Field(
        default=None,
        alias="group.func",
        description="Group based on unique values of a function query. Not supported in distributed searches.",
    )
    query: Optional[Union[str, List[str]]] = Field(
        default=None,
        alias="group.query",
        description="Return a group of documents matching the given query. Can be specified multiple times.",
    )
    limit: Optional[int] = Field(
        default=1,
        alias="group.limit",
        description="Number of results to return for each group. Default: 1.",
    )
    offset: Optional[int] = Field(
        default=None,
        alias="group.offset",
        description="Initial offset for the document list of each group.",
    )
    sort: Optional[str] = Field(
        default=None,
        alias="group.sort",
        description="How to sort documents within each group. Default: uses the sort parameter.",
    )
    format: Optional[str] = Field(
        default="grouped",
        alias="group.format",
        description="Format for grouped documents: 'grouped' (default) or 'simple'.",
    )
    main: Optional[bool] = Field(
        default=None,
        alias="group.main",
        description="If true, use the first field grouping as the main result list.",
    )
    ngroups: Optional[bool] = Field(
        default=False,
        alias="group.ngroups",
        description="If true, include the number of groups that matched the query. Default: false.",
    )
    truncate: Optional[bool] = Field(
        default=False,
        alias="group.truncate",
        description="If true, facet counts are based on the most relevant doc of each group. Default: false.",
    )
    facet: Optional[bool] = Field(
        default=False,
        alias="group.facet",
        description="Whether to compute grouped facets for the field facets specified in facet.field. Default: false.",
    )
    cache_percent: Optional[int] = Field(
        default=0,
        alias="group.cache.percent",
        description="Enable caching for result grouping. 0 disables. Default: 0.",
    )
