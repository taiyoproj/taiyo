from taiyo.parsers.base import BaseQueryParser
from taiyo.params import SpatialSearchParamsMixin


class SpatialQueryParser(BaseQueryParser, SpatialSearchParamsMixin):
    """Base class for spatial query parsers (geofilt, bbox)."""

    def build(self, *args, **kwargs):
        """Build query parameters, excluding mixin keys."""
        return self.model_dump(
            by_alias=True,
            exclude_none=True,
            exclude_unset=True,
            exclude=SpatialSearchParamsMixin.get_mixin_keys(),
            *args,
            **kwargs,
        )
