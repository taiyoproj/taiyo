from taiyo.parsers.base import BaseQueryParser
from taiyo.params import DenseVectorSearchParamsMixin


class DenseVectorSearchQueryParser(BaseQueryParser, DenseVectorSearchParamsMixin):
    def build(self, *args, **kwargs):
        return self.model_dump(
            by_alias=True,
            exclude_none=True,
            exclude_unset=True,
            exclude=DenseVectorSearchParamsMixin.get_mixin_keys(),
            *args,
            **kwargs,
        )
