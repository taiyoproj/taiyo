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
        self.timeout = timeout
        self.auth = auth
        self.collection = None

    def _build_url(self, endpoint: str) -> str:
        """Build the full URL for a Solr API endpoint."""
        return urljoin(f"{self.base_url}/", endpoint)

    def set_collection(self, collection: str) -> None:
        self.collection = collection
        return None

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
        """Build a SolrResponse from raw Solr response data.

        Supports both standard search responses (with top-level 'response') and
        grouped responses (with top-level 'grouped').
        """
        docs: list[DocumentT] = []
        num_found: int = 0
        start: int = 0

        if "response" in response:
            # Standard search response
            for doc in response["response"]["docs"]:
                try:
                    docs.append(document_model.model_validate(doc, by_name=True))
                except ValidationError:
                    docs.append(document_model.model_validate(doc, by_alias=True))
                except Exception:
                    raise
            num_found = response["response"]["numFound"]
            start = response["response"]["start"]
        elif "grouped" in response:
            # Grouped response; flatten docs for convenience
            for _group_field, grouped_data in response["grouped"].items():
                groups = grouped_data.get("groups", [])
                for g in groups:
                    doclist = g.get("doclist", {})
                    for doc in doclist.get("docs", []):
                        try:
                            docs.append(
                                document_model.model_validate(doc, by_name=True)
                            )
                        except ValidationError:
                            docs.append(
                                document_model.model_validate(doc, by_alias=True)
                            )
                        except Exception:
                            raise
                    num_found += int(doclist.get("numFound", 0))
            start = 0
        else:
            # Unknown format; attempt to be graceful
            pass

        return SolrResponse[document_model](
            status=response.get("responseHeader", {}).get("status", 0),
            qtime=response.get("responseHeader", {}).get("QTime", 0),
            num_found=num_found,
            start=start,
            docs=docs,
            facet_counts=response.get("facet_counts"),
            highlighting=response.get("highlighting"),
            extra=response,
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
