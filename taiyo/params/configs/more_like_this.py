from pydantic import Field, computed_field
from typing import Optional, Union

from taiyo.params.configs.base import ParamsConfig


class MoreLikeThisParamsConfig(ParamsConfig):
    fields: Optional[Union[str, list[str]]] = Field(
        default=None,
        alias="mlt.fl",
        description="Fields to use for similarity (comma-separated or list).",
    )
    min_term_freq: Optional[int] = Field(
        default=None,
        alias="mlt.mintf",
        description="Minimum term frequency in the source document.",
    )
    min_doc_freq: Optional[int] = Field(
        default=None,
        alias="mlt.mindf",
        description="Minimum document frequency for terms.",
    )
    max_doc_freq: Optional[int] = Field(
        default=None,
        alias="mlt.maxdf",
        description="Maximum document frequency for terms.",
    )
    max_doc_freq_pct: Optional[int] = Field(
        default=None,
        alias="mlt.maxdfpct",
        description="Maximum document frequency as a percent of docs in the index.",
    )
    min_word_len: Optional[int] = Field(
        default=None, alias="mlt.minwl", description="Minimum word length."
    )
    max_word_len: Optional[int] = Field(
        default=None, alias="mlt.maxwl", description="Maximum word length."
    )
    max_query_terms: Optional[int] = Field(
        default=None, alias="mlt.maxqt", description="Maximum number of query terms."
    )
    max_num_tokens_parsed: Optional[int] = Field(
        default=None,
        alias="mlt.maxntp",
        description="Maximum number of tokens to parse per field.",
    )
    boost: Optional[bool] = Field(
        default=None,
        alias="mlt.boost",
        description="Boost query by interesting term relevance.",
    )
    query_fields: Optional[str] = Field(
        default=None,
        alias="mlt.qf",
        description="Query fields and boosts (must also be in mlt.fl).",
    )
    interesting_terms: Optional[str] = Field(
        default=None,
        alias="mlt.interestingTerms",
        description="Show top terms used for the MoreLikeThis query ('list', 'none', 'details').",
    )
    match_include: Optional[bool] = Field(
        default=None,
        alias="mlt.match.include",
        description="Include the matched document in the response.",
    )
    match_offset: Optional[int] = Field(
        default=None,
        alias="mlt.match.offset",
        description="Offset into main query results for the doc to use.",
    )
