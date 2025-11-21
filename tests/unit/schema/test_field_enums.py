"""Tests for field type class enumerations."""

from taiyo.schema.enums import SolrFieldClass


def test_solr_field_class_text_types():
    """Test text and string field type enums."""
    assert SolrFieldClass.TEXT.value == "solr.TextField"
    assert SolrFieldClass.STR.value == "solr.StrField"
    assert SolrFieldClass.COLLATION.value == "solr.CollationField"
    assert SolrFieldClass.ICU_COLLATION.value == "solr.ICUCollationField"
    assert SolrFieldClass.ENUM.value == "solr.EnumFieldType"


def test_solr_field_class_boolean_types():
    """Test boolean, binary, and UUID field type enums."""
    assert SolrFieldClass.BOOL.value == "solr.BoolField"
    assert SolrFieldClass.BINARY.value == "solr.BinaryField"
    assert SolrFieldClass.UUID.value == "solr.UUIDField"


def test_solr_field_class_numeric_types():
    """Test numeric point field type enums."""
    assert SolrFieldClass.INT_POINT.value == "solr.IntPointField"
    assert SolrFieldClass.LONG_POINT.value == "solr.LongPointField"
    assert SolrFieldClass.FLOAT_POINT.value == "solr.FloatPointField"
    assert SolrFieldClass.DOUBLE_POINT.value == "solr.DoublePointField"
    assert SolrFieldClass.DATE_POINT.value == "solr.DatePointField"


def test_solr_field_class_date_currency_types():
    """Test date range and currency field type enums."""
    assert SolrFieldClass.DATE_RANGE.value == "solr.DateRangeField"
    assert SolrFieldClass.CURRENCY.value == "solr.CurrencyFieldType"


def test_solr_field_class_spatial_types():
    """Test spatial field type enums."""
    assert SolrFieldClass.LATLON_POINT_SPATIAL.value == "solr.LatLonPointSpatialField"
    assert SolrFieldClass.BBOX.value == "solr.BBoxField"
    assert (
        SolrFieldClass.SPATIAL_RPT.value == "solr.SpatialRecursivePrefixTreeFieldType"
    )
    assert SolrFieldClass.RPT_WITH_GEOMETRY.value == "solr.RptWithGeometrySpatialField"
    assert SolrFieldClass.POINT.value == "solr.PointType"


def test_solr_field_class_vector_types():
    """Test vector/ML field type enums."""
    assert SolrFieldClass.DENSE_VECTOR.value == "solr.DenseVectorField"


def test_solr_field_class_string_conversion():
    """Test that enum values can be used as strings."""
    assert str(SolrFieldClass.TEXT) == "solr.TextField"
    assert str(SolrFieldClass.INT_POINT) == "solr.IntPointField"


def test_solr_field_class_is_string_enum():
    """Test that enum members are string instances."""
    assert isinstance(SolrFieldClass.TEXT, str)
    assert isinstance(SolrFieldClass.INT_POINT, str)
