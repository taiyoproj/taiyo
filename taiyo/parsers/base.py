from typing import Any
from pydantic import ConfigDict
from taiyo.params.configs.base import ParamsConfig
from taiyo.params.mixins.common import CommonParamsMixin


class BaseQueryParser(CommonParamsMixin):
    def serialize_configs(self, params: dict[str, Any]) -> dict:
        """Serialize ParamsConfig objects as top level params."""
        updates = {}
        for config_key in params:
            if config_key in super().__dict__ and isinstance(
                super().__dict__[config_key], ParamsConfig
            ):
                updates[config_key] = True
                updates.update(params[config_key])
        params.update(updates)
        return params

    def build(self, *args, **kwargs) -> dict[str, Any]:
        """
        Serialize the parser configuration to Solr-compatible query parameters using Pydantic's model_dump.
        """
        params = self.model_dump(
            by_alias=True, exclude_none=True, exclude_unset=True, *args, **kwargs
        )
        return self.serialize_configs(params)

    model_config = ConfigDict(validate_by_alias=False, extra="forbid")
