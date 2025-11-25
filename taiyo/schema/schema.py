"""Solr schema definition and management.

Provides the top-level Schema model that combines all schema components
(fields, field types, copy fields) into a complete schema definition that
can be serialized to either XML (schema.xml) or JSON (Schema API).

The Schema model serves as the root container for all schema elements and
handles serialization to Solr-compatible formats.

Example:
    ```python
    from taiyo.schema import (
        Schema, SolrField, SolrDynamicField,
        SolrFieldType, SolrFieldClass, CopyField
    )
    from taiyo.schema.field_type import Analyzer, Tokenizer, Filter

    # Build complete schema
    schema = Schema(
        name="my_schema",
        version=1.6,
        uniqueKey="id",
        fields=[...],
        dynamicFields=[...],
        fieldTypes=[...],
        copyFields=[...]
    )

    # Serialize to XML
    xml_output = schema.build(format="xml")

    # Serialize to JSON for Schema API
    json_output = schema.build(format="json")
    ```

Reference:
    https://solr.apache.org/guide/solr/latest/indexing-guide/schema-elements.html
    https://solr.apache.org/guide/solr/latest/indexing-guide/schema-api.html
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict

from .field import SolrField as SolrField, SolrDynamicField
from .field_type import SolrFieldType
from .copy_field import CopyField


class Schema(BaseModel):
    """Complete Solr schema definition with all components.

    A Schema represents the complete structure of a Solr collection, defining
    how documents are indexed, stored, and searched. It combines field definitions,
    field types, copy field directives, and configuration into a single model
    that can be serialized to XML or JSON.

    The Schema supports both:
    - Classic schema.xml format (XML serialization)
    - Schema API format (JSON serialization)

    Attributes:
        name: Optional schema name identifier
        version: Schema version number (typically 1.6 for modern Solr)
        uniqueKey: Field name to use as unique document identifier (commonly 'id')
        fields: List of field definitions
        dynamicFields: List of dynamic field patterns
        fieldTypes: List of field type definitions
        copyFields: List of copy field directives

    Example:
        ```python
        from taiyo.schema import (
            Schema, SolrField, SolrDynamicField,
            SolrFieldType, SolrFieldClass, CopyField
        )
        from taiyo.schema.field_type import Analyzer, Tokenizer, Filter

        # Define field types
        text_type = SolrFieldType(
            name="text_general",
            solr_class=SolrFieldClass.TEXT,
            position_increment_gap=100,
            analyzer=Analyzer(
                tokenizer=Tokenizer(name="standard"),
                filters=[
                    Filter(name="lowercase"),
                    Filter(name="stop", words="stopwords.txt")
                ]
            )
        )

        # Define fields
        id_field = SolrField(
            name="id",
            type="string",
            indexed=True,
            stored=True,
            required=True
        )

        title_field = SolrField(
            name="title",
            type="text_general",
            indexed=True,
            stored=True
        )

        # Define dynamic fields
        text_dynamic = SolrDynamicField(
            name="*_txt",
            type="text_general",
            indexed=True,
            stored=True
        )

        # Define copy fields
        title_copy = CopyField(source="title", dest="text")

        # Build complete schema
        schema = Schema(
            name="my_collection",
            version=1.6,
            uniqueKey="id",
            fields=[id_field, title_field],
            dynamicFields=[text_dynamic],
            fieldTypes=[text_type],
            copyFields=[title_copy]
        )

        # Serialize to XML for schema.xml
        xml_output = schema.build(format="xml")
        with open("schema.xml", "w") as f:
            f.write(xml_output)

        # Serialize to JSON for Schema API
        json_output = schema.build(format="json")

        # Use builder pattern
        schema = (
            Schema(name="my_schema", version=1.6, uniqueKey="id")
            .add_field_type(text_type)
            .add_field(id_field)
            .add_field(title_field)
            .add_dynamic_field(text_dynamic)
            .add_copy_field(title_copy)
        )
        ```

    Reference:
        https://solr.apache.org/guide/solr/latest/indexing-guide/schema-elements.html
        https://solr.apache.org/guide/solr/latest/indexing-guide/schema-api.html
    """

    name: Optional[str] = Field(default=None, description="Schema name (optional)")
    version: Optional[float] = Field(default=None, description="Schema version number")
    uniqueKey: Optional[str] = Field(
        default=None, description="Field name to use as unique key (commonly 'id')"
    )

    fields: List[SolrField] = Field(
        default_factory=list, description="Field definitions"
    )
    dynamicFields: List[SolrDynamicField] = Field(
        default_factory=list, description="Dynamic field patterns"
    )
    fieldTypes: List[SolrFieldType] = Field(
        default_factory=list, description="Field type definitions"
    )
    copyFields: List[CopyField] = Field(
        default_factory=list, description="Copy field directives"
    )

    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
    )

    def build(self, format: str = "xml") -> Dict[str, Any] | str:
        """Build schema in specified format.

        Args:
            format: Output format - "xml" (default) or "json"

        Returns:
            XML string for format="xml", dict for format="json"
        """
        match format:
            case "json":
                return self._to_dict()
            case "xml":
                return self._to_xml()
            case _:
                raise ValueError(f"Invalid format: {format}. Use 'xml' or 'json'.")

    def _to_dict(self) -> Dict[str, Any]:
        """Serialize into dictionary."""
        data = self.model_dump(by_alias=True, exclude_none=True)
        return {
            k: v for k, v in data.items() if not (isinstance(v, list) and len(v) == 0)
        }

    def _to_xml(self) -> str:
        """
        Serialize to XML for schema.xml.

        Returns a complete schema.xml document that can be used
        with classic Solr configuration.
        """
        lines = ['<?xml version="1.0" encoding="UTF-8"?>']

        # Schema root element
        attrs = []
        if self.name:
            attrs.append(f'name="{self.name}"')
        if self.version:
            attrs.append(f'version="{self.version}"')

        if attrs:
            lines.append(f"<schema {' '.join(attrs)}>")
        else:
            lines.append("<schema>")

        # Unique key
        if self.uniqueKey:
            lines.append(f"  <uniqueKey>{self.uniqueKey}</uniqueKey>")
            lines.append("")

        # Field types
        if self.fieldTypes:
            lines.append("  <!-- Field Types -->")
            for ft in self.fieldTypes:
                result = ft.build(format="xml", indent="  ")
                assert isinstance(result, str)
                lines.append(result)
            lines.append("")

        # Fields
        if self.fields:
            lines.append("  <!-- Fields -->")
            for f in self.fields:
                result = f.build(format="xml", indent="  ")
                assert isinstance(result, str)
                lines.append(result)
            lines.append("")

        # Dynamic fields
        if self.dynamicFields:
            lines.append("  <!-- Dynamic Fields -->")
            for df in self.dynamicFields:
                result = df.build(format="xml", indent="  ")
                assert isinstance(result, str)
                lines.append(result)
            lines.append("")

        # Copy fields
        if self.copyFields:
            lines.append("  <!-- Copy Fields -->")
            for cf in self.copyFields:
                result = cf.build(format="xml", indent="  ")
                assert isinstance(result, str)
                lines.append(result)
            lines.append("")

        lines.append("</schema>")

        return "\n".join(lines)

    def add_field(self, field: SolrField) -> "Schema":
        """Add a field to the schema (builder pattern)."""
        self.fields.append(field)
        return self

    def add_dynamic_field(self, field: SolrDynamicField) -> "Schema":
        """Add a dynamic field to the schema (builder pattern)."""
        self.dynamicFields.append(field)
        return self

    def add_field_type(self, field_type: SolrFieldType) -> "Schema":
        """Add a field type to the schema (builder pattern)."""
        self.fieldTypes.append(field_type)
        return self

    def add_copy_field(self, copy_field: CopyField) -> "Schema":
        """Add a copy field to the schema (builder pattern)."""
        self.copyFields.append(copy_field)
        return self
