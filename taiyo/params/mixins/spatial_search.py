from typing import Optional
from pydantic import Field, field_serializer
from taiyo.params.mixins.base import ParamsMixin


class SpatialSearchParamsMixin(ParamsMixin):
    spatial_field: str = Field(
        ..., alias="sfield", description="Spatial indexed field (required)"
    )
    center_point: list[float] = Field(
        ..., alias="pt", description="Center point (lat,lon or x,y) (required)"
    )
    radial_distance: float = Field(
        ..., alias="d", description="Radial distance (required)"
    )
    score: Optional[str] = Field(
        default=None,
        alias="score",
        description="Scoring mode (none, kilometers, miles, degrees, distance, recipDistance, overlapRatio, area, area2D)",
    )
    filter: Optional[bool] = Field(
        default=None,
        alias="filter",
        description="If false, only scores, does not filter (advanced)",
    )

    @field_serializer("center_point", return_type=str)
    def serialize_point(self, values: list[float]) -> str:
        return ",".join([str(v) for v in values])
