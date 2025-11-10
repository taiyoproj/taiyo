from pydantic import Field
from typing import Literal, Optional
from taiyo.parsers.sparse.base import SparseQueryParser


class StandardParser(SparseQueryParser):
    query: str = Field(
        ...,
        alias="q",
        description="Defines a query using standard query syntax. This parameter is mandatory.",
    )
    query_operator: Optional[Literal["AND", "OR"]] = Field(
        default=None,
        alias="q.op",
        description='Specifies the default operator for query expressions. Possible values are "AND" or "OR".',
    )
    default_field: Optional[str] = Field(
        default=None, alias="df", description="Specifies a default searchable field."
    )
    split_on_whitespace: Optional[bool] = Field(
        default=None,
        alias="sow",
        description="Split on whitespace. If true, analyze each whitespace-separated term separately.",
    )
