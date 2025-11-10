from pydantic import Field, computed_field
from taiyo.parsers.sparse.dismax import DisMaxQueryParser
from typing import Literal


from typing import Optional, Dict


class ExtendedDisMaxQueryParser(DisMaxQueryParser):
    split_on_whitespace: Optional[bool] = Field(
        default=None,
        description="Split on whitespace. If true, analyze each whitespace-separated term separately.",
    )
    min_match_auto_relax: Optional[bool] = Field(
        default=None,
        alias="mm.autoRelax",
        description="Automatically relax mm if clauses are removed by stopwords.",
    )
    lowercase_operators: Optional[bool] = Field(
        default=None,
        alias="lowercaseOperators",
        description="Treat lowercase 'and'/'or' as operators.",
    )
    phrase_fields_bigram: Optional[Dict[str, float]] = Field(
        default=None, description="Phrase fields for bigrams with boosts."
    )
    phrase_slop_bigram: Optional[int] = Field(
        default=None, description="Slop for bigram phrase fields."
    )
    phrase_fields_trigram: Optional[Dict[str, float]] = Field(
        default=None, description="Phrase fields for trigrams with boosts."
    )
    phrase_slop_trigram: Optional[int] = Field(
        default=None, description="Slop for trigram phrase fields."
    )
    stopwords: Optional[bool] = Field(
        default=None, description="Respect stopword filter in analyzer."
    )
    user_fields: Optional[list[str]] = Field(
        default=None, description="User fields allowed for explicit query."
    )

    @computed_field(alias="defType")
    @property
    def def_type(self) -> Literal["edismax"]:
        return "edismax"
