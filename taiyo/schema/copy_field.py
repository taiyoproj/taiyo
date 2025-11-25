"""Solr copyField directive definitions.

Provides models for defining copy field directives that automatically copy
data from one field to another at index time.

Copy fields are useful for:
- Creating catch-all search fields
- Indexing the same content with different analysis
- Supporting multiple query strategies on the same data
- Building facet or highlight fields from source fields

Example:
    ```python
    from taiyo.schema import CopyField

    # Copy title to catch-all text field
    copy = CopyField(source="title", dest="text")

    # Copy with wildcard pattern
    copy_all_text = CopyField(source="*_txt", dest="text")

    # Copy with character limit
    copy_summary = CopyField(
        source="content",
        dest="content_summary",
        maxChars=1000
    )
    ```

Reference:
    https://solr.apache.org/guide/solr/latest/indexing-guide/copy-fields.html
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict


class CopyField(BaseModel):
    """Solr copyField directive for automatic field data copying.

    Copy fields instruct Solr to automatically copy data from a source field
    (or pattern) to a destination field during indexing. The destination field
    receives the original pre-analyzed text, which is then analyzed according
    to its own field type.

    This enables:
    - Catch-all search fields aggregating multiple source fields
    - Same content analyzed differently for different purposes
    - Faceting on different field types than used for searching
    - Creating summary fields with character limits

    Attributes:
        source: Source field name (supports wildcards like '*_txt' or 'attr_*')
        dest: Destination field name (must be a defined field, no wildcards)
        maxChars: Optional character limit for copied content (truncates if exceeded)

    Example:
        ```python
        from taiyo.schema import CopyField

        # Copy single field to catch-all
        title_copy = CopyField(source="title", dest="text")
        content_copy = CopyField(source="content", dest="text")

        # Copy all text fields with wildcard
        all_text_copy = CopyField(source="*_txt", dest="text")

        # Copy with character limit for summaries
        summary_copy = CopyField(
            source="content",
            dest="content_summary",
            maxChars=500
        )

        # Copy for different analysis
        # (e.g., stemmed text to unstemmed for exact phrase matching)
        exact_copy = CopyField(source="description", dest="description_exact")

        # Copy multiple dynamic fields
        multi_lang_copy = CopyField(source="title_*", dest="title_all")
        ```

    Note:
        - Copies happen before analysis of the destination field
        - Destination field must be defined (cannot be dynamic)
        - Wildcards only work in source, not destination
        - maxChars truncates at character boundary, may split words
        - Copying is one-way; changes to dest don't affect source

    Reference:
        https://solr.apache.org/guide/solr/latest/indexing-guide/copy-fields.html
    """

    source: str = Field(
        ..., description="Source field name (supports wildcards like '*_txt')"
    )
    dest: str = Field(
        ..., description="Destination field name (must be a defined field)"
    )
    max_chars: Optional[int] = Field(
        default=None,
        alias="maxChars",
        description="Maximum characters to copy (truncates if exceeded)",
    )

    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
    )

    def build(self, format: str = "xml", indent: str = "") -> Dict[str, Any] | str:
        """Build copy field definition in specified format.

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
        return self.model_dump(by_alias=True, exclude_none=True, exclude_unset=True)

    def _to_xml(self, indent: str = "") -> str:
        """Serialize to XML for schema.xml."""
        attrs = [f'source="{self.source}"', f'dest="{self.dest}"']

        if self.max_chars is not None:
            attrs.append(f'maxChars="{self.max_chars}"')

        return f"{indent}<copyField {' '.join(attrs)}/>"
