from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, List, Optional, TypeVar, Generic, Union


class SolrDocument(BaseModel):
    """Base model for Solr documents."""

    model_config: ConfigDict = {
        "extra": "allow",
    }


DocumentT = TypeVar("DocumentT", bound=SolrDocument)


InterestingTermsType = Union[List[Any], Dict[str, Any]]


class SolrMoreLikeThisResult(BaseModel, Generic[DocumentT]):
    """BaseModel for MoreLikeThis matches."""

    num_found: int = Field(default=0, alias="numFound")
    start: int = 0
    num_found_exact: Optional[bool] = Field(default=None, alias="numFoundExact")
    docs: List[DocumentT] = Field(default_factory=list)
    interesting_terms: Optional[InterestingTermsType] = None

    model_config = ConfigDict(populate_by_name=True, validate_by_name=True)


class SolrResponse(BaseModel, Generic[DocumentT]):
    """Model representing a Solr response."""

    status: int
    query_time: int = Field(alias="qtime")
    num_found: int = Field(alias="numFound")
    start: int = 0
    docs: List[DocumentT]
    facet_counts: Optional[Dict[str, Any]] = None
    highlighting: Optional[Dict[str, Dict[str, List[str]]]] = None
    more_like_this: Optional[Dict[str, SolrMoreLikeThisResult[DocumentT]]] = Field(
        default=None, alias="moreLikeThis"
    )
    extra: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(populate_by_name=True, validate_by_name=True)


class SolrError(Exception):
    """Base exception for Solr-related errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response = response
