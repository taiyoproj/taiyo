"""Tests for Schema component."""

import pytest
from taiyo.schema import (
    Schema,
    SolrField,
    SolrDynamicField,
    SolrFieldType,
    SolrFieldClass,
    CopyField,
)
from taiyo.schema.field_type import Analyzer, Tokenizer, Filter


def test_schema_basic():
    """Test basic schema creation."""
    schema = Schema()

    assert schema.name is None
    assert schema.version is None
    assert schema.uniqueKey is None
    assert len(schema.fields) == 0
    assert len(schema.fieldTypes) == 0


def test_schema_with_metadata():
    """Test schema with name, version, and uniqueKey."""
    schema = Schema(
        name="my_schema",
        version=1.6,
        uniqueKey="id",
    )

    assert schema.name == "my_schema"
    assert schema.version == 1.6
    assert schema.uniqueKey == "id"


def test_schema_with_fields():
    """Test schema with field definitions."""
    schema = Schema(
        fields=[
            SolrField(name="id", type="string", required=True),
            SolrField(name="title", type="text_general"),
        ]
    )

    assert len(schema.fields) == 2
    assert schema.fields[0].name == "id"
    assert schema.fields[1].name == "title"


def test_schema_with_field_types():
    """Test schema with field type definitions."""
    schema = Schema(
        fieldTypes=[
            SolrFieldType(name="pint", solr_class=SolrFieldClass.INT_POINT),
            SolrFieldType(name="text_general", solr_class=SolrFieldClass.TEXT),
        ]
    )

    assert len(schema.fieldTypes) == 2
    assert schema.fieldTypes[0].name == "pint"
    assert schema.fieldTypes[1].name == "text_general"


def test_schema_with_dynamic_fields():
    """Test schema with dynamic field patterns."""
    schema = Schema(
        dynamicFields=[
            SolrDynamicField(name="*_txt", type="text_general"),
            SolrDynamicField(name="*_s", type="string"),
        ]
    )

    assert len(schema.dynamicFields) == 2
    assert schema.dynamicFields[0].name == "*_txt"


def test_schema_with_copy_fields():
    """Test schema with copy field directives."""
    schema = Schema(
        copyFields=[
            CopyField(source="title", dest="text"),
            CopyField(source="content", dest="text"),
        ]
    )

    assert len(schema.copyFields) == 2
    assert schema.copyFields[0].source == "title"


def test_schema_to_dict():
    """Test schema JSON serialization."""
    schema = Schema(
        name="test_schema",
        version=1.6,
        uniqueKey="id",
        fields=[SolrField(name="id", type="string")],
    )
    result = schema.build(format="json")

    assert result["name"] == "test_schema"
    assert result["version"] == 1.6
    assert result["uniqueKey"] == "id"
    assert len(result["fields"]) == 1


def test_schema_to_dict_excludes_empty_lists():
    """Test schema JSON serialization excludes empty lists."""
    schema = Schema(
        name="test_schema",
        fields=[SolrField(name="id", type="string")],
    )
    result = schema.build(format="json")

    assert "fields" in result
    assert "dynamicFields" not in result
    assert "fieldTypes" not in result
    assert "copyFields" not in result


def test_schema_to_xml_basic():
    """Test basic schema XML serialization."""
    schema = Schema()
    xml = schema.build(format="xml")

    assert '<?xml version="1.0" encoding="UTF-8"?>' in xml
    assert "<schema>" in xml
    assert "</schema>" in xml


def test_schema_to_xml_with_attributes():
    """Test schema XML serialization with name and version."""
    schema = Schema(name="my_schema", version=1.6)
    xml = schema.build(format="xml")

    assert '<schema name="my_schema" version="1.6">' in xml


def test_schema_to_xml_with_unique_key():
    """Test schema XML serialization with uniqueKey."""
    schema = Schema(uniqueKey="id")
    xml = schema.build(format="xml")

    assert "<uniqueKey>id</uniqueKey>" in xml


def test_schema_to_xml_with_fields():
    """Test schema XML serialization with fields."""
    schema = Schema(
        fields=[
            SolrField(name="id", type="string", required=True),
            SolrField(name="title", type="text_general"),
        ]
    )
    xml = schema.build(format="xml")

    assert "<!-- Fields -->" in xml
    assert '<field name="id"' in xml
    assert '<field name="title"' in xml


def test_schema_to_xml_with_field_types():
    """Test schema XML serialization with field types."""
    schema = Schema(
        fieldTypes=[
            SolrFieldType(name="pint", solr_class=SolrFieldClass.INT_POINT),
        ]
    )
    xml = schema.build(format="xml")

    assert "<!-- Field Types -->" in xml
    assert '<fieldType name="pint"' in xml


def test_schema_to_xml_with_dynamic_fields():
    """Test schema XML serialization with dynamic fields."""
    schema = Schema(
        dynamicFields=[
            SolrDynamicField(name="*_txt", type="text_general"),
        ]
    )
    xml = schema.build(format="xml")

    assert "<!-- Dynamic Fields -->" in xml
    assert '<dynamicField name="*_txt"' in xml


def test_schema_to_xml_with_copy_fields():
    """Test schema XML serialization with copy fields."""
    schema = Schema(
        copyFields=[
            CopyField(source="title", dest="text"),
        ]
    )
    xml = schema.build(format="xml")

    assert "<!-- Copy Fields -->" in xml
    assert '<copyField source="title" dest="text"' in xml


def test_schema_to_xml_complete():
    """Test complete schema XML serialization with all components."""
    schema = Schema(
        name="complete_schema",
        version=1.6,
        uniqueKey="id",
        fields=[
            SolrField(name="id", type="string", required=True),
        ],
        fieldTypes=[
            SolrFieldType(
                name="text_general",
                solr_class=SolrFieldClass.TEXT,
                analyzer=Analyzer(
                    tokenizer=Tokenizer(name="standard"),
                    filters=[Filter(name="lowercase")],
                ),
            ),
        ],
        dynamicFields=[
            SolrDynamicField(name="*_txt", type="text_general"),
        ],
        copyFields=[
            CopyField(source="title", dest="text"),
        ],
    )
    xml = schema.build(format="xml")

    assert '<?xml version="1.0" encoding="UTF-8"?>' in xml
    assert '<schema name="complete_schema" version="1.6">' in xml
    assert "<uniqueKey>id</uniqueKey>" in xml
    assert "<!-- Field Types -->" in xml
    assert "<!-- Fields -->" in xml
    assert "<!-- Dynamic Fields -->" in xml
    assert "<!-- Copy Fields -->" in xml
    assert "</schema>" in xml


def test_schema_invalid_format():
    """Test schema with invalid format raises error."""
    schema = Schema()

    with pytest.raises(ValueError, match="Invalid format"):
        schema.build(format="yaml")


def test_schema_add_field():
    """Test schema builder pattern - add_field."""
    schema = Schema()
    field = SolrField(name="id", type="string")

    result = schema.add_field(field)

    assert result is schema  # Returns self for chaining
    assert len(schema.fields) == 1
    assert schema.fields[0].name == "id"


def test_schema_add_dynamic_field():
    """Test schema builder pattern - add_dynamic_field."""
    schema = Schema()
    field = SolrDynamicField(name="*_txt", type="text_general")

    result = schema.add_dynamic_field(field)

    assert result is schema
    assert len(schema.dynamicFields) == 1
    assert schema.dynamicFields[0].name == "*_txt"


def test_schema_add_field_type():
    """Test schema builder pattern - add_field_type."""
    schema = Schema()
    field_type = SolrFieldType(name="pint", solr_class=SolrFieldClass.INT_POINT)

    result = schema.add_field_type(field_type)

    assert result is schema
    assert len(schema.fieldTypes) == 1
    assert schema.fieldTypes[0].name == "pint"


def test_schema_add_copy_field():
    """Test schema builder pattern - add_copy_field."""
    schema = Schema()
    copy_field = CopyField(source="title", dest="text")

    result = schema.add_copy_field(copy_field)

    assert result is schema
    assert len(schema.copyFields) == 1
    assert schema.copyFields[0].source == "title"


def test_schema_builder_pattern_chaining():
    """Test schema builder pattern with method chaining."""
    schema = (
        Schema(name="test", version=1.6, uniqueKey="id")
        .add_field_type(SolrFieldType(name="pint", solr_class=SolrFieldClass.INT_POINT))
        .add_field(SolrField(name="id", type="string"))
        .add_dynamic_field(SolrDynamicField(name="*_txt", type="text_general"))
        .add_copy_field(CopyField(source="title", dest="text"))
    )

    assert schema.name == "test"
    assert len(schema.fieldTypes) == 1
    assert len(schema.fields) == 1
    assert len(schema.dynamicFields) == 1
    assert len(schema.copyFields) == 1


def test_schema_complex_field_type():
    """Test schema with complex field type including analyzers."""
    field_type = SolrFieldType(
        name="text_en",
        solr_class=SolrFieldClass.TEXT,
        position_increment_gap=100,
        analyzer=Analyzer(
            tokenizer=Tokenizer(name="standard"),
            filters=[
                Filter(name="lowercase"),
                Filter(name="stop", words="stopwords_en.txt"),
                Filter(name="snowballPorter", language="English"),
            ],
        ),
    )

    schema = Schema(fieldTypes=[field_type])
    xml = schema.build(format="xml")

    assert '<fieldType name="text_en"' in xml
    assert 'positionIncrementGap="100"' in xml
    assert "<analyzer" in xml
    assert '<tokenizer name="standard"' in xml
    assert '<filter name="lowercase"' in xml
    assert '<filter name="stop"' in xml
    assert '<filter name="snowballPorter"' in xml
