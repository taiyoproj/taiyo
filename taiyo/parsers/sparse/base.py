from pydantic import Field

from taiyo.params import (
    FacetParamsConfig,
    HighlightParamsConfig,
    GroupParamsConfig,
    MoreLikeThisParamsConfig,
)
from taiyo.parsers.base import BaseQueryParser
from typing import Optional


class SparseQueryParser(BaseQueryParser):
    group: Optional[GroupParamsConfig] = Field(
        default=None,
        description="Configuration object for Grouping feature.",
    )
    facet: Optional[FacetParamsConfig] = Field(
        default=None,
        description="Configuration object for Faceting feature.",
    )
    highlight: Optional[HighlightParamsConfig] = Field(
        default=None,
        description="Configuration object for Highlighting feature.",
    )
    more_like_this: Optional[MoreLikeThisParamsConfig] = Field(
        default=None,
        description="Configuration object for MoreLikeThis feature.",
    )
