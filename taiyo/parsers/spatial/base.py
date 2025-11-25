from typing import Any, Dict
from taiyo.parsers.base import BaseQueryParser
from taiyo.params import SpatialSearchParamsMixin


class SpatialQueryParser(BaseQueryParser, SpatialSearchParamsMixin):
    """Base class for spatial query parsers (geofilt, bbox)."""

    def build(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Build query parameters, excluding mixin keys."""
        params = self.model_dump(
            by_alias=True,
            exclude_none=True,
            exclude_unset=True,
            exclude=["configs", *SpatialSearchParamsMixin.get_mixin_keys()],  # type: ignore[arg-type]
            *args,
            **kwargs,
        )
        return self.serialize_configs(params)
