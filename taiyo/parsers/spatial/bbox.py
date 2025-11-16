from typing import Literal
from pydantic import computed_field
from ..base import BaseQueryParser
from taiyo.params import SpatialSearchParamsMixin


class BoundingBoxQueryParser(BaseQueryParser, SpatialSearchParamsMixin):
    """
    Parser for Solr's bbox spatial query parser.
    """

    _def_type: Literal["bbox"] = "bbox"

    @computed_field(alias="q")
    @property
    def query(self) -> str:
        return "*:*"

    @computed_field(alias="fq")
    @property
    def filter_query(self) -> str:
        return f"{{!{self._def_type} sfield={self.spatial_field}}}"
