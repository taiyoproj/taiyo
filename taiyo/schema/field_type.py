"""
Solr Field Type and Analyzer definitions
"""

from typing import Any, Optional, Literal, Union, List, Dict
from pydantic import BaseModel, Field, ConfigDict, field_validator
from .enums import (
    SolrFieldClass,
    SolrTokenizerFactory,
    SolrFilterFactory,
    SolrCharFilterFactory,
)


class CharFilter(BaseModel):
    """
    Character filter for text analysis.

    Applied before tokenization to preprocess text.

    Example:
        ```python
        from taiyo.schema.enums import SolrCharFilterFactory

        # Using enum
        char_filter = CharFilter(
            solr_class=SolrCharFilterFactory.PATTERN_REPLACE,
            pattern="([a-zA-Z])\\\\1+",
            replacement="$1$1"
        )

        # Or using string
        char_filter = CharFilter(
            name="patternReplace",
            pattern="([a-zA-Z])\\\\1+",
            replacement="$1$1"
        )
        ```
    """

    name: Optional[str] = Field(
        default=None, description="Filter name (e.g., 'patternReplace', 'htmlStrip')"
    )
    solr_class: Optional[Union[SolrCharFilterFactory, str]] = Field(
        default=None,
        alias="class",
        description="Char filter class (enum or string, e.g., SolrCharFilterFactory.HTML_STRIP or 'solr.HTMLStripCharFilterFactory')",
    )

    @field_validator("solr_class", mode="before")
    @classmethod
    def validate_class(cls, v: Any) -> Any:
        """Accept both enum and string values."""
        if isinstance(v, SolrCharFilterFactory):
            return v.value
        return v

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
    )

    def build(self, format: str = "xml") -> Dict[str, Any]:
        """Build char filter definition.

        Args:
            format: Output format - only "json" supported for components

        Returns:
            dict representation
        """
        return self._to_dict()

    def _to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        data = self.model_dump(by_alias=True, exclude_none=True, exclude_unset=True)
        if hasattr(self, "__pydantic_extra__") and self.__pydantic_extra__:
            data.update(self.__pydantic_extra__)
        return data


class Tokenizer(BaseModel):
    """
    Tokenizer for text analysis.

    Splits text into tokens.

    Example:
        ```python
        from taiyo.schema.enums import SolrTokenizerFactory

        # Using enum
        tokenizer = Tokenizer(solr_class=SolrTokenizerFactory.STANDARD)

        # Or using name
        tokenizer = Tokenizer(name="standard")

        # Or using string class
        tokenizer = Tokenizer(solr_class="solr.StandardTokenizerFactory")
        ```
    """

    name: Optional[str] = Field(
        default=None,
        description="Tokenizer name (e.g., 'standard', 'whitespace', 'keyword')",
    )
    solr_class: Optional[Union[SolrTokenizerFactory, str]] = Field(
        default=None,
        alias="class",
        description="Tokenizer class (enum or string, e.g., SolrTokenizerFactory.STANDARD or 'solr.StandardTokenizerFactory')",
    )

    @field_validator("solr_class", mode="before")
    @classmethod
    def validate_class(cls, v: Any) -> Any:
        """Accept both enum and string values."""
        if isinstance(v, SolrTokenizerFactory):
            return v.value
        return v

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",  # Allow additional parameters
    )

    def build(self, format: str = "xml") -> Dict[str, Any]:
        """Build tokenizer definition.

        Args:
            format: Output format - only "json" supported for components

        Returns:
            dict representation
        """
        return self._to_dict()

    def _to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        data = self.model_dump(by_alias=True, exclude_none=True, exclude_unset=True)
        if hasattr(self, "__pydantic_extra__") and self.__pydantic_extra__:
            data.update(self.__pydantic_extra__)
        return data


class Filter(BaseModel):
    """
    Token filter for text analysis.

    Applied after tokenization to transform tokens.

    Example:
        ```python
        from taiyo.schema.enums import SolrFilterFactory

        # Using enum
        filter = Filter(solr_class=SolrFilterFactory.LOWER_CASE)

        # Using name
        filter = Filter(name="lowercase")

        # With parameters using enum
        filter = Filter(
            solr_class=SolrFilterFactory.STOP,
            ignore_case=True,
            words="stopwords.txt"
        )

        # With parameters using name
        filter = Filter(
            name="stop",
            ignore_case=True,
            words="stopwords.txt"
        )
        ```
    """

    name: Optional[str] = Field(
        default=None,
        description="Filter name (e.g., 'lowercase', 'stop', 'snowballPorter')",
    )
    solr_class: Optional[Union[SolrFilterFactory, str]] = Field(
        default=None,
        alias="class",
        description="Filter class (enum or string, e.g., SolrFilterFactory.LOWER_CASE or 'solr.LowerCaseFilterFactory')",
    )

    @field_validator("solr_class", mode="before")
    @classmethod
    def validate_class(cls, v: Any) -> Any:
        """Accept both enum and string values."""
        if isinstance(v, SolrFilterFactory):
            return v.value
        return v

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",  # Allow additional parameters
    )

    def build(self, format: str = "xml") -> Dict[str, Any]:
        """Build filter definition.

        Args:
            format: Output format - only "json" supported for components

        Returns:
            dict representation
        """
        return self._to_dict()

    def _to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        data = self.model_dump(by_alias=True, exclude_none=True, exclude_unset=True)
        if hasattr(self, "__pydantic_extra__") and self.__pydantic_extra__:
            data.update(self.__pydantic_extra__)
        return data


class Analyzer(BaseModel):
    """
    Analyzer configuration for field types.

    Defines how text is processed for indexing and querying.

    Example:
        ```python
        analyzer = Analyzer(
            tokenizer=Tokenizer(name="standard"),
            filters=[
                Filter(name="lowercase"),
                Filter(name="stop", ignore_case=True, words="stopwords.txt")
            ]
        )
        ```
    """

    type: Optional[Literal["index", "query", "multiterm"]] = Field(
        default=None, description="Analyzer type (index, query, or multiterm)"
    )
    solr_class: Optional[str] = Field(
        default=None,
        alias="class",
        description="Analyzer class (e.g., 'solr.TokenizerChain')",
    )
    char_filters: Optional[List[CharFilter]] = Field(
        default=None,
        alias="charFilters",
        description="Character filters applied before tokenization",
    )
    tokenizer: Optional[Tokenizer] = Field(
        default=None, description="Tokenizer for splitting text"
    )
    filters: Optional[List[Filter]] = Field(
        default=None, description="Token filters applied after tokenization"
    )

    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
    )

    def build(self, format: str = "xml", indent: str = "  ") -> Dict[str, Any] | str:
        """Build analyzer definition in specified format.

        Args:
            format: Output format - "xml" (default) or "json"
            indent: Indentation prefix for XML output

        Returns:
            XML string for format="xml", dict for format="json"
        """
        match format:
            case "json":
                return self._to_dict()
            case "xml":
                return self._to_xml(indent=indent)
            case _:
                raise ValueError(f"Invalid format: {format}. Use 'xml' or 'json'.")

    def _to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for JSON Schema API."""
        result: Dict[str, Any] = {}

        if self.solr_class:
            result["class"] = self.solr_class

        if self.char_filters:
            result["charFilters"] = [cf._to_dict() for cf in self.char_filters]

        if self.tokenizer:
            result["tokenizer"] = self.tokenizer._to_dict()

        if self.filters:
            result["filters"] = [f._to_dict() for f in self.filters]

        return result

    def _to_xml(self, indent: str = "  ") -> str:
        """Serialize to XML for schema.xml."""
        lines = []
        type_attr = f' type="{self.type}"' if self.type else ""
        class_attr = f' class="{self.solr_class}"' if self.solr_class else ""
        lines.append(f"{indent}<analyzer{type_attr}{class_attr}>")

        # Character filters
        if self.char_filters:
            for cf in self.char_filters:
                attrs = []
                data = cf._to_dict()
                for key, value in data.items():
                    if isinstance(value, bool):
                        attrs.append(f'{key}="{str(value).lower()}"')
                    else:
                        attrs.append(f'{key}="{value}"')
                lines.append(f"{indent}  <charFilter {' '.join(attrs)}/>")

        # Tokenizer
        if self.tokenizer:
            attrs = []
            data = self.tokenizer._to_dict()
            for key, value in data.items():
                if isinstance(value, bool):
                    attrs.append(f'{key}="{str(value).lower()}"')
                else:
                    attrs.append(f'{key}="{value}"')
            lines.append(f"{indent}  <tokenizer {' '.join(attrs)}/>")

        # Filters
        if self.filters:
            for f in self.filters:
                attrs = []
                data = f._to_dict()
                for key, value in data.items():
                    if isinstance(value, bool):
                        attrs.append(f'{key}="{str(value).lower()}"')
                    else:
                        attrs.append(f'{key}="{value}"')
                lines.append(f"{indent}  <filter {' '.join(attrs)}/>")

        lines.append(f"{indent}</analyzer>")
        return "\n".join(lines)


class SolrFieldType(BaseModel):
    """
    Represents a Solr field type definition.

    Field types define how data is analyzed and stored.

    Example:
        ```python
        from taiyo.schema import SolrFieldType, Analyzer, Tokenizer, Filter
        from taiyo.schema.enums import (
            SolrFieldClass,
            SolrTokenizerFactory,
            SolrFilterFactory
        )

        # Using enums (recommended)
        field_type = SolrFieldType(
            name="text_general",
            solr_class=SolrFieldClass.TEXT,
            position_increment_gap=100,
            analyzer=Analyzer(
                tokenizer=Tokenizer(solr_class=SolrTokenizerFactory.STANDARD),
                filters=[
                    Filter(solr_class=SolrFilterFactory.LOWER_CASE),
                    Filter(solr_class=SolrFilterFactory.STOP, ignore_case=True, words="stopwords.txt")
                ]
            )
        )

        # Or using strings (also supported)
        field_type = SolrFieldType(
            name="text_general",
            solr_class="solr.TextField",
            position_increment_gap=100,
            analyzer=Analyzer(
                tokenizer=Tokenizer(name="standard"),
                filters=[
                    Filter(name="lowercase"),
                    Filter(name="stop", ignore_case=True, words="stopwords.txt")
                ]
            )
        )
        ```

    Reference: https://solr.apache.org/guide/solr/latest/indexing-guide/field-type-definitions-and-properties.html
    """

    name: str = Field(..., description="Field type name")
    solr_class: Union[SolrFieldClass, str] = Field(
        ...,
        alias="class",
        description="Field type class (enum or string, e.g., SolrFieldClass.TEXT or 'solr.TextField')",
    )

    @field_validator("solr_class", mode="before")
    @classmethod
    def validate_field_class(cls, v: Any) -> Any:
        """Accept both enum and string values."""
        if isinstance(v, SolrFieldClass):
            return v.value
        return v

    analyzer: Optional[Union[Analyzer, Dict[str, Analyzer]]] = Field(
        default=None,
        description="Analyzer configuration (single or separate index/query/multiterm)",
    )
    index_analyzer: Optional[Analyzer] = Field(
        default=None, alias="indexAnalyzer", description="Analyzer for indexing"
    )
    query_analyzer: Optional[Analyzer] = Field(
        default=None, alias="queryAnalyzer", description="Analyzer for querying"
    )
    multiterm_analyzer: Optional[Analyzer] = Field(
        default=None,
        alias="multitermAnalyzer",
        description="Analyzer for multiterm queries",
    )

    position_increment_gap: Optional[int] = Field(
        default=None,
        alias="positionIncrementGap",
        description="Gap for multi-valued fields (default: 0)",
    )
    auto_generate_phrase_queries: Optional[bool] = Field(
        default=None,
        alias="autoGeneratePhraseQueries",
        description="Generate phrase queries automatically",
    )
    synonym_query_style: Optional[
        Literal["as_same_term", "pick_best", "as_distinct_terms"]
    ] = Field(
        default=None,
        alias="synonymQueryStyle",
        description="How to combine synonym scores",
    )
    enable_graph_queries: Optional[bool] = Field(
        default=None,
        alias="enableGraphQueries",
        description="Enable graph-aware query processing (default: true for text)",
    )
    doc_values_format: Optional[str] = Field(
        default=None, alias="docValuesFormat", description="Custom DocValuesFormat"
    )
    postings_format: Optional[str] = Field(
        default=None, alias="postingsFormat", description="Custom PostingsFormat"
    )

    indexed: Optional[bool] = None
    stored: Optional[bool] = None
    doc_values: Optional[bool] = Field(default=None, alias="docValues")
    sort_missing_first: Optional[bool] = Field(default=None, alias="sortMissingFirst")
    sort_missing_last: Optional[bool] = Field(default=None, alias="sortMissingLast")
    multi_valued: Optional[bool] = Field(default=None, alias="multiValued")
    uninvertible: Optional[bool] = None
    omit_norms: Optional[bool] = Field(default=None, alias="omitNorms")
    omit_term_freq_and_positions: Optional[bool] = Field(
        default=None, alias="omitTermFreqAndPositions"
    )
    omit_positions: Optional[bool] = Field(default=None, alias="omitPositions")
    term_vectors: Optional[bool] = Field(default=None, alias="termVectors")
    term_positions: Optional[bool] = Field(default=None, alias="termPositions")
    term_offsets: Optional[bool] = Field(default=None, alias="termOffsets")
    term_payloads: Optional[bool] = Field(default=None, alias="termPayloads")
    required: Optional[bool] = None
    use_doc_values_as_stored: Optional[bool] = Field(
        default=None, alias="useDocValuesAsStored"
    )
    large: Optional[bool] = None

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",  # Allow additional parameters for specific field types
    )

    def build(self, format: str = "xml", indent: str = "") -> Dict[str, Any] | str:
        """Build field type definition in specified format.

        Args:
            format: Output format - "xml" (default) or "json"
            indent: Indentation prefix for XML output

        Returns:
            XML string for format="xml", dict for format="json"
        """
        match format:
            case "json":
                return self._to_dict()
            case "xml":
                return self._to_xml(indent=indent)
            case _:
                raise ValueError(f"Invalid format: {format}. Use 'xml' or 'json'.")

    def _to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for JSON Schema API."""
        class_name = (
            self.solr_class.value
            if isinstance(self.solr_class, SolrFieldClass)
            else self.solr_class
        )
        result: Dict[str, Any] = {"name": self.name, "class": class_name}

        # Add analyzer configurations
        if self.analyzer:
            if isinstance(self.analyzer, dict):
                result["analyzer"] = {k: v._to_dict() for k, v in self.analyzer.items()}
            else:
                result["analyzer"] = self.analyzer._to_dict()

        if self.index_analyzer:
            result["indexAnalyzer"] = self.index_analyzer._to_dict()

        if self.query_analyzer:
            result["queryAnalyzer"] = self.query_analyzer._to_dict()

        if self.multiterm_analyzer:
            result["multitermAnalyzer"] = self.multiterm_analyzer._to_dict()

        # Add other properties
        data = self.model_dump(
            by_alias=True,
            exclude_none=True,
            exclude={
                "name",
                "solr_class",
                "analyzer",
                "index_analyzer",
                "query_analyzer",
                "multiterm_analyzer",
            },
        )
        result.update(data)

        # Add extra fields
        if hasattr(self, "__pydantic_extra__") and self.__pydantic_extra__:
            result.update(self.__pydantic_extra__)

        return result

    def _to_xml(self, indent: str = "") -> str:
        """Serialize to XML for schema.xml."""
        lines = []

        # Build attributes
        class_name = (
            self.solr_class.value
            if isinstance(self.solr_class, SolrFieldClass)
            else self.solr_class
        )
        attrs = [f'name="{self.name}"', f'class="{class_name}"']

        # Add simple properties as attributes
        simple_props = self.model_dump(
            by_alias=True,
            exclude_none=True,
            exclude={
                "name",
                "solr_class",
                "analyzer",
                "index_analyzer",
                "query_analyzer",
                "multiterm_analyzer",
            },
        )
        for key, value in simple_props.items():
            if isinstance(value, bool):
                attrs.append(f'{key}="{str(value).lower()}"')
            elif not isinstance(value, (dict, list)):
                attrs.append(f'{key}="{value}"')

        # Check if we have analyzers (need multi-line format)
        has_analyzers = any(
            [
                self.analyzer,
                self.index_analyzer,
                self.query_analyzer,
                self.multiterm_analyzer,
            ]
        )

        if has_analyzers:
            lines.append(f"{indent}<fieldType {' '.join(attrs)}>")

            # Add analyzers
            if self.analyzer:
                if isinstance(self.analyzer, dict):
                    for analyzer in self.analyzer.values():
                        lines.append(analyzer._to_xml(indent=indent + "  "))
                else:
                    lines.append(self.analyzer._to_xml(indent=indent + "  "))

            if self.index_analyzer:
                lines.append(self.index_analyzer._to_xml(indent=indent + "  "))

            if self.query_analyzer:
                lines.append(self.query_analyzer._to_xml(indent=indent + "  "))

            if self.multiterm_analyzer:
                lines.append(self.multiterm_analyzer._to_xml(indent=indent + "  "))

            lines.append(f"{indent}</fieldType>")
        else:
            # Self-closing tag
            lines.append(f"{indent}<fieldType {' '.join(attrs)}/>")

        return "\n".join(lines)
