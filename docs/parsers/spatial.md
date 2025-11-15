# Spatial Query Parsers

Spatial query parsers are used for geospatial filtering and scoring in Solr. Both extend `SpatialSearchParamsMixin` and require `sfield`, `pt`, and `d`.

## BoundingBoxQueryParser

```python
from taiyo import BoundingBoxQueryParser

bbox = BoundingBoxQueryParser(
    spatial_field="store",
    center_point=[45.15, -93.85],
    radial_distance=5,
)
res = client.search(bbox)
```

## GeoFilterQueryParser

```python
from taiyo import GeoFilterQueryParser

geofilt = GeoFilterQueryParser(
    spatial_field="store",
    center_point=[45.15, -93.85],
    radial_distance=10,
    score="distance",
)
res = client.search(geofilt)
```
