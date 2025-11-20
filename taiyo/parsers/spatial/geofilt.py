from typing import Literal
from pydantic import computed_field, Field
from .base import SpatialQueryParser


class GeoFilterQueryParser(SpatialQueryParser):
    """
    Parser for Solr's geospatial filter query parsers (geofilt and bbox).

    The geofilt filter retrieves documents based on their geospatial distance
    from a specified point, effectively creating a circular search area.

    The bbox filter is similar but uses a bounding box instead of a circle.
    It can be faster, though it may include points outside the specified radius.

    Examples:
        # Using geofilt (circular, precise)
        &q=*:*&fq={!geofilt sfield=store}&pt=45.15,-93.85&d=5

        # Using bbox (rectangular, faster)
        &q=*:*&fq={!bbox sfield=store}&pt=45.15,-93.85&d=5

    Required parameters:
        - sfield: Spatial indexed field
        - pt: Center point (lat,lon or x,y)
        - d: Radial distance

    Optional parameters:
        - filter_type: 'geofilt' (default, circular) or 'bbox' (rectangular, faster)
        - score: Scoring mode (none, kilometers, miles, degrees, etc.)
        - filter: If false, only scores without filtering
        - cache: Whether to cache the filter query
    """

    filter_type: Literal["geofilt", "bbox"] = Field(
        default="geofilt",
        description="Type of spatial filter: 'geofilt' for circular (precise) or 'bbox' for bounding box (faster)",
    )

    @computed_field(alias="q")
    @property
    def query(self) -> str:
        return "*:*"

    @computed_field(alias="fq")
    @property
    def filter_query(self) -> str:
        params = self.spatial_params
        params_str = f" {params}" if params else ""
        return f"{{!{self.filter_type} sfield={self.spatial_field}{params_str}}}"
