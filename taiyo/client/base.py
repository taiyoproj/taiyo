from typing import Any, Dict, Optional, Union, Type, TYPE_CHECKING
from abc import abstractmethod
from urllib.parse import urljoin
from pydantic import ValidationError

from taiyo.parsers.base import BaseQueryParser
from ..types import SolrResponse, DocumentT
from httpx import Client, AsyncClient

if TYPE_CHECKING:
    from .auth import SolrAuth


class BaseSolrClient:
    """
    Base class for Solr clients.

    Args:
        base_url: Base URL of the Solr instance (e.g., "http://localhost:8983/solr")
        collection: Name of the Solr collection
        auth: Authentication method to use (optional)
        timeout: Request timeout in seconds
        verify: SSL certificate verification (default: True)
    """

    def __init__(
        self,
        base_url: str,
        auth: Optional["SolrAuth"] = None,
        timeout: float = 10.0,
        verify: Union[bool, str] = True,
    ):
        """
        Args:
            base_url: Base URL of the Solr instance i.e. http://localhost:8983/solr.
            collection: Name of the Solr collection.
            auth: Authentication method to use (optional).
            timeout: Request timeout in seconds. Defaults to 10.
            verify: SSL certificate verification. Can be True (default), False, or path to CA bundle.
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.auth = auth
        self.verify = verify
        self.collection = None
        self._client: Client | AsyncClient

    def _build_url(self, endpoint: str) -> str:
        """Build the full URL for a Solr API endpoint."""
        return urljoin(f"{self.base_url}/", endpoint)

    def set_collection(self, collection: str) -> None:
        self.collection = collection
        return None

    def set_header(self, key: str, value: Any) -> None:
        self._client.headers[key] = value
        return None

    def unset_header(self, key: str) -> None:
        if key in self._client.headers:
            del self._client.headers[key]
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
    def _build_delete_command(
        query: Optional[str] = None,
        ids: Optional[Union[str, list[str]]] = None,
    ) -> Union[str, list[str], Dict[str, Any]]:
        """Build delete command according to Solr specification."""
        if ids and not query:
            if isinstance(ids, str):
                return ids
            if isinstance(ids, list) and len(ids) == 1:
                return ids[0]
            return ids

        if query and not ids:
            return {"query": query}

        return {
            "query": query,
            "id": ids if isinstance(ids, str) else ids,
        }

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
