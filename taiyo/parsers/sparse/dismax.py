from pydantic import Field, computed_field, field_serializer

from taiyo.parsers.base import BaseQueryParser
from typing import Literal


from typing import Optional, Dict, List


class DisMaxQueryParser(BaseQueryParser):
    """
    DisMaxQueryParser processes user queries using the DisMax (Disjunction Max) algorithm.
    It supports simplified query syntax and distributes terms across multiple fields with boosts.
    """

    query: Optional[str] = Field(
        default=None, alias="q", description="Main query string."
    )
    alternate_query: Optional[str] = Field(
        default=None,
        alias="q.alt",
        description="Alternate query if q is not specified.",
    )
    query_fields: Optional[Dict[str, float]] = Field(
        default=None,
        alias="qf",
        description="Query fields with boosts, e.g., {'title': 2.0, 'body': 1.0}.",
    )
    query_slop: Optional[int] = Field(
        default=None, alias="qs", description="Slop for query fields."
    )
    min_match: Optional[str] = Field(
        default=None,
        alias="mm",
        description="Minimum should match, e.g., '75%', '2<-25% 9<-3'.",
    )
    phrase_fields: Optional[Dict[str, float]] = Field(
        default=None, alias="pf", description="Phrase fields with boosts."
    )
    phrase_slop: Optional[int] = Field(
        default=None, alias="ps", description="Slop for phrase fields."
    )
    tie_breaker: float = Field(
        default=0.0, alias="tie", description="Tie breaker value."
    )
    boost_queries: Optional[str | List[str]] = Field(
        default=None, alias="bq", description="List of boost queries."
    )
    boost_functons: Optional[str | List[str]] = Field(
        default=None, alias="bf", description="List of boost functions."
    )

    @computed_field(alias="defType")
    @property
    def def_type(self) -> Literal["dismax"]:
        return "dismax"

    @field_serializer("query_fields", "phrase_fields")
    def serialize_boost_terms(values) -> str:
        return " ".join([f"{k}^{v}" for k, v in values.items()])
