"""Tests for field type and analyzer components."""

import pytest
from taiyo.schema import SolrFieldType, SolrFieldClass
from taiyo.schema.field_type import Analyzer, Tokenizer, Filter, CharFilter


def test_char_filter_basic():
    """Test basic character filter creation."""
    char_filter = CharFilter(name="htmlStrip")

    assert char_filter.name == "htmlStrip"
    assert char_filter.solr_class is None


def test_char_filter_with_class():
    """Test character filter with class name."""
    char_filter = CharFilter(solr_class="solr.HTMLStripCharFilterFactory")

    assert char_filter.solr_class == "solr.HTMLStripCharFilterFactory"


def test_char_filter_with_extra_params():
    """Test character filter with extra parameters."""
    char_filter = CharFilter(
        name="patternReplace",
        pattern=r"([a-z])\1+",
        replacement="$1",
    )

    assert char_filter.name == "patternReplace"
    # Extra params should be accessible
    result = char_filter.build(format="json")
    assert "pattern" in result
    assert "replacement" in result


def test_char_filter_to_dict():
    """Test character filter JSON serialization."""
    char_filter = CharFilter(name="htmlStrip")
    result = char_filter.build(format="json")

    assert result == {"name": "htmlStrip"}


def test_tokenizer_basic():
    """Test basic tokenizer creation."""
    tokenizer = Tokenizer(name="standard")

    assert tokenizer.name == "standard"
    assert tokenizer.solr_class is None


def test_tokenizer_with_class():
    """Test tokenizer with class name."""
    tokenizer = Tokenizer(solr_class="solr.StandardTokenizerFactory")

    assert tokenizer.solr_class == "solr.StandardTokenizerFactory"


def test_tokenizer_with_extra_params():
    """Test tokenizer with extra parameters."""
    tokenizer = Tokenizer(
        name="nGram",
        minGramSize=3,
        maxGramSize=5,
    )

    assert tokenizer.name == "nGram"
    result = tokenizer.build(format="json")
    assert "minGramSize" in result
    assert "maxGramSize" in result


def test_tokenizer_to_dict():
    """Test tokenizer JSON serialization."""
    tokenizer = Tokenizer(name="whitespace")
    result = tokenizer.build(format="json")

    assert result == {"name": "whitespace"}


def test_filter_basic():
    """Test basic token filter creation."""
    filter_ = Filter(name="lowercase")

    assert filter_.name == "lowercase"
    assert filter_.solr_class is None


def test_filter_with_class():
    """Test filter with class name."""
    filter_ = Filter(solr_class="solr.LowerCaseFilterFactory")

    assert filter_.solr_class == "solr.LowerCaseFilterFactory"


def test_filter_with_extra_params():
    """Test filter with extra parameters (must use camelCase for Solr compatibility)."""
    filter_ = Filter(
        name="stop",
        ignoreCase=True,
        words="stopwords.txt",
    )

    assert filter_.name == "stop"
    result = filter_.build(format="json")
    assert "ignoreCase" in result
    assert "words" in result


def test_filter_to_dict():
    """Test filter JSON serialization."""
    filter_ = Filter(name="lowercase")
    result = filter_.build(format="json")

    assert result == {"name": "lowercase"}


def test_analyzer_basic():
    """Test basic analyzer creation."""
    analyzer = Analyzer(
        tokenizer=Tokenizer(name="standard"),
        filters=[Filter(name="lowercase")],
    )

    assert analyzer.tokenizer.name == "standard"
    assert len(analyzer.filters) == 1
    assert analyzer.filters[0].name == "lowercase"


def test_analyzer_with_char_filters():
    """Test analyzer with character filters."""
    analyzer = Analyzer(
        char_filters=[CharFilter(name="htmlStrip")],
        tokenizer=Tokenizer(name="standard"),
        filters=[Filter(name="lowercase")],
    )

    assert len(analyzer.char_filters) == 1
    assert analyzer.char_filters[0].name == "htmlStrip"


def test_analyzer_with_type():
    """Test analyzer with type specified."""
    analyzer = Analyzer(
        type="index",
        tokenizer=Tokenizer(name="standard"),
    )

    assert analyzer.type == "index"


def test_analyzer_to_dict():
    """Test analyzer JSON serialization."""
    analyzer = Analyzer(
        tokenizer=Tokenizer(name="standard"),
        filters=[Filter(name="lowercase"), Filter(name="stop")],
    )
    result = analyzer.build(format="json")

    assert "tokenizer" in result
    assert result["tokenizer"]["name"] == "standard"
    assert "filters" in result
    assert len(result["filters"]) == 2


def test_analyzer_to_xml():
    """Test analyzer XML serialization."""
    analyzer = Analyzer(
        tokenizer=Tokenizer(name="standard"),
        filters=[Filter(name="lowercase")],
    )
    xml = analyzer.build(format="xml")

    assert "<analyzer" in xml
    assert "<tokenizer" in xml
    assert 'name="standard"' in xml
    assert "<filter" in xml
    assert 'name="lowercase"' in xml
    assert "</analyzer>" in xml


def test_analyzer_to_xml_with_type():
    """Test analyzer XML serialization with type attribute."""
    analyzer = Analyzer(
        type="query",
        tokenizer=Tokenizer(name="standard"),
    )
    xml = analyzer.build(format="xml")

    assert 'type="query"' in xml


def test_analyzer_to_xml_with_char_filters():
    """Test analyzer XML serialization with character filters."""
    analyzer = Analyzer(
        char_filters=[CharFilter(name="htmlStrip")],
        tokenizer=Tokenizer(name="standard"),
    )
    xml = analyzer.build(format="xml")

    assert "<charFilter" in xml
    assert 'name="htmlStrip"' in xml


def test_analyzer_invalid_format():
    """Test analyzer with invalid format raises error."""
    analyzer = Analyzer(tokenizer=Tokenizer(name="standard"))

    with pytest.raises(ValueError, match="Invalid format"):
        analyzer.build(format="yaml")


def test_field_type_basic():
    """Test basic field type creation."""
    field_type = SolrFieldType(name="text_general", solr_class=SolrFieldClass.TEXT)

    assert field_type.name == "text_general"
    assert field_type.solr_class == SolrFieldClass.TEXT


def test_field_type_with_string_class():
    """Test field type with string class instead of enum."""
    field_type = SolrFieldType(name="custom", solr_class="solr.TextField")

    assert field_type.name == "custom"
    assert field_type.solr_class == "solr.TextField"


def test_field_type_with_analyzer():
    """Test field type with analyzer."""
    analyzer = Analyzer(
        tokenizer=Tokenizer(name="standard"),
        filters=[Filter(name="lowercase")],
    )
    field_type = SolrFieldType(
        name="text_general",
        solr_class=SolrFieldClass.TEXT,
        analyzer=analyzer,
    )

    assert field_type.analyzer is not None
    assert field_type.analyzer.tokenizer.name == "standard"


def test_field_type_with_separate_analyzers():
    """Test field type with separate index and query analyzers."""
    field_type = SolrFieldType(
        name="text_general",
        solr_class=SolrFieldClass.TEXT,
        index_analyzer=Analyzer(
            tokenizer=Tokenizer(name="standard"),
            filters=[Filter(name="lowercase")],
        ),
        query_analyzer=Analyzer(
            tokenizer=Tokenizer(name="standard"),
            filters=[Filter(name="lowercase"), Filter(name="synonymGraph")],
        ),
    )

    assert field_type.index_analyzer is not None
    assert field_type.query_analyzer is not None
    assert len(field_type.query_analyzer.filters) == 2


def test_field_type_with_properties():
    """Test field type with various properties."""
    field_type = SolrFieldType(
        name="text_general",
        solr_class=SolrFieldClass.TEXT,
        position_increment_gap=100,
        auto_generate_phrase_queries=True,
        enable_graph_queries=True,
    )

    assert field_type.position_increment_gap == 100
    assert field_type.auto_generate_phrase_queries is True
    assert field_type.enable_graph_queries is True


def test_field_type_to_dict_with_enum():
    """Test field type JSON serialization with enum class."""
    field_type = SolrFieldType(
        name="text_general",
        solr_class=SolrFieldClass.TEXT,
    )
    result = field_type.build(format="json")

    assert result["name"] == "text_general"
    assert result["class"] == "solr.TextField"


def test_field_type_to_dict_with_string():
    """Test field type JSON serialization with string class."""
    field_type = SolrFieldType(
        name="custom",
        solr_class="solr.TextField",
    )
    result = field_type.build(format="json")

    assert result["name"] == "custom"
    assert result["class"] == "solr.TextField"


def test_field_type_to_dict_with_analyzer():
    """Test field type JSON serialization with analyzer."""
    field_type = SolrFieldType(
        name="text_general",
        solr_class=SolrFieldClass.TEXT,
        analyzer=Analyzer(
            tokenizer=Tokenizer(name="standard"),
        ),
    )
    result = field_type.build(format="json")

    assert "analyzer" in result
    assert result["analyzer"]["tokenizer"]["name"] == "standard"


def test_field_type_to_xml_simple():
    """Test field type XML serialization without analyzer."""
    field_type = SolrFieldType(
        name="pint",
        solr_class=SolrFieldClass.INT_POINT,
    )
    xml = field_type.build(format="xml")

    assert "<fieldType" in xml
    assert 'name="pint"' in xml
    assert 'class="solr.IntPointField"' in xml
    assert "/>" in xml
    assert "</fieldType>" not in xml  # Self-closing tag


def test_field_type_to_xml_with_analyzer():
    """Test field type XML serialization with analyzer."""
    field_type = SolrFieldType(
        name="text_general",
        solr_class=SolrFieldClass.TEXT,
        analyzer=Analyzer(
            tokenizer=Tokenizer(name="standard"),
            filters=[Filter(name="lowercase")],
        ),
    )
    xml = field_type.build(format="xml")

    assert "<fieldType" in xml
    assert "<analyzer" in xml
    assert "<tokenizer" in xml
    assert "<filter" in xml
    assert "</analyzer>" in xml
    assert "</fieldType>" in xml


def test_field_type_to_xml_with_indent():
    """Test field type XML serialization with indentation."""
    field_type = SolrFieldType(
        name="pint",
        solr_class=SolrFieldClass.INT_POINT,
    )
    xml = field_type.build(format="xml", indent="  ")

    assert xml.startswith("  <fieldType")


def test_field_type_with_extra_params():
    """Test field type with extra parameters for specific types."""
    field_type = SolrFieldType(
        name="vector",
        solr_class=SolrFieldClass.DENSE_VECTOR,
        vectorDimension=768,
        similarityFunction="cosine",
    )

    result = field_type.build(format="json")
    assert result["vectorDimension"] == 768
    assert result["similarityFunction"] == "cosine"


def test_field_type_camel_case_aliases():
    """Test field type supports camelCase aliases."""
    field_type = SolrFieldType(
        name="text_general",
        solr_class=SolrFieldClass.TEXT,
        position_increment_gap=100,
        auto_generate_phrase_queries=True,
        doc_values=True,
    )

    assert field_type.position_increment_gap == 100
    assert field_type.auto_generate_phrase_queries is True
    assert field_type.doc_values is True


def test_field_type_invalid_format():
    """Test field type with invalid format raises error."""
    field_type = SolrFieldType(name="test", solr_class=SolrFieldClass.TEXT)

    with pytest.raises(ValueError, match="Invalid format"):
        field_type.build(format="invalid")
