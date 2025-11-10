from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, List, Optional, TypeVar, Generic


class SolrDocument(BaseModel):
    """Base model for Solr documents."""

    model_config: ConfigDict = {
        "extra": "allow",
    }


DocumentT = TypeVar("DocumentT", bound=SolrDocument)


class SolrResponse(BaseModel, Generic[DocumentT]):
    """Model representing a Solr response."""

    status: int
    query_time: int = Field(alias="qtime")
    num_found: int = Field(alias="numFound")
    start: int = 0
    docs: List[DocumentT]
    facet_counts: Optional[Dict[str, Any]] = None
    highlighting: Optional[Dict[str, Dict[str, List[str]]]] = None

    model_config = ConfigDict(validate_by_name=True)


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
