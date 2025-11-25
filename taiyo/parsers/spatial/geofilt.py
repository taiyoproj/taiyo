from typing import Literal
from pydantic import computed_field, Field
from .base import SpatialQueryParser


class GeoFilterQueryParser(SpatialQueryParser):
    """Geospatial Filter Query Parsers (geofilt and bbox) for Apache Solr.

    The geofilt and bbox parsers enable location-based filtering in Solr, allowing you to
    find documents within a certain distance from a point. Geofilt uses a circular radius
    (precise), while bbox uses a rectangular bounding box (faster but less precise).

    Solr Reference:
        https://solr.apache.org/guide/solr/latest/query-guide/spatial-search.html

    Key Features:
        - Circular radius search (geofilt) or bounding box search (bbox)
        - Distance-based filtering and scoring
        - Configurable distance units (kilometers, miles, degrees)
        - Cache control for performance optimization
        - Compatible with LatLonPointSpatialField and RPT fields

    How Geospatial Filtering Works:
        geofilt:
          - Creates a circular search area around a center point
          - Precise: Only includes documents within exact radius
          - Slightly slower but more accurate

        bbox:
          - Creates a rectangular bounding box around a center point
          - Faster: Uses simpler rectangular calculations
          - May include points outside the circular radius

    Distance Scoring:
        Use the score parameter to return distance as the relevance score:
        - none: Fixed score of 1.0 (default)
        - kilometers: Distance in km
        - miles: Distance in miles
        - degrees: Distance in degrees

    Schema Requirements:
        Spatial field must be indexed with appropriate field type:
        <field name="store" type="location" indexed="true" stored="true"/>
        <fieldType name="location" class="solr.LatLonPointSpatialField"/>

    Examples:
        >>> # Circular geospatial filter (precise)
        >>> parser = GeoFilterQueryParser(
        ...     spatial_field="store_location",
        ...     center_point=[45.15, -93.85],
        ...     distance=5,  # 5 km radius
        ...     filter_type="geofilt"
        ... )

        >>> # Bounding box filter (faster)
        >>> parser = GeoFilterQueryParser(
        ...     spatial_field="restaurant_coords",
        ...     center_point=[37.7749, -122.4194],  # San Francisco
        ...     distance=10,  # 10 km
        ...     filter_type="bbox"
        ... )

        >>> # With distance scoring
        >>> parser = GeoFilterQueryParser(
        ...     spatial_field="hotel_location",
        ...     center_point=[51.5074, -0.1278],  # London
        ...     distance=2,
        ...     filter_type="geofilt",
        ...     score="kilometers"  # Return distance as score
        ... )

        >>> # Disable caching for dynamic queries
        >>> parser = GeoFilterQueryParser(
        ...     spatial_field="user_location",
        ...     center_point=[40.7128, -74.0060],  # NYC
        ...     distance=1,
        ...     filter_type="geofilt",
        ...     cache=False  # Don't cache this filter
        ... )

        >>> # Filter with sorting by distance
        >>> # Combine with geodist() function query for sorting
        >>> parser = GeoFilterQueryParser(
        ...     spatial_field="store",
        ...     center_point=[45.15, -93.85],
        ...     distance=50
        ... )
        >>> # Add: &sort=geodist() asc to request

    Args:
        filter_type: 'geofilt' for circular (precise) or 'bbox' for bounding box (faster)
        spatial_field: Name of the spatial indexed field (inherited from base, required)
        center_point: [lat, lon] or [x, y] coordinates of search center (inherited, required)
        distance: Radial distance from center point (inherited, required)
        score: Scoring mode (none, kilometers, miles, degrees) (inherited from base)
        cache: Whether to cache the filter query (inherited from base)

    Returns:
        Filter query (fq) matching documents within the specified distance

    Performance Tips:
        - Use bbox for large radius searches where precision isn't critical
        - Set cache=false for highly variable queries (e.g., user location)
        - Use geofilt for small radius searches requiring precision
        - Consider using docValues for better spatial query performance

    See Also:
        - BBoxQueryParser: For querying indexed bounding boxes with spatial predicates
        - geodist() function: For distance calculations and sorting
        - Solr Spatial Search Guide: https://solr.apache.org/guide/solr/latest/query-guide/spatial-search.html
    """

    filter_type: Literal["geofilt", "bbox"] = Field(
        default="geofilt",
        description="Type of spatial filter: 'geofilt' for circular (precise) or 'bbox' for bounding box (faster)",
    )

    @computed_field(alias="q")
    def query(self) -> str:
        return "*:*"

    @computed_field(alias="fq")
    def filter_query(self) -> str:
        params: str = self.spatial_params  # type: ignore[assignment]
        params_str = f" {params}" if params else ""
        return f"{{!{self.filter_type} sfield={self.spatial_field}{params_str}}}"
