from typing import Literal, Optional
from pydantic import Field, computed_field, field_serializer
from ..base import BaseQueryParser


class BBoxQueryParser(BaseQueryParser):
    """BBoxField Query Parser for Apache Solr Spatial Bounding Box Search.

    The BBoxField parser enables searching on indexed bounding boxes (rectangles) using
    spatial predicates. Unlike the bbox filter parser which finds points within a distance,
    this parser performs shape-to-shape comparisons using predicates like Contains,
    Intersects, and Within.

    Solr Reference:
        https://solr.apache.org/guide/solr/latest/query-guide/spatial-search.html

    Key Features:
        - Index and query rectangular bounding boxes
        - Multiple spatial predicates (Contains, Intersects, Within, etc.)
        - Advanced scoring (overlap ratio, area calculations)
        - Efficient for rectangular region queries
        - Supports both geographic and Cartesian coordinates

    How BBoxField Works:
        - Documents contain bounding boxes (e.g., store delivery areas, parcels, regions)
        - Queries test spatial relationships between query shape and indexed shapes
        - Predicates determine which documents match based on spatial relationship
        - Scoring modes calculate relevance based on shape overlap

    Spatial Predicates:
        Contains:
          - Matches when indexed bbox contains the query shape
          - Use case: Find regions that fully contain a point or area

        Intersects:
          - Matches when indexed bbox intersects with query shape
          - Use case: Find regions that overlap with an area

        Within/IsWithin:
          - Matches when indexed bbox is within the query shape
          - Use case: Find regions fully contained by a larger area

        IsDisjointTo:
          - Matches when indexed bbox does not intersect query shape
          - Use case: Find regions that don't overlap with an area

    Scoring Modes:
        overlapRatio:
          - Relative overlap between shapes (0.0 to 1.0)
          - Good for ranking by coverage

        area:
          - Absolute overlapping area (haversine-based for geo)
          - Good for ranking by size of overlap

        area2D:
          - Absolute overlapping area (cartesian coordinates)
          - Good for non-geographic projections

    WKT ENVELOPE Syntax:
        Format: ENVELOPE(minX, maxX, maxY, minY)
        - minX: Western edge (longitude)
        - maxX: Eastern edge (longitude)
        - maxY: Northern edge (latitude)
        - minY: Southern edge (latitude)

        Example: ENVELOPE(-122.5, -122.3, 37.8, 37.7)
        (San Francisco area: west, east, north, south)

    Schema Requirements:
        BBoxField type must be configured:
        <field name="bbox" type="bbox" />
        <fieldType name="bbox" class="solr.BBoxField"
                   geo="true" distanceUnits="kilometers" numberType="pdouble" />
        <fieldType name="pdouble" class="solr.DoublePointField" docValues="true"/>

    Examples:
        >>> # Find delivery areas containing a location
        >>> parser = BBoxQueryParser(
        ...     bbox_field="delivery_area",
        ...     predicate="Contains",
        ...     envelope=[-122.4, -122.4, 37.8, 37.8],  # Point as tiny box
        ... )

        >>> # Find parcels intersecting a search area
        >>> parser = BBoxQueryParser(
        ...     bbox_field="land_parcel",
        ...     predicate="Intersects",
        ...     envelope=[-10, 20, 15, 10],  # Search rectangle
        ...     score="overlapRatio"  # Score by overlap percentage
        ... )

        >>> # Find small regions within a larger area
        >>> parser = BBoxQueryParser(
        ...     bbox_field="city_bounds",
        ...     predicate="Within",
        ...     envelope=[-180, 180, 90, -90],  # Whole world
        ... )

        >>> # Find zones that don't overlap with restricted area
        >>> parser = BBoxQueryParser(
        ...     bbox_field="service_zone",
        ...     predicate="IsDisjointTo",
        ...     envelope=[-122.5, -122.3, 37.8, 37.7],  # Restricted area
        ... )

        >>> # Score by absolute overlapping area
        >>> parser = BBoxQueryParser(
        ...     bbox_field="coverage_area",
        ...     predicate="Intersects",
        ...     envelope=[-100, -90, 40, 35],
        ...     score="area"  # Score by km² of overlap
        ... )

    Indexing BBoxField Data:
        Documents must use WKT ENVELOPE syntax:
        {
          "id": "store1",
          "bbox": "ENVELOPE(-122.5, -122.3, 37.8, 37.7)"
        }

    Args:
        bbox_field: Name of the BBoxField to query (required)
        predicate: Spatial predicate to use (default: "Intersects")
            Options: Contains, Intersects, Within, IsWithin, IsDisjointTo
        envelope: Bounding box as [minX, maxX, maxY, minY] (required)
        score: Scoring mode (default: None)
            Options: overlapRatio, area, area2D

    Returns:
        Query matching documents based on spatial predicate and bbox relationship

    Note:
        BBoxField is optimized for indexing bounding boxes. For point-based
        spatial search, use LatLonPointSpatialField with geofilt/bbox parsers.

    See Also:
        - GeoFilterQueryParser: For point-based distance filtering
        - Solr Spatial Search: https://solr.apache.org/guide/solr/latest/query-guide/spatial-search.html
        - JTS Spatial: For complex polygon support
    """

    bbox_field: str = Field(
        ...,
        description="Name of the BBoxField to query",
    )

    predicate: Literal[
        "Contains", "Intersects", "Within", "IsWithin", "IsDisjointTo"
    ] = Field(
        default="Intersects",
        description="Spatial predicate to use",
    )

    envelope: list[float] = Field(
        ...,
        description="Bounding box as [minX, maxX, maxY, minY]",
    )

    score: Optional[Literal["overlapRatio", "area", "area2D"]] = Field(
        default=None,
        description="Scoring mode for BBoxField queries",
    )

    @field_serializer("envelope", return_type=str)
    def serialize_envelope(self, values: list[float]) -> str:
        """Serialize envelope to WKT ENVELOPE format."""
        minX, maxX, maxY, minY = values
        return f"ENVELOPE({minX}, {maxX}, {maxY}, {minY})"

    @computed_field(alias="q")
    def query(self) -> str:
        """Constructs the BBoxField query with predicate and envelope."""
        envelope_str = self.serialize_envelope(self.envelope)
        score_param = f" score={self.score}" if self.score else ""
        return f"{{!field f={self.bbox_field}{score_param}}}{self.predicate}({envelope_str})"
