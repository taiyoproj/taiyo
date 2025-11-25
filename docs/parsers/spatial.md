# Spatial Search Parsers

Spatial parsers enable geographic and location-based queries using lat/lon coordinates or bounding boxes. Perfect for building location finders, proximity search, and map-based applications.

## Overview

Taiyo provides two spatial query parsers:

- **GeoFilterQueryParser**: Find documents within a radius of a point
- **BBoxQueryParser**: Find documents within a rectangular map area

**Solr Documentation**: [Spatial Search](https://solr.apache.org/guide/solr/latest/query-guide/spatial-search.html)

## Setup

### Schema Configuration

```python
from taiyo.schema import SolrFieldType, SolrField, SolrFieldClass

# Define spatial field type
location_type = SolrFieldType(
    name="location", solr_class=SolrFieldClass.LATLON_POINT_SPATIAL
)

# Add fields
fields = [
    SolrField(name="name", type="string", stored=True),
    SolrField(name="location", type="location", indexed=True, stored=True),
    SolrField(name="cuisine", type="string", stored=True),
    SolrField(name="rating", type="pfloat", stored=True),
]

# Update schema
client.add_field_type(location_type)
for field in fields:
    client.add_field(field)
```

### Index Data with Locations

```python
from taiyo import SolrDocument


class Restaurant(SolrDocument):
    name: str
    location: str  # "lat,lon" format
    cuisine: str
    rating: float


restaurants = [
    Restaurant(
        id="1",
        name="Joe's Pizza",
        location="40.7589,-73.9851",
        cuisine="Italian",
        rating=4.5,
    ),
    Restaurant(
        id="2",
        name="Sushi Place",
        location="40.7614,-73.9776",
        cuisine="Japanese",
        rating=4.8,
    ),
    Restaurant(
        id="3",
        name="Taco Stand",
        location="40.7580,-73.9855",
        cuisine="Mexican",
        rating=4.2,
    ),
]

client.add(restaurants)
client.commit()
```

## GeoFilterQueryParser

Find documents within a specified radius of a point.

### Basic Usage

```python
from taiyo.parsers import GeoFilterQueryParser

# Find restaurants within 5km of Times Square
parser = GeoFilterQueryParser(
    spatial_field="location",
    center_point=[40.7589, -73.9851],
    radial_distance=5,  # 5 km radius
)

results = client.search(parser, document_model=Restaurant)
```

### With Distance and Sorting

```python
parser = GeoFilterQueryParser(
    spatial_field="location",
    center_point=[40.7589, -73.9851],
    radial_distance=5,
    sort="geodist() asc",  # Nearest first
    field_list=["id", "name", "cuisine", "rating", "distance:geodist()"],
)

results = client.search(parser, document_model=Restaurant)

for doc in results.docs:
    print(f"{doc.name} ({doc.cuisine}) - {doc.distance:.2f} km away - ⭐ {doc.rating}")
```

### Example

```python
from taiyo.parsers import GeoFilterQueryParser

# User's current location (Times Square)
user_lat, user_lon = 40.7589, -73.9851

parser = GeoFilterQueryParser(
    spatial_field="location",
    center_point=[user_lat, user_lon],
    radial_distance=5,
    rows=20,
    sort="geodist() asc",
    field_list=["id", "name", "cuisine", "rating", "distance:geodist()"],
    filters=["rating:[4 TO *]"],  # Highly rated only
).facet(fields=["cuisine"], mincount=1)

results = client.search(parser, document_model=Restaurant)

print(f"Found {results.num_found} restaurants within 5km")
for doc in results.docs:
    print(f"{doc.name} - {doc.cuisine} - {doc.distance:.1f}km - ⭐{doc.rating}")
```

### Reusable Search Function

```python
def find_restaurants(
    lat: float,
    lon: float,
    radius_km: float = 5,
    cuisine: str = None,
    min_rating: float = 4.0,
):
    """Find restaurants near a location."""
    filters = [f"rating:[{min_rating} TO *]"]
    if cuisine:
        filters.append(f"cuisine:{cuisine}")

    parser = GeoFilterQueryParser(
        spatial_field="location",
        center_point=[lat, lon],
        radial_distance=radius_km,
        rows=20,
        field_list=["id", "name", "cuisine", "rating", "distance:geodist()"],
        sort="geodist() asc",
        filters=filters,
    )

    return client.search(parser, document_model=Restaurant)


# Find Italian restaurants within 3km
results = find_restaurants(40.7589, -73.9851, radius_km=3, cuisine="Italian")
```

## BBoxQueryParser

Find documents within a rectangular bounding box (map area).

### Basic Usage

```python
from taiyo.parsers import BBoxQueryParser

# Manhattan area
parser = BBoxQueryParser(
    bbox_field="location",
    envelope=[-74.0, -73.9, 40.8, 40.7],  # [minX, maxX, maxY, minY]
)

results = client.search(parser, document_model=Restaurant)
```

### Map Viewport Search

```python
from taiyo.parsers import BBoxQueryParser


def search_map_area(sw_lat: float, sw_lon: float, ne_lat: float, ne_lon: float):
    """Search within map viewport bounds."""
    parser = BBoxQueryParser(
        bbox_field="location",
        envelope=[sw_lon, ne_lon, ne_lat, sw_lat],  # [minX, maxX, maxY, minY]
        rows=100,
        field_list=["id", "name", "location", "cuisine", "rating"],
        sort="rating desc",
    )
    return client.search(parser, document_model=Restaurant)


# Search visible map area
results = search_map_area(
    sw_lat=40.7,
    sw_lon=-74.02,  # Southwest corner
    ne_lat=40.8,
    ne_lon=-73.9,  # Northeast corner
)
```

### With Filters and Faceting

```python
# Find highly-rated restaurants in Central Manhattan
parser = BBoxQueryParser(
    bbox_field="location",
    envelope=[-73.99, -73.97, 40.77, 40.75],
    rows=50,
    field_list=["id", "name", "cuisine", "rating"],
    sort="rating desc",
    filters=["rating:[4 TO *]"],
).facet(fields=["cuisine"], mincount=1)

results = client.search(parser, document_model=Restaurant)

print(f"Found {results.num_found} restaurants in area")
for doc in results.docs:
    print(f"{doc.name} - {doc.cuisine} - ⭐{doc.rating}")
```

## Next Steps

- Learn about [Sparse Parsers](sparse.md) for keyword search
- Explore [Dense Parsers](dense.md) for vector similarity search
- Add [Faceting](../faceting.md) for filtering options
- Use [Grouping](../grouping.md) for organizing results
