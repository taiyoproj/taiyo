"""Base configuration for Solr query parameters."""

from pydantic import BaseModel, ConfigDict


class ParamsConfig(BaseModel):
    """Base class for Solr parameter configurations.

    This class serves as the parent for all specialized parameter configuration
    classes like FacetParamsConfig, GroupParamsConfig, HighlightParamsConfig, etc.

    Attributes:
        enable_key: The Solr parameter key that enables this feature.
    """

    enable_key: str

    model_config = ConfigDict(
        populate_by_name=True, validate_by_name=True, validate_by_alias=False
    )
