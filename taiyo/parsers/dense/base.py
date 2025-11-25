from typing import Any, Dict
from taiyo.parsers.base import BaseQueryParser
from taiyo.params import DenseVectorSearchParamsMixin


class DenseVectorSearchQueryParser(BaseQueryParser, DenseVectorSearchParamsMixin):
    def build(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        params = self.model_dump(
            by_alias=True,
            exclude_none=True,
            exclude_unset=True,
            exclude=["configs", *DenseVectorSearchParamsMixin.get_mixin_keys()],  # type: ignore[arg-type]
            *args,
            **kwargs,
        )
        return self.serialize_configs(params)
