from typing import Literal
from pydantic import Field
from ..base import BaseQueryParser
from taiyo.params import SpatialSearchParamsMixin


class GeoFilterQueryParser(BaseQueryParser, SpatialSearchParamsMixin):
    """
    Parser for Solr's geofilt spatial query parser.
    """

    def_type: Literal["geofilt"] = Field(
        "geofilt",
        alias="defType",
        description="defType for geofilt parser",
    )
