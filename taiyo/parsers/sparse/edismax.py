from pydantic import Field, computed_field
from taiyo.parsers.sparse.dismax import DisMaxQueryParser
from typing import Literal


from typing import Optional, Dict


class ExtendedDisMaxQueryParser(DisMaxQueryParser):
    """Extended DisMax (eDisMax) Query Parser for Apache Solr.

    The Extended DisMax (eDisMax) query parser is an improved version of DisMax that handles
    full Lucene query syntax while maintaining error tolerance. It's the most flexible parser
    for user-facing search applications, combining the precision of the Standard parser with
    the user-friendliness of DisMax.

    Solr Reference:
        https://solr.apache.org/guide/solr/latest/query-guide/edismax-query-parser.html

    Key Enhancements over DisMax:
        - Full Lucene query syntax support (field names, boolean operators, wildcards)
        - Automatic mm (minimum match) adjustment when stopwords are removed
        - Lowercase operator support ("and", "or" as operators)
        - Bigram (pf2) and trigram (pf3) phrase boosting
        - Multiplicative boosting via boost parameter
        - Fine-grained control over stopword handling
        - User field restrictions (uf) for security

    Advanced Phrase Boosting:
        - pf: Standard phrase fields (all query terms)
        - pf2: Bigram phrase fields (word pairs)
        - pf3: Trigram phrase fields (word triplets)
        Each has independent slop control (ps, ps2, ps3)

    Examples:
        >>> # Basic eDisMax query with Lucene syntax
        >>> parser = ExtendedDisMaxQueryParser(
        ...     query="title:solr OR (content:search AND type:guide)",
        ...     query_fields={"title": 2.0, "content": 1.0}
        ... )

        >>> # Multi-level phrase boosting
        >>> parser = ExtendedDisMaxQueryParser(
        ...     query="apache solr search",
        ...     query_fields={"title": 5.0, "body": 1.0},
        ...     phrase_fields={"title": 50.0},  # All 3 words
        ...     phrase_fields_bigram={"title": 20.0},  # 2-word phrases
        ...     phrase_fields_trigram={"title": 30.0},  # 3-word phrases
        ...     phrase_slop=2,
        ...     phrase_slop_bigram=1
        ... )

        >>> # With field aliasing and restrictions
        >>> parser = ExtendedDisMaxQueryParser(
        ...     query="name:Mike sysadmin",
        ...     query_fields={"title": 1.0, "text": 1.0},
        ...     user_fields=["title", "text", "last_name", "first_name"]
        ... )

        >>> # With automatic mm relaxation
        >>> parser = ExtendedDisMaxQueryParser(
        ...     query="the quick brown fox",
        ...     query_fields={"content": 1.0, "title": 2.0},
        ...     min_match="75%",
        ...     min_match_auto_relax=True  # Adjust if stopwords removed
        ... )

    Args:
        split_on_whitespace: If True, analyze each term separately; if False (default),
            analyze term sequences for multi-word synonyms
        min_match_auto_relax: Auto-relax mm when stopwords are removed unevenly
        lowercase_operators: Treat lowercase 'and'/'or' as boolean operators
        phrase_fields_bigram: Fields for bigram phrase boosting (pf2)
        phrase_slop_bigram: Slop for bigram phrases (ps2)
        phrase_fields_trigram: Fields for trigram phrase boosting (pf3)
        phrase_slop_trigram: Slop for trigram phrases (ps3)
        stopwords: If False, ignore StopFilterFactory in query analyzer
        user_fields: Whitelist of fields users can explicitly query (uf parameter)

    Inherits from DisMaxQueryParser:
        query, alternate_query, query_fields, min_match, phrase_fields,
        phrase_slop, tie_breaker, boost_queries, boost_functons

    Note:
        The eDisMax default mm behavior differs from DisMax:
        - mm=0% if query contains explicit operators (-, +, OR, NOT) or q.op=OR
        - mm=100% if q.op=AND and query only uses AND operators

    See Also:
        - DisMaxQueryParser: Simpler version without Lucene syntax support
        - StandardParser: For pure Lucene syntax without DisMax features
    """

    split_on_whitespace: Optional[bool] = Field(
        default=None,
        description="Split on whitespace. If true, analyze each whitespace-separated term separately.",
    )
    min_match_auto_relax: Optional[bool] = Field(
        default=None,
        alias="mm.autoRelax",
        description="Automatically relax mm if clauses are removed by stopwords.",
    )
    lowercase_operators: Optional[bool] = Field(
        default=None,
        alias="lowercaseOperators",
        description="Treat lowercase 'and'/'or' as operators.",
    )
    phrase_fields_bigram: Optional[Dict[str, float]] = Field(
        default=None, description="Phrase fields for bigrams with boosts."
    )
    phrase_slop_bigram: Optional[int] = Field(
        default=None, description="Slop for bigram phrase fields."
    )
    phrase_fields_trigram: Optional[Dict[str, float]] = Field(
        default=None, description="Phrase fields for trigrams with boosts."
    )
    phrase_slop_trigram: Optional[int] = Field(
        default=None, description="Slop for trigram phrase fields."
    )
    stopwords: Optional[bool] = Field(
        default=None, description="Respect stopword filter in analyzer."
    )
    user_fields: Optional[list[str]] = Field(
        default=None, description="User fields allowed for explicit query."
    )

    @computed_field(alias="defType")
    def def_type(self) -> Literal["edismax"]:  # type: ignore[override]
        return "edismax"
