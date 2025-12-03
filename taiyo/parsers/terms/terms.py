from typing import Optional, Literal, Any, Dict
from pydantic import Field, computed_field
from taiyo.parsers.base import BaseQueryParser


class TermsQueryParser(BaseQueryParser):
    """
    Terms Query Parser for Apache Solr.

    The Terms Query Parser generates a query from multiple comma-separated values,
    matching documents where the specified field contains any of the provided terms.
    It's optimized for efficiently searching for multiple discrete values in a field,
    particularly useful for filtering by IDs, tags, or categories.

    Solr Reference:
        https://solr.apache.org/guide/solr/latest/query-guide/other-parsers.html#terms-query-parser

    Key Features:
        - Efficient multi-value term matching
        - Configurable separator for term parsing
        - Multiple query implementation methods with different performance characteristics
        - Optimized for large numbers of terms
        - Works with both regular and docValues fields

    Query Implementation Methods:
        - termsFilter (default): Uses BooleanQuery or TermInSetQuery based on term count.
          Scales well with index size and moderately with number of terms.
        - booleanQuery: Creates a BooleanQuery. Scales well with index size but
          poorly with many terms.
        - automaton: Uses automaton-based matching. Good for certain use cases.
        - docValuesTermsFilter: For docValues fields. Automatically chooses between
          per-segment or top-level implementation.
        - docValuesTermsFilterPerSegment: Per-segment docValues filtering.
        - docValuesTermsFilterTopLevel: Top-level docValues filtering.

    Performance Considerations:
        - Use termsFilter (default) for general cases
        - Use booleanQuery for small term sets with large indices
        - Use docValues methods only on fields with docValues enabled
        - Term count affects which internal implementation is chosen

    Examples:
        >>> # Basic usage - search for multiple tags (as filter)
        >>> parser = TermsQueryParser(
        ...     field="tags",
        ...     terms=["software", "apache", "solr", "lucene"]
        ... )

        >>> # With custom query field
        >>> parser = TermsQueryParser(
        ...     field="tags",
        ...     terms=["python", "java", "rust"],
        ...     query="status:active"
        ... )

        >>> # Using space separator with category IDs
        >>> parser = TermsQueryParser(
        ...     field="categoryId",
        ...     terms=["8", "6", "7", "5309"],
        ...     separator=" ",
        ...     method="booleanQuery"
        ... )

        >>> # Filtering by product IDs
        >>> parser = TermsQueryParser(
        ...     field="product_id",
        ...     terms=["P123", "P456", "P789", "P012"]
        ... )

        >>> # Using with docValues field
        >>> parser = TermsQueryParser(
        ...     field="author_id",
        ...     terms=["author1", "author2", "author3"],
        ...     method="docValuesTermsFilter"
        ... )

        >>> # Building query params for use with any Solr client
        >>> params = parser.build()
        >>> # {'q': '*:*', 'fq': '{!terms f=tags}software,apache,solr,lucene'}

    Args:
        field: The field name to search (required)
        terms: List of terms to match (required)
        query: Optional main query string (default: '*:*'). The terms filter is applied as fq.
        separator: Character(s) to use for joining terms (default: ',').
                  Use ' ' (single space) if you want space-separated terms.
        method: Query implementation method. Options:
                - termsFilter (default): Automatic choice between implementations
                - booleanQuery: Boolean query approach
                - automaton: Automaton-based matching
                - docValuesTermsFilter: Auto-select docValues approach
                - docValuesTermsFilterPerSegment: Per-segment docValues
                - docValuesTermsFilterTopLevel: Top-level docValues

    Returns:
        Documents where the specified field contains any of the provided terms

    Note:
        When using docValues methods, ensure the target field has docValues enabled
        in the schema. The cache parameter defaults to false for docValues methods.

    See Also:
        - StandardParser: For Lucene syntax queries with field specifications
        - DisMaxQueryParser: For multi-field user-friendly queries
    """

    query: str = Field(
        "*:*",
        alias="q",
        description="Optional main query string (default: '*:*'). The terms filter is applied as fq.",
    )
    field: str = Field(
        ..., alias="f", exclude=True, description="The field name to search (required)"
    )
    terms: list[str] = Field(
        ..., exclude=True, description="List of terms to match (required)"
    )
    separator: str = Field(
        ",",
        exclude=True,
        description="Character(s) to use for joining terms (default: ','). Use ' ' (single space) if you want space-separated terms.",
    )
    method: Optional[
        Literal[
            "termsFilter",
            "booleanQuery",
            "automaton",
            "docValuesTermsFilter",
            "docValuesTermsFilterPerSegment",
            "docValuesTermsFilterTopLevel",
        ]
    ] = Field(
        default=None,
        alias="method",
        description="Query implementation method. Options: termsFilter (default), booleanQuery, automaton, docValuesTermsFilter, docValuesTermsFilterPerSegment, docValuesTermsFilterTopLevel.",
    )

    def build(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        params = super().build(*args, **kwargs)
        params.setdefault("q", self.query)
        return params

    @computed_field(alias="fq")
    def filter_query(self) -> str | list[str]:
        opts = [f"f={self.field}"]
        if self.method:
            opts.append(f"method={self.method}")

        fq = f"{{!terms {' '.join(opts)}}}{self.separator.join(self.terms)}"
        if self.filters:
            # Return a new list: all filters + terms filter
            return list(self.filters) + [fq]
        else:
            return fq
