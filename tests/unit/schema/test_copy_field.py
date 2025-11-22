"""Tests for CopyField schema component."""

import pytest
from taiyo.schema import CopyField


def test_copy_field_basic():
    """Test basic copy field creation."""
    copy_field = CopyField(source="title", dest="text")

    assert copy_field.source == "title"
    assert copy_field.dest == "text"
    assert copy_field.max_chars is None


def test_copy_field_with_max_chars():
    """Test copy field with character limit."""
    copy_field = CopyField(source="content", dest="summary", max_chars=500)

    assert copy_field.source == "content"
    assert copy_field.dest == "summary"
    assert copy_field.max_chars == 500


def test_copy_field_with_wildcard_source():
    """Test copy field with wildcard source pattern."""
    copy_field = CopyField(source="*_txt", dest="text")

    assert copy_field.source == "*_txt"
    assert copy_field.dest == "text"


def test_copy_field_to_dict():
    """Test copy field JSON serialization."""
    copy_field = CopyField(source="title", dest="text")
    result = copy_field.build(format="json")

    assert result == {"source": "title", "dest": "text"}


def test_copy_field_to_dict_with_max_chars():
    """Test copy field JSON serialization with maxChars."""
    copy_field = CopyField(source="content", dest="summary", max_chars=1000)
    result = copy_field.build(format="json")

    assert result == {"source": "content", "dest": "summary", "maxChars": 1000}


def test_copy_field_to_xml():
    """Test copy field XML serialization."""
    copy_field = CopyField(source="title", dest="text")
    xml = copy_field.build(format="xml")

    assert xml == '<copyField source="title" dest="text"/>'


def test_copy_field_to_xml_with_indent():
    """Test copy field XML serialization with indentation."""
    copy_field = CopyField(source="title", dest="text")
    xml = copy_field.build(format="xml", indent="  ")

    assert xml == '  <copyField source="title" dest="text"/>'


def test_copy_field_to_xml_with_max_chars():
    """Test copy field XML serialization with maxChars."""
    copy_field = CopyField(source="content", dest="summary", max_chars=500)
    xml = copy_field.build(format="xml")

    assert xml == '<copyField source="content" dest="summary" maxChars="500"/>'


def test_copy_field_invalid_format():
    """Test copy field with invalid format raises error."""
    copy_field = CopyField(source="title", dest="text")

    with pytest.raises(ValueError, match="Invalid format"):
        copy_field.build(format="invalid")


def test_copy_field_alias_support():
    """Test copy field supports camelCase alias for maxChars."""
    copy_field = CopyField(source="title", dest="text", maxChars=100)

    assert copy_field.max_chars == 100
