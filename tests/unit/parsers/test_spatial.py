from taiyo.parsers import GeoFilterQueryParser
from taiyo.parsers.spatial.bbox import BBoxQueryParser


def test_geofilt_as_bbox_minimal():
    """Test using bbox filter type (rectangular, faster)"""
    parser = GeoFilterQueryParser(
        spatial_field="store",
        center_point=[45.15, -93.85],
        radial_distance=5,
        filter_type="bbox",
    )
    params = parser.build()
    # Spatial parameters are excluded from build() but available via properties
    assert params["q"] == "*:*"
    assert params["fq"] == "{!bbox sfield=store pt=45.15,-93.85 d=5.0}"
    assert parser.spatial_field == "store"
    assert parser.center_point == [45.15, -93.85]
    assert parser.radial_distance == 5


def test_geofilt_as_bbox_with_options():
    """Test bbox filter with additional options"""
    parser = GeoFilterQueryParser(
        spatial_field="store",
        center_point=[45.15, -93.85],
        radial_distance=10,
        filter_type="bbox",
        score="kilometers",
        cache=False,
    )
    params = parser.build()
    assert (
        params["fq"]
        == "{!bbox sfield=store pt=45.15,-93.85 d=10.0 score=kilometers cache=false}"
    )


def test_geofilt_minimal():
    parser = GeoFilterQueryParser(
        spatial_field="store", center_point=[45.15, -93.85], radial_distance=5
    )
    params = parser.build()
    assert params["q"] == "*:*"
    assert params["fq"] == "{!geofilt sfield=store pt=45.15,-93.85 d=5.0}"
    assert parser.spatial_field == "store"


def test_geofilt_with_options():
    parser = GeoFilterQueryParser(
        spatial_field="store",
        center_point=[45.15, -93.85],
        radial_distance=10,
        score="miles",
        filter=False,
    )
    params = parser.build()
    assert (
        params["fq"]
        == "{!geofilt sfield=store pt=45.15,-93.85 d=10.0 score=miles filter=false}"
    )


def test_geofilt_as_bbox_fq():
    """Test filter query generation for bbox type"""
    parser = GeoFilterQueryParser(
        spatial_field="store",
        center_point=[0, 0],
        radial_distance=1,
        filter_type="bbox",
    )
    assert parser.filter_query == "{!bbox sfield=store pt=0.0,0.0 d=1.0}"


def test_geofilt_fq():
    parser = GeoFilterQueryParser(
        spatial_field="store", center_point=[0, 0], radial_distance=1
    )
    assert parser.filter_query == "{!geofilt sfield=store pt=0.0,0.0 d=1.0}"


def test_bbox_field_minimal():
    parser = BBoxQueryParser(
        bbox_field="location",
        envelope=[-10, 20, 15, 10],
    )
    params = parser.build()
    assert (
        params["q"]
        == "{!field f=location}Intersects(ENVELOPE(-10.0, 20.0, 15.0, 10.0))"
    )


def test_bbox_field_with_predicate_and_score():
    parser = BBoxQueryParser(
        bbox_field="location",
        predicate="Contains",
        envelope=[-180, 180, 90, -90],
        score="overlapRatio",
    )
    params = parser.build()
    assert (
        params["q"]
        == "{!field f=location score=overlapRatio}Contains(ENVELOPE(-180.0, 180.0, 90.0, -90.0))"
    )


def test_geofilt_with_facet_config():
    """Test that GeoFilter parser properly includes facet configuration."""
    parser = GeoFilterQueryParser(
        spatial_field="location",
        center_point=[37.7749, -122.4194],
        radial_distance=10,
        filter_type="geofilt",
    )
    parser.facet(fields=["city", "state"], limit=20)

    result = parser.build()

    # Check that both geofilt params and facet params are present
    assert "fq" in result
    assert "{!geofilt" in result["fq"]
    assert result["facet"] is True
    assert result["facet.field"] == ["city", "state"]
    assert result["facet.limit"] == 20


def test_bbox_parser_with_highlight_config():
    """Test that BBox parser properly includes highlight configuration."""
    parser = BBoxQueryParser(
        bbox_field="region",
        predicate="Intersects",
        envelope=[-122.5, -122.3, 37.8, 37.7],
    )
    parser.highlight(fields=["name", "description"], snippets_per_field=3)

    result = parser.build()

    # Check that both bbox params and highlight params are present
    assert "q" in result
    assert result["hl"] is True
    assert result["hl.fl"] == ["name", "description"]
    assert result["hl.snippets"] == 3
