from typing import Any, Dict, Optional, Union, Type, TYPE_CHECKING
from abc import ABC, abstractmethod
from urllib.parse import urljoin
from pydantic import ValidationError

from taiyo.parsers.base import BaseQueryParser
from ..types import SolrResponse, DocumentT

if TYPE_CHECKING:
    from .auth import SolrAuth


class BaseSolrClient(ABC):
    """
    Base class for Solr clients.

    Args:
        base_url: Base URL of the Solr instance (e.g., "http://localhost:8983/solr")
        collection: Name of the Solr collection
        auth: Authentication method to use (optional)
        timeout: Request timeout in seconds
    """

    def __init__(
        self,
        base_url: str,
        collection: str,
        auth: Optional["SolrAuth"] = None,
        timeout: float = 10.0,
    ):
        """
        Args:
            base_url: Base URL of the Solr instance i.e. http://localhost:8983/solr.
            collection: Name of the Solr collection.
            auth: Authentication method to use (optional).
            timeout: Request timeout in seconds. Defaults to 10.
        """
        self.base_url = base_url.rstrip("/")
        self.collection = collection
        self.timeout = timeout
        self.auth = auth

    def _build_url(self, endpoint: str) -> str:
        """Build the full URL for a Solr API endpoint."""
        return urljoin(f"{self.base_url}/{self.collection}/", endpoint)

    @abstractmethod
    def _request(
        self,
        method: str,
        endpoint: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make a request to Solr and handle the response."""
        pass

    @staticmethod
    def _build_search_response(
        response: Dict[str, Any],
        document_model: Type[DocumentT],
    ) -> SolrResponse[DocumentT]:
        """Build a SolrResponse from raw Solr response data."""
        docs: list[DocumentT] = []
        for doc in response["response"]["docs"]:
            try:
                docs.append(document_model.model_validate(doc, by_name=True))
            except ValidationError:
                docs.append(document_model.model_validate(doc, by_alias=True))
            except Exception:
                raise

        return SolrResponse[document_model](
            status=response["responseHeader"]["status"],
            qtime=response["responseHeader"]["QTime"],
            num_found=response["response"]["numFound"],
            start=response["response"]["start"],
            docs=docs,
            facet_counts=response.get("facet_counts"),
            highlighting=response.get("highlighting"),
        )

    @staticmethod
    def _build_search_params(
        query: Union[str, Dict[str, Any], BaseQueryParser],
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Build search parameters from query and kwargs."""
        if isinstance(query, str):
            params = {"q": query}
        elif isinstance(query, BaseQueryParser):
            params = query.build()
        else:
            params = query

        params.update(kwargs)
        params.setdefault("wt", "json")
        return params

    @abstractmethod
    def close(self):
        """Close the underlying HTTP client."""
        pass
