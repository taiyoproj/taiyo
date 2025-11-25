from typing import List, Optional, Literal
from pydantic import Field, field_serializer, computed_field
from taiyo.params.mixins.base import ParamsMixin


class SpatialSearchParamsMixin(ParamsMixin):
    """Base mixin for spatial search parameters used by geofilt and bbox parsers."""

    spatial_field: str = Field(
        ...,
        alias="sfield",
        description="Spatial indexed field (required)",
    )
    center_point: list[float] = Field(
        ..., alias="pt", description="Center point (lat,lon or x,y) (required)"
    )
    radial_distance: float = Field(
        ..., alias="d", description="Radial distance (required)"
    )
    score: Optional[
        Literal[
            "none",
            "kilometers",
            "miles",
            "degrees",
            "distance",
            "recipDistance",
            "overlapRatio",
            "area",
            "area2D",
        ]
    ] = Field(
        default=None,
        description="Scoring mode for spatial queries",
    )
    filter: Optional[bool] = Field(
        default=None,
        description="If false, only scores, does not filter (advanced)",
    )
    cache: Optional[bool] = Field(
        default=None,
        description="Whether to cache the filter query (default: true)",
    )

    @field_serializer("center_point", return_type=str)
    def serialize_point(self, values: list[float]) -> str:
        return ",".join([str(v) for v in values])

    @computed_field
    def spatial_params(self) -> str:
        """Build the spatial search parameters string for use in filter queries."""
        params = self.model_dump(
            include=set(SpatialSearchParamsMixin.__annotations__.keys()),
            by_alias=True,
            exclude_computed_fields=True,
            exclude_none=True,
        )
        _ = params.pop("sfield", None)

        res = []
        for k, v in params.items():
            if isinstance(v, bool):
                res.append(f"{k}={str(v).lower()}")
            else:
                res.append(f"{k}={v}")
        return " ".join(res)

    @classmethod
    def get_mixin_keys(cls) -> List[str]:
        return list(SpatialSearchParamsMixin.model_computed_fields.keys()) + list(
            SpatialSearchParamsMixin.__annotations__.keys()
        )
