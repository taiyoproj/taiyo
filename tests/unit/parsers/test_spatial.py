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
