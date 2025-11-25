"""Solr field and dynamic field definitions.

Provides models for defining fields in a Solr schema. Fields specify how
individual pieces of data are indexed, stored, and retrieved.

Fields reference field types to inherit their analysis and storage behavior,
while dynamic fields provide pattern-based field name matching for automatic
field creation.

Example:
    ```python
    from taiyo.schema import SolrField, SolrDynamicField

    # Regular field
    id_field = SolrField(
        name="id",
        type="string",
        indexed=True,
        stored=True,
        required=True
    )

    # Dynamic field for all *_txt fields
    text_dynamic = SolrDynamicField(
        name="*_txt",
        type="text_general",
        indexed=True,
        stored=True,
        multiValued=True
    )
    ```

Reference:
    https://solr.apache.org/guide/solr/latest/indexing-guide/fields.html
    https://solr.apache.org/guide/solr/latest/indexing-guide/dynamic-fields.html
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict


class SolrField(BaseModel):
    """Solr field definition specifying data indexing and storage behavior.

    Fields are named data containers that reference a field type to determine
    how their values are analyzed, indexed, and stored. Each field can override
    default behaviors inherited from its field type.

    Attributes:
        name: Field identifier (alphanumeric/underscore, no leading digit)
        type: Field type name (must reference a defined fieldType)
        default: Default value when not provided in documents
        indexed: Enable field in queries and sorting (default: true)
        stored: Store original value for retrieval (default: true)
        doc_values: Column-oriented storage for sorting/faceting (default: true)
        multi_valued: Allow multiple values per field (default: false)
        required: Reject documents missing this field (default: false)
        omit_norms: Disable length normalization (default: true for non-analyzed)
        omit_term_freq_and_positions: Omit term frequency and positions
        omit_positions: Omit positions but keep term frequency
        term_vectors: Store term vectors for highlighting (default: false)
        term_positions: Store term positions in vectors
        term_offsets: Store term offsets in vectors
        term_payloads: Store term payloads in vectors
        sort_missing_first: Sort docs without this field first
        sort_missing_last: Sort docs without this field last
        uninvertible: Allow un-inverting when indexed=true docValues=false
        use_doc_values_as_stored: Return docValues when using '*' in fl param
        large: Lazy load values >512KB (requires stored=true, multiValued=false)

    Example:
        ```python
        from taiyo.schema import SolrField

        # Unique ID field
        id_field = SolrField(
            name="id",
            type="string",
            indexed=True,
            stored=True,
            required=True
        )

        # Text field for full-text search
        title_field = SolrField(
            name="title",
            type="text_general",
            indexed=True,
            stored=True
        )

        # Multi-valued field
        tags_field = SolrField(
            name="tags",
            type="string",
            indexed=True,
            stored=True,
            multi_valued=True
        )

        # Field with docValues for faceting
        category_field = SolrField(
            name="category",
            type="string",
            indexed=True,
            stored=True,
            doc_values=True
        )

        # Numeric field with default value
        price_field = SolrField(
            name="price",
            type="pdouble",
            indexed=True,
            stored=True,
            default=0.0
        )

        # Version field (internal)
        version_field = SolrField(
            name="_version_",
            type="plong",
            indexed=False,
            stored=False
        )
        ```

    Reference:
        https://solr.apache.org/guide/solr/latest/indexing-guide/fields.html
    """

    name: str = Field(
        ...,
        description="Field name (alphanumeric or underscore, not starting with digit)",
    )
    type: str = Field(
        ..., description="Field type name (must reference a defined fieldType)"
    )
    default: Optional[Any] = Field(
        default=None, description="Default value if not provided in document"
    )
    indexed: Optional[bool] = Field(
        default=None,
        description="Whether the field can be used in queries (default: true)",
    )
    stored: Optional[bool] = Field(
        default=None,
        description="Whether the field value can be retrieved (default: true)",
    )
    doc_values: Optional[bool] = Field(
        default=None,
        alias="docValues",
        description="Column-oriented storage for sorting/faceting (default: true)",
    )
    multi_valued: Optional[bool] = Field(
        default=None,
        alias="multiValued",
        description="Whether field can contain multiple values (default: false)",
    )
    required: Optional[bool] = Field(
        default=None, description="Reject documents without this field (default: false)"
    )
    omit_norms: Optional[bool] = Field(
        default=None,
        alias="omitNorms",
        description="Disable length normalization (default: true for non-analyzed)",
    )
    omit_term_freq_and_positions: Optional[bool] = Field(
        default=None,
        alias="omitTermFreqAndPositions",
        description="Omit term frequency and positions from postings",
    )
    omit_positions: Optional[bool] = Field(
        default=None,
        alias="omitPositions",
        description="Omit positions but keep term frequency",
    )
    term_vectors: Optional[bool] = Field(
        default=None,
        alias="termVectors",
        description="Store term vectors (default: false)",
    )
    term_positions: Optional[bool] = Field(
        default=None,
        alias="termPositions",
        description="Store term positions in vectors",
    )
    term_offsets: Optional[bool] = Field(
        default=None, alias="termOffsets", description="Store term offsets in vectors"
    )
    term_payloads: Optional[bool] = Field(
        default=None, alias="termPayloads", description="Store term payloads in vectors"
    )
    sort_missing_first: Optional[bool] = Field(
        default=None,
        alias="sortMissingFirst",
        description="Sort documents without this field first (default: false)",
    )
    sort_missing_last: Optional[bool] = Field(
        default=None,
        alias="sortMissingLast",
        description="Sort documents without this field last (default: false)",
    )
    uninvertible: Optional[bool] = Field(
        default=None,
        description="Allow un-inverting at query time when indexed=true docValues=false",
    )
    use_doc_values_as_stored: Optional[bool] = Field(
        default=None,
        alias="useDocValuesAsStored",
        description="Return docValues as stored when matching '*' in fl param",
    )
    large: Optional[bool] = Field(
        default=None,
        description="Lazy load large values >512KB (requires stored=true, multiValued=false)",
    )

    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
    )

    def build(self, format: str = "xml", indent: str = "") -> Dict[str, Any] | str:
        """Build field definition in specified format.

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
        return self.model_dump(by_alias=True, exclude_none=True)

    def _to_xml(self, indent: str = "") -> str:
        """Serialize to XML for schema.xml."""
        attrs = []
        data = self.model_dump(by_alias=True, exclude_none=True)
        for key, value in data.items():
            if isinstance(value, bool):
                attrs.append(f'{key}="{str(value).lower()}"')
            else:
                attrs.append(f'{key}="{value}"')
        return f"{indent}<field {' '.join(attrs)}/>"


class SolrDynamicField(SolrField):
    """Dynamic field pattern for automatic field creation.

    Dynamic fields use wildcard patterns (* prefix or suffix) to automatically
    configure fields that match the pattern. When a document contains a field
    name matching a dynamic field pattern, Solr automatically creates and
    configures that field using the dynamic field's settings.

    Dynamic fields are particularly useful for:
    - Handling varying field names in semi-structured data
    - Supporting multi-language fields (e.g., title_en, title_fr)
    - Creating type-specific field groups (e.g., *_txt, *_i, *_dt)

    Attributes:
        name: Dynamic field pattern (e.g., '*_txt', '*_s', 'attr_*')
        type: Field type name (must reference a defined fieldType)
        ... (inherits all attributes from SolrField)

    Example:
        ```python
        from taiyo.schema import SolrDynamicField

        # Text fields with suffix pattern
        text_dynamic = SolrDynamicField(
            name="*_txt",
            type="text_general",
            indexed=True,
            stored=True,
            multi_valued=True
        )

        # String fields with suffix pattern
        string_dynamic = SolrDynamicField(
            name="*_s",
            type="string",
            indexed=True,
            stored=True,
            doc_values=True
        )

        # Integer fields with suffix pattern
        int_dynamic = SolrDynamicField(
            name="*_i",
            type="pint",
            indexed=True,
            stored=True,
            doc_values=True
        )

        # Date fields with suffix pattern
        date_dynamic = SolrDynamicField(
            name="*_dt",
            type="pdate",
            indexed=True,
            stored=True,
            doc_values=True
        )

        # Attribute fields with prefix pattern
        attr_dynamic = SolrDynamicField(
            name="attr_*",
            type="text_general",
            indexed=True,
            stored=True
        )

        # Ignored fields (no indexing or storage)
        ignored_dynamic = SolrDynamicField(
            name="ignored_*",
            type="string",
            indexed=False,
            stored=False
        )
        ```

    Note:
        - Patterns must contain exactly one asterisk (*)
        - Asterisk can be at beginning or end only
        - More specific patterns take precedence over less specific ones
        - If multiple patterns match, the longest match wins

    Reference:
        https://solr.apache.org/guide/solr/latest/indexing-guide/dynamic-fields.html
    """

    name: str = Field(
        ..., description="Dynamic field pattern (e.g., '*_txt', '*_s', 'attr_*')"
    )

    def _to_xml(self, indent: str = "") -> str:
        """Serialize to XML for schema.xml."""
        attrs = []
        data = self.model_dump(by_alias=True, exclude_none=True)
        for key, value in data.items():
            if isinstance(value, bool):
                attrs.append(f'{key}="{str(value).lower()}"')
            else:
                attrs.append(f'{key}="{value}"')
        return f"{indent}<dynamicField {' '.join(attrs)}/>"
