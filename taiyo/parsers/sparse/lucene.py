from pydantic import Field
from typing import Literal, Optional
from taiyo.parsers.base import BaseQueryParser


class StandardParser(BaseQueryParser):
    """Standard Query Parser (Lucene syntax) for Apache Solr.

    The Standard Query Parser is Solr's default query parser, supporting full Lucene query syntax
    including field-specific searches, boolean operators, wildcards, proximity searches, range queries,
    boosting, and fuzzy searches. It offers greater precision but requires more exact syntax.

    Solr Reference:
        https://solr.apache.org/guide/solr/latest/query-guide/standard-query-parser.html

    Features:
        - Field-specific queries: title:"The Right Way" AND text:go
        - Boolean operators: AND, OR, NOT, +, -
        - Wildcards: te?t, test*, *esting
        - Proximity searches: "jakarta apache"~10
        - Range queries: [1 TO 5], {A TO Z}
        - Boosting: jakarta^4 apache
        - Fuzzy searches: roam~0.8
        - Grouping with parentheses: (jakarta OR apache) AND website
        - Constant score queries: description:blue^=1.0

    Examples:
        >>> # Basic field search
        >>> parser = StandardParser(query="title:Solr AND content:search")

        >>> # Range query
        >>> parser = StandardParser(query="price:[10 TO 100]")

        >>> # Proximity search
        >>> parser = StandardParser(query='"apache solr"~5')

        >>> # With default field and operator
        >>> parser = StandardParser(
        ...     query="apache solr",
        ...     default_field="content",
        ...     query_operator="AND"
        ... )

    Args:
        query: Query string using Lucene syntax (required)
        query_operator: Default operator ("AND" or "OR"). Determines how multiple terms are combined
        default_field: Default field to search when no field is specified
        split_on_whitespace: If True, analyze each term separately; if False (default),
            analyze term sequences together for multi-word synonyms and shingles

    See Also:
        - DisMaxQueryParser: For user-friendly queries with error tolerance
        - ExtendedDisMaxQueryParser: For advanced user queries combining Lucene syntax with DisMax features
    """

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
