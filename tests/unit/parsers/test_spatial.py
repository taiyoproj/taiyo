from taiyo.parsers import BoundingBoxQueryParser


def test_bbox_minimal():
    parser = BoundingBoxQueryParser(
        spatial_field="store", center_point=[45.15, -93.85], radial_distance=5
    )
    params = parser.build()
    assert params["sfield"] == "store"
    assert params["pt"] == "45.15,-93.85"
    assert params["d"] == 5
    assert "score" not in params
    assert "filter" not in params


def test_bbox_full():
    parser = BoundingBoxQueryParser(
        spatial_field="store",
        center_point=[45.15, -93.85],
        radial_distance=10,
        score="overlapRatio",
        filter=True,
    )
    params = parser.build()
    assert params["score"] == "overlapRatio"
    assert params["filter"] is True
