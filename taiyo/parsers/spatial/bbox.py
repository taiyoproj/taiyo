from typing import Literal, Optional
from pydantic import Field, computed_field, field_serializer
from ..base import BaseQueryParser


class BBoxQueryParser(BaseQueryParser):
    """
    Parser for querying Solr BBoxField types with spatial predicates.

    BBoxField is designed for indexing bounding boxes (rectangles) and supports
    spatial predicates like Contains, Intersects, Within, IsWithin, and IsDisjointTo.
    This is different from the bbox query parser which filters by distance from a point.

    The field must be indexed using WKT ENVELOPE syntax:
        ENVELOPE(minX, maxX, maxY, minY)
        Example: ENVELOPE(-10, 20, 15, 10)

    Schema configuration example:
        <field name="bbox" type="bbox" />
        <fieldType name="bbox" class="solr.BBoxField"
                   geo="true" distanceUnits="kilometers" numberType="pdouble" />

    Examples:
        # Query for bounding boxes that contain a point/shape
        &q={!field f=bbox}Contains(ENVELOPE(-10, 20, 15, 10))

        # Query with Intersects predicate and scoring
        &q={!field f=bbox score=overlapRatio}Intersects(ENVELOPE(-10, 20, 15, 10))

        # Filter query with IsWithin predicate
        &fq={!field f=bbox}IsWithin(ENVELOPE(-180, 180, 90, -90))

    Supported spatial predicates:
        - Contains(shape): Indexed shape contains the query shape
        - Intersects(shape): Indexed shape intersects the query shape
        - Within(shape): Indexed shape is within the query shape
        - IsWithin(shape): Alias for Within
        - IsDisjointTo(shape): Indexed shape does not intersect query shape

    Supported scoring modes:
        - overlapRatio: Relative overlap between indexed shape & query shape
        - area: Haversine-based area of overlapping shapes
        - area2D: Cartesian-based area of overlapping shapes
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
    @property
    def query(self) -> str:
        """Constructs the BBoxField query with predicate and envelope."""
        envelope_str = self.serialize_envelope(self.envelope)
        score_param = f" score={self.score}" if self.score else ""
        return f"{{!field f={self.bbox_field}{score_param}}}{self.predicate}({envelope_str})"
