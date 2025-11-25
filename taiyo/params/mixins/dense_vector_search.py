from pydantic import Field, computed_field
from typing import Optional, List
from taiyo.params.mixins.base import ParamsMixin


class DenseVectorSearchParamsMixin(ParamsMixin):
    field: str = Field(
        ..., alias="f", description="DenseVectorField to search in. Required."
    )
    pre_filter: Optional[List[str]] = Field(
        default=None,
        alias="preFilter",
        description="Explicit list of pre-filter query strings.",
    )
    include_tags: Optional[List[str]] = Field(
        default=None,
        alias="includeTags",
        description="Only fq filters with these tags are considered for implicit pre-filtering.",
    )
    exclude_tags: Optional[List[str]] = Field(
        default=None,
        alias="excludeTags",
        description="fq filters with these tags are excluded from implicit pre-filtering.",
    )

    @computed_field
    def vector_search_params(self) -> str:
        params = self.model_dump(
            include=set(DenseVectorSearchParamsMixin.__annotations__.keys()),
            by_alias=True,
            exclude_computed_fields=True,
            exclude_none=True,
        )
        res = []
        for k, v in params.items():
            if isinstance(v, list):
                for vi in v:
                    res.append(f"{k}={vi}")
            else:
                res.append(f"{k}={v}")
        return " ".join(res)

    @classmethod
    def get_mixin_keys(cls) -> List[str]:
        return list(DenseVectorSearchParamsMixin.model_computed_fields.keys()) + list(
            DenseVectorSearchParamsMixin.__annotations__.keys()
        )
