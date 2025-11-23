# Spatial Search Parsers

Spatial parsers enable geographic and location-based queries using lat/lon coordinates or bounding boxes.

## Overview

Solr supports spatial search for geographic data using specialized field types and query parsers. Taiyo provides parsers for the two main spatial query types:

- **GeoFilterQueryParser**: Filter documents within a radius of a point
- **BBoxQueryParser**: Filter documents within a bounding box

**Solr Documentation**: [Spatial Search](https://solr.apache.org/guide/solr/latest/query-guide/spatial-search.html)

## Schema Setup

Before using spatial parsers, configure your schema with spatial fields:

```python
from taiyo.schema import FieldType, Field

# LatLonPointSpatialField (recommended for most cases)
location_type = FieldType(
    name="location",
    class_name="solr.LatLonPointSpatialField",
    doc_values=True
)

# Add location field
location_field = Field(
    name="location",
    type="location",
    indexed=True,
    stored=True
)

# Update schema
client.schema.add_field_type(location_type)
client.schema.add_field(location_field)
```

### Indexing Location Data

```python
documents = [
    {
        "id": "restaurant1",
        "name": "Joe's Pizza",
        "location": "40.7589,-73.9851",  # lat,lon format
        "category": "restaurant"
    },
    {
        "id": "hotel1",
        "name": "Grand Hotel",
        "location": "40.7614,-73.9776",
        "category": "hotel"
    },
    {
        "id": "cafe1",
        "name": "Coffee Corner",
        "location": "40.7580,-73.9855",
        "category": "cafe"
    }
]

client.index(documents)
```

## GeoFilterQueryParser

The `GeoFilterQueryParser` (geofilt) finds documents within a specified radius of a point.

### Basic Usage

```python
from taiyo.parsers import GeoFilterQueryParser

parser = GeoFilterQueryParser(
    field="location",
    point="40.7589,-73.9851",  # Times Square, NYC
    distance=5  # 5 km radius
)

results = client.search(parser)
```

### Parameters

```python
parser = GeoFilterQueryParser(
    field="location",              # Spatial field name
    point="lat,lon",              # Center point (lat,lon)
    distance=10,                  # Radius in km
    
    # Common parameters
    rows=10,
    start=0,
    fields=["id", "name", "location"],
    sort="geodist() asc",         # Sort by distance
    filter_query=["category:restaurant"]
)
```

### Distance Sorting

Sort results by distance from the query point:

```python
parser = GeoFilterQueryParser(
    field="location",
    point="40.7589,-73.9851",
    distance=5,
    sort="geodist() asc",  # Nearest first
    field_list=["id", "name", "location", "score"]
)

results = client.search(parser)

for doc in results.docs:
    # Calculate distance in results
    print(f"{doc.name} - {doc.location}")
```

### Return Distance as Field

Include the distance in results:

```python
parser = GeoFilterQueryParser(
    field="location",
    point="40.7589,-73.9851",
    distance=10,
    sort="geodist() asc",
    field_list=["id", "name", "location", "distance:geodist()"]
)

results = client.search(parser)

for doc in results.docs:
    print(f"{doc.name}: {doc.distance:.2f} km away")
```

### Complete Example

```python
from taiyo.parsers import GeoFilterQueryParser

# User's current location
user_lat, user_lon = 40.7589, -73.9851

parser = (
    GeoFilterQueryParser(
        field="location",
        point=f"{user_lat},{user_lon}",
        distance=5,  # 5 km radius
        rows=20,
        sort="geodist() asc",  # Nearest first
        field_list=[
            "id",
            "name",
            "category",
            "rating",
            "location",
            "distance:geodist()"
        ],
        filters=[
            "category:restaurant",
            "rating:[4 TO *]",  # Highly rated
            "status:open"
        ]
    )
    .facet(
        fields=["category", "price_range"],
        mincount=1
    )
)

results = client.search(parser)

print(f"Found {results.num_found} restaurants within 5km")
for doc in results.docs:
    print(f"\n{doc.name}")
    print(f"  Category: {doc.category}")
    print(f"  Rating: {doc.rating}/5")
    print(f"  Distance: {doc.distance:.2f} km")
```

### Dynamic Distance

Allow users to specify search radius:

```python
def search_nearby(lat: float, lon: float, radius_km: float = 5, category: str = None):
    """Search for places near a location."""
    filters = ["status:active"]
    if category:
        filters.append(f"category:{category}")

    parser = GeoFilterQueryParser(
        field="location",
        point=f"{lat},{lon}",
        distance=radius_km,
        rows=20,
        field_list=["id", "name", "category", "distance:geodist()"],
        sort="geodist() asc",
        filters=filters
    )

    return client.search(parser)

# Usage
results = search_nearby(40.7589, -73.9851, radius_km=10, category="restaurant")
```

## BBoxQueryParser

The `BBoxQueryParser` finds documents within a rectangular bounding box.

### Basic Usage

```python
from taiyo.parsers import BBoxQueryParser

parser = BBoxQueryParser(
    field="location",
    min_lat=40.7,
    min_lon=-74.0,
    max_lat=40.8,
    max_lon=-73.9
)

results = client.search(parser)
```

### Parameters

```python
parser = BBoxQueryParser(
    field="location",       # Spatial field name
    min_lat=40.7,          # Southwest corner latitude
    min_lon=-74.0,         # Southwest corner longitude
    max_lat=40.8,          # Northeast corner latitude
    max_lon=-73.9,         # Northeast corner longitude
    
    # Common parameters
    rows=10,
    start=0,
    fields=["id", "name", "location"],
    filter_query=["category:restaurant"]
)
```

### Map Viewport Search

Search within the user's map viewport:

```python
from taiyo.parsers import BBoxQueryParser

def search_in_viewport(sw_lat: float, sw_lon: float, 
                       ne_lat: float, ne_lon: float,
                       category: str = None):
    """Search within map bounds."""
    parser = BBoxQueryParser(
        field="location",
        min_lat=sw_lat,
        min_lon=sw_lon,
        max_lat=ne_lat,
        max_lon=ne_lon,
        rows=100,  # Return many points for map
        field_list=["id", "name", "location", "category"],
        filters=["status:active"]
    )
    
    if category:
        parser = parser.model_copy(update={
            "filters": [f"category:{category}", "status:active"]
        })
    
    return client.search(parser)

# User's map viewport (Manhattan)
results = search_in_viewport(
    sw_lat=40.7,
    sw_lon=-74.02,
    ne_lat=40.8,
    ne_lon=-73.9,
    category="restaurant"
)
```

### Complete Example

```python
from taiyo.parsers import BBoxQueryParser

# Search area: Central Manhattan
parser = (
    BBoxQueryParser(
        field="location",
        min_lat=40.75,      # Southwest corner
        min_lon=-73.99,
        max_lat=40.77,      # Northeast corner
        max_lon=-73.97,
        rows=50,
        field_list=[
            "id",
            "name",
            "address",
            "category",
            "rating",
            "location"
        ],
        sort="rating desc, name asc",
        filters=[
            "category:(restaurant OR cafe)",
            "rating:[4 TO *]",
            "price_range:[1 TO 3]"
        ]
    )
    .facet(
        fields=["category", "price_range", "cuisine"],
        mincount=1
    )
)

results = client.search(parser)

print(f"Found {results.num_found} places in area")
for doc in results.docs:
    print(f"\n{doc.name} ({doc.category})")
    print(f"  Address: {doc.address}")
    print(f"  Rating: {doc.rating}/5")
    print(f"  Location: {doc.location}")
```

## Combining Spatial and Other Queries

### Spatial + Keyword Search

```python
from taiyo.parsers import GeoFilterQueryParser

parser = (
    GeoFilterQueryParser(
        field="location",
        point="40.7589,-73.9851",
        distance=5
    )
)
params = parser.build()
params.update(
    {
        "q": "pizza",  # Keyword search
        "qf": "name^2 description",  # Use eDisMax-style boosts
        "rows": 20,
        "fl": "id,name,description,distance:geodist()",
        "sort": "geodist() asc"
    }
)

results = client.search(params)
```

### Spatial with Faceting

```python
parser = (
    GeoFilterQueryParser(
        field="location",
        point="40.7589,-73.9851",
        distance=10,
        rows=20,
        field_list=["id", "name", "category", "distance:geodist()"],
        sort="geodist() asc"
    )
    .facet(
        fields=["category", "price_range", "cuisine"],
        mincount=1
    )
)

results = client.search(parser)

# Show facets
print("\nCategories:")
for category, count in results.facet_counts["facet_fields"]["category"]:
    print(f"  {category}: {count}")
```

### Multi-Location Search

Search near multiple locations:

```python
from taiyo.parsers import GeoFilterQueryParser

# Find places near either location
locations = [
    ("40.7589,-73.9851", "Times Square"),
    ("40.7614,-73.9776", "Central Park")
]

# Build filter with OR
location_filters = " OR ".join([
    f"{{!geofilt sfield=location pt={loc} d=2}}"
    for loc, _ in locations
])

parser = GeoFilterQueryParser(
    field="location",
    point=locations[0][0],  # Primary location
    distance=2,
    filters=[location_filters],  # Near any location
    rows=50,
    sort="geodist() asc"
)
```

## Distance Functions

Use `geodist()` for distance calculations:

```python
# Example parser with location filter
parser = GeoFilterQueryParser(
    field="location",
    point="40.7589,-73.9851",
    distance=5
)

# Sort by distance
results = client.search(
    parser,
    sort="geodist() asc"
)

# Return distance as field
results = client.search(
    parser,
    fl="id,name,distance:geodist()"
)

# Boost by proximity (closer = higher score)
results = client.search(
    parser,
    bf="recip(geodist(),2,200,20)"
)

# Filter by distance range
results = client.search(
    parser,
    fq="{!frange l=0 u=5}geodist()"  # 0-5 km
)
```

## Best Practices

### Use Appropriate Spatial Field Type

For simple latitude/longitude points:

```python
FieldType(
    name="location",
    class_name="solr.LatLonPointSpatialField",
    doc_values=True
)
```



### Index Location Format

Format: "latitude,longitude"

```python
docs = [
    {"id": "1", "location": "40.7589,-73.9851"},
    {"id": "2", "location": "-73.9851,40.7589"},  # Wrong: lon,lat
]
```

### Choose Distance Units

```python
# Solr default is kilometers
parser = GeoFilterQueryParser(
    field="location",
    point="40.7589,-73.9851",
    distance=5  # 5 kilometers
)

# For miles, convert
miles_to_km = 1.60934
parser = GeoFilterQueryParser(
    field="location",
    point="40.7589,-73.9851",
    distance=5 * miles_to_km  # 5 miles
)
```

### Optimize Radius Search

```python
# Start with reasonable radius
parser = GeoFilterQueryParser(
    field="location",
    point="40.7589,-73.9851",
    distance=10,  # Not too large
    filters=[
        "category:restaurant",  # Narrow scope
        "rating:[4 TO *]"       # Quality filter
    ],
    rows=20  # Reasonable limit
)
```

### Use BBox for Map Displays

```python
# For map viewport queries, BBox is more efficient
parser = BBoxQueryParser(
    field="location",
    min_lat=viewport_sw_lat,
    min_lon=viewport_sw_lon,
    max_lat=viewport_ne_lat,
    max_lon=viewport_ne_lon,
    rows=100,  # Many points for map
    field_list=["id", "name", "location", "category"]
)
```

### Handle Edge Cases

```python
def safe_spatial_search(lat: float, lon: float, radius_km: float):
    """Spatial search with validation."""
    # Validate inputs
    if not (-90 <= lat <= 90):
        raise ValueError("Latitude must be between -90 and 90")
    if not (-180 <= lon <= 180):
        raise ValueError("Longitude must be between -180 and 180")
    if radius_km <= 0:
        raise ValueError("Radius must be positive")
    
    parser = GeoFilterQueryParser(
        field="location",
        point=f"{lat},{lon}",
        distance=radius_km
    )
    
    return client.search(parser)
```

## Common Patterns

### Restaurant Finder

```python
def find_restaurants(lat: float, lon: float, 
                    cuisine: str = None,
                    radius_km: float = 5,
                    min_rating: float = 3.5):
    """Find restaurants near a location."""
    parser = GeoFilterQueryParser(
        field="location",
        point=f"{lat},{lon}",
        distance=radius_km
    )
    
    filters = [
        "category:restaurant",
        f"rating:[{min_rating} TO *]",
        "status:open"
    ]
    
    if cuisine:
        filters.append(f"cuisine:{cuisine}")
    
    parser = GeoFilterQueryParser(
        field="location",
        point=f"{lat},{lon}",
        distance=radius_km,
        rows=20,
        field_list=[
            "id", "name", "cuisine", "rating",
            "price_range", "distance:geodist()"
        ],
        sort="geodist() asc",
        filters=filters
    ).facet(
        fields=["cuisine", "price_range"],
        mincount=1
    )
    
    return client.search(parser)

# Usage
results = find_restaurants(
    lat=40.7589,
    lon=-73.9851,
    cuisine="italian",
    radius_km=3,
    min_rating=4.0
)
```

### Store Locator

```python
def find_nearest_stores(lat: float, lon: float, max_results: int = 5):
    """Find nearest store locations."""
    parser = GeoFilterQueryParser(
        field="location",
        point=f"{lat},{lon}",
        distance=50,  # Wide initial search
        rows=max_results,
        field_list=[
            "id", "name", "address", "phone",
            "hours", "distance:geodist()"
        ],
        sort="geodist() asc",
        filters=["type:store", "status:open"]
    )
    
    return client.search(parser)
```

### Delivery Zone Check

```python
def check_delivery_available(restaurant_id: str, 
                             delivery_lat: float,
                             delivery_lon: float):
    """Check if delivery address is within range."""
    # Get restaurant location
    restaurant = client.get(restaurant_id)
    rest_location = restaurant["location"]  # "lat,lon"
    
    # Check distance
    parser = GeoFilterQueryParser(
        field="location",
        point=rest_location,
        distance=5,  # 5km delivery radius
        field_list=["id", "distance:geodist()"],
        filters=[f"location:{delivery_lat},{delivery_lon}"]
    )
    
    results = client.search(parser)
    
    if results.num_found > 0:
        distance = results.docs[0].distance
        return True, f"Within delivery range ({distance:.1f}km)"
    else:
        return False, "Outside delivery range"
```

### Map Clustering

```python
def get_map_points(sw_lat: float, sw_lon: float,
                   ne_lat: float, ne_lon: float,
                   category: str = None):
    """Get points for map display with clustering."""
    parser = (
        BBoxQueryParser(
            field="location",
            min_lat=sw_lat,
            min_lon=sw_lon,
            max_lat=ne_lat,
            max_lon=ne_lon,
            rows=500,  # Many points for clustering
            field_list=["id", "name", "location", "category"],
            filters=["status:active"]
        )
    )
    
    if category:
        parser = parser.model_copy(
            update={"filters": [f"category:{category}", "status:active"]}
        )
    
    results = client.search(parser)
    
    # Return points for client-side clustering
    return [
        {
            "id": doc.id,
            "name": doc.name,
            "lat": float(doc.location.split(",")[0]),
            "lon": float(doc.location.split(",")[1]),
            "category": doc.category
        }
        for doc in results.docs
    ]
```

## Next Steps

- Learn about [Sparse Parsers](sparse.md) for keyword search
- Explore [Dense Parsers](dense.md) for vector similarity search
- Add [Faceting](../faceting.md) for filtering options
- Use [Grouping](../grouping.md) for organizing results
