from typing import Literal
from pydantic import Field
from ..base import BaseQueryParser
from taiyo.params import SpatialSearchParamsMixin


class BoundingBoxQueryParser(BaseQueryParser, SpatialSearchParamsMixin):
    """
    Parser for Solr's bbox spatial query parser.
    """

    def_type: Literal["bbox"] = Field(
        "bbox",
        alias="defType",
        description="defType for bbox parser",
    )
