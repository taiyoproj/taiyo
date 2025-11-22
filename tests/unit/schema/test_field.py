"""Tests for SolrField and SolrDynamicField schema components."""

import pytest
from taiyo.schema import SolrField, SolrDynamicField


def test_solr_field_basic():
    """Test basic field creation with required attributes."""
    field = SolrField(name="title", type="text_general")

    assert field.name == "title"
    assert field.type == "text_general"
    assert field.indexed is None
    assert field.stored is None


def test_solr_field_with_all_attributes():
    """Test field with all boolean attributes."""
    field = SolrField(
        name="id",
        type="string",
        indexed=True,
        stored=True,
        required=True,
        multi_valued=False,
        doc_values=True,
    )

    assert field.name == "id"
    assert field.type == "string"
    assert field.indexed is True
    assert field.stored is True
    assert field.required is True
    assert field.multi_valued is False
    assert field.doc_values is True


def test_solr_field_with_default_value():
    """Test field with default value."""
    field = SolrField(name="status", type="string", default="active")

    assert field.name == "status"
    assert field.default == "active"


def test_solr_field_to_dict():
    """Test field JSON serialization."""
    field = SolrField(
        name="title",
        type="text_general",
        indexed=True,
        stored=True,
    )
    result = field.build(format="json")

    assert result == {
        "name": "title",
        "type": "text_general",
        "indexed": True,
        "stored": True,
    }


def test_solr_field_to_dict_excludes_none():
    """Test field JSON serialization excludes None values."""
    field = SolrField(name="title", type="text_general")
    result = field.build(format="json")

    assert result == {"name": "title", "type": "text_general"}
    assert "indexed" not in result
    assert "stored" not in result


def test_solr_field_to_xml():
    """Test field XML serialization."""
    field = SolrField(name="id", type="string", indexed=True, stored=True)
    xml = field.build(format="xml")

    assert "<field" in xml
    assert 'name="id"' in xml
    assert 'type="string"' in xml
    assert 'indexed="true"' in xml
    assert 'stored="true"' in xml
    assert "/>" in xml


def test_solr_field_to_xml_with_indent():
    """Test field XML serialization with indentation."""
    field = SolrField(name="id", type="string")
    xml = field.build(format="xml", indent="  ")

    assert xml.startswith("  <field")


def test_solr_field_to_xml_boolean_lowercase():
    """Test field XML serialization converts booleans to lowercase."""
    field = SolrField(name="id", type="string", required=True, multi_valued=False)
    xml = field.build(format="xml")

    assert 'required="true"' in xml
    assert 'multiValued="false"' in xml


def test_solr_field_camel_case_aliases():
    """Test field supports camelCase aliases."""
    field = SolrField(
        name="title",
        type="text_general",
        docValues=True,
        multiValued=True,
        omitNorms=False,
    )

    assert field.doc_values is True
    assert field.multi_valued is True
    assert field.omit_norms is False


def test_solr_field_term_vector_options():
    """Test field with term vector options."""
    field = SolrField(
        name="content",
        type="text_general",
        term_vectors=True,
        term_positions=True,
        term_offsets=True,
        term_payloads=False,
    )

    assert field.term_vectors is True
    assert field.term_positions is True
    assert field.term_offsets is True
    assert field.term_payloads is False


def test_solr_field_sort_options():
    """Test field with sort missing options."""
    field = SolrField(
        name="price",
        type="pdouble",
        sort_missing_first=False,
        sort_missing_last=True,
    )

    assert field.sort_missing_first is False
    assert field.sort_missing_last is True


def test_solr_field_invalid_format():
    """Test field with invalid format raises error."""
    field = SolrField(name="title", type="text_general")

    with pytest.raises(ValueError, match="Invalid format"):
        field.build(format="yaml")


def test_dynamic_field_basic():
    """Test basic dynamic field creation."""
    field = SolrDynamicField(name="*_txt", type="text_general")

    assert field.name == "*_txt"
    assert field.type == "text_general"


def test_dynamic_field_suffix_pattern():
    """Test dynamic field with suffix wildcard pattern."""
    field = SolrDynamicField(
        name="*_s",
        type="string",
        indexed=True,
        stored=True,
    )

    assert field.name == "*_s"
    assert field.type == "string"


def test_dynamic_field_prefix_pattern():
    """Test dynamic field with prefix wildcard pattern."""
    field = SolrDynamicField(
        name="attr_*",
        type="text_general",
        indexed=True,
        stored=True,
    )

    assert field.name == "attr_*"


def test_dynamic_field_to_xml():
    """Test dynamic field XML serialization."""
    field = SolrDynamicField(
        name="*_txt",
        type="text_general",
        indexed=True,
        stored=True,
    )
    xml = field.build(format="xml")

    assert "<dynamicField" in xml
    assert 'name="*_txt"' in xml
    assert 'type="text_general"' in xml
    assert 'indexed="true"' in xml


def test_dynamic_field_inherits_from_solr_field():
    """Test that SolrDynamicField inherits all SolrField attributes."""
    field = SolrDynamicField(
        name="*_i",
        type="pint",
        doc_values=True,
        multi_valued=False,
        required=False,
    )

    assert field.doc_values is True
    assert field.multi_valued is False
    assert field.required is False


def test_dynamic_field_to_dict():
    """Test dynamic field JSON serialization."""
    field = SolrDynamicField(
        name="*_txt",
        type="text_general",
        indexed=True,
        multi_valued=True,
    )
    result = field.build(format="json")

    assert result["name"] == "*_txt"
    assert result["type"] == "text_general"
    assert result["indexed"] is True
    assert result["multiValued"] is True
