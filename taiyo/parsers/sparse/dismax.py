from pydantic import Field, computed_field, field_serializer

from taiyo.parsers.base import BaseQueryParser
from typing import Literal


from typing import Optional, Dict, List


class DisMaxQueryParser(BaseQueryParser):
    """DisMax (Disjunction Max) Query Parser for Apache Solr.

    The DisMax query parser is designed for user-friendly queries, providing an experience similar
    to popular search engines like Google. It handles queries gracefully even when they contain
    errors, making it ideal for end-user facing applications. DisMax distributes terms across
    multiple fields with individual boosts and combines results using disjunction max scoring.

    Solr Reference:
        https://solr.apache.org/guide/solr/latest/query-guide/dismax-query-parser.html

    Key Features:
        - Simplified query syntax (no need for field names)
        - Error-tolerant parsing
        - Multi-field search with individual field boosts (qf)
        - Phrase boosting for proximity matches (pf)
        - Minimum should match logic (mm)
        - Tie-breaker for scoring across fields
        - Boost queries and functions for result tuning

    How DisMax Scoring Works:
        The "tie" parameter controls how field scores are combined:
        - tie=0.0 (default): Only the highest scoring field contributes
        - tie=1.0: All field scores are summed
        - tie=0.1 (typical): Highest score + 0.1 * sum of other scores

    Examples:
        >>> # Basic multi-field search
        >>> parser = DisMaxQueryParser(
        ...     query="ipod",
        ...     query_fields={"name": 2.0, "features": 1.0, "text": 0.5}
        ... )

        >>> # With phrase boosting and minimum match
        >>> parser = DisMaxQueryParser(
        ...     query="belkin ipod",
        ...     query_fields={"name": 5.0, "text": 2.0},
        ...     phrase_fields={"name": 10.0, "text": 3.0},
        ...     phrase_slop=2,
        ...     min_match="75%"
        ... )

        >>> # With boost queries
        >>> parser = DisMaxQueryParser(
        ...     query="video",
        ...     query_fields={"features": 20.0, "text": 0.3},
        ...     boost_queries="cat:electronics^5.0"
        ... )

    Args:
        query: Main query string (user's search terms)
        alternate_query: Fallback query if q is not specified
        query_fields: Fields to search with boosts, e.g., {'title': 2.0, 'body': 1.0}
        query_slop: Phrase slop for explicit phrase queries in user input
        min_match: Minimum should match specification (e.g., '75%', '2<-25% 9<-3')
        phrase_fields: Fields for phrase boosting with boosts
        phrase_slop: Maximum position distance for phrase queries
        tie_breaker: Tie-breaker value (0.0 to 1.0) for multi-field scoring
        boost_queries: Additional queries to boost matching documents (additive)
        boost_functons: Function queries to boost scores (additive)

    Note:
        For multiplicative boosting (more predictable), use ExtendedDisMaxQueryParser
        with the boost parameter instead of bq/bf.

    See Also:
        - ExtendedDisMaxQueryParser: Enhanced version with additional features
        - StandardParser: For more precise Lucene syntax queries
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
    def def_type(self) -> Literal["dismax"]:
        return "dismax"

    @field_serializer("query_fields", "phrase_fields")
    def serialize_boost_terms(
        self, values: Optional[Dict[str, float]]
    ) -> Optional[str]:
        if values is None:
            return None
        return " ".join([f"{k}^{v}" for k, v in values.items()])
