from typing import Any, Dict, Optional, Union, Type, TYPE_CHECKING, TypeVar, Generic
from abc import abstractmethod
from urllib.parse import urljoin
from pydantic import ValidationError

from taiyo.parsers.base import BaseQueryParser
from ..types import SolrResponse, DocumentT, SolrMoreLikeThisResult, SolrFacetResult
from httpx import Client, AsyncClient

if TYPE_CHECKING:
    from .auth import SolrAuth

ClientT = TypeVar("ClientT", Client, AsyncClient)


class BaseSolrClient(Generic[ClientT]):
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
        self.collection: Optional[str] = None
        self._client: ClientT

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
        grouping_result = None

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
            from taiyo.types import SolrGroup, SolrGroupedField, SolrGroupingResult

            grouped_fields = {}
            for group_field, grouped_data in response["grouped"].items():
                groups = []
                if "groups" in grouped_data:
                    for g in grouped_data.get("groups", []):
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
                        groups.append(
                            SolrGroup(
                                group_value=g.get("groupValue"),
                                doclist=doclist,
                                group_offset=g.get("groupOffset"),
                            )
                        )
                    grouped_fields[group_field] = SolrGroupedField(
                        matches=grouped_data.get("matches", 0),
                        groups=groups,
                        ngroups=grouped_data.get("ngroups"),
                        facet=grouped_data.get("facet"),
                    )
                elif "doclist" in grouped_data:
                    doclist = grouped_data.get("doclist", {})
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
                    grouped_fields[group_field] = SolrGroupedField(
                        matches=grouped_data.get("matches", 0),
                        doclist=doclist,
                        ngroups=grouped_data.get("ngroups"),
                        facet=grouped_data.get("facet"),
                    )
            # Top-level grouping params
            grouping_result = SolrGroupingResult(
                grouped=grouped_fields,
                group_sort=response.get("group.sort"),
                group_limit=response.get("group.limit"),
                group_offset=response.get("group.offset"),
                group_format=response.get("group.format"),
                distributed_caveats=response.get("distributed_caveats"),
            )
            start = 0
        else:
            # Unknown format; attempt to be graceful
            pass

        more_like_this: Optional[Dict[str, SolrMoreLikeThisResult[DocumentT]]] = None
        raw_interesting_terms = response.get("interestingTerms")
        raw_more_like_this = response.get("moreLikeThis")
        if isinstance(raw_more_like_this, dict):
            more_like_this = {}
            for doc_id, payload in raw_more_like_this.items():
                if not isinstance(payload, dict):
                    continue

                payload_docs = payload.get("docs", []) or []
                parsed_docs: list[DocumentT] = []
                for doc in payload_docs:
                    try:
                        parsed_docs.append(
                            document_model.model_validate(doc, by_name=True)
                        )
                    except ValidationError:
                        parsed_docs.append(
                            document_model.model_validate(doc, by_alias=True)
                        )
                    except Exception:
                        raise

                if isinstance(raw_interesting_terms, dict):
                    doc_interesting_terms = raw_interesting_terms.get(doc_id)
                else:
                    doc_interesting_terms = raw_interesting_terms

                more_like_this[doc_id] = SolrMoreLikeThisResult(
                    num_found=payload.get("numFound", 0),
                    start=payload.get("start", 0),
                    num_found_exact=payload.get("numFoundExact"),
                    docs=parsed_docs,
                    interesting_terms=doc_interesting_terms,
                )

        facets = SolrFacetResult.from_response(response)

        return SolrResponse(
            status=response.get("responseHeader", {}).get("status", 0),
            query_time=response.get("responseHeader", {}).get("QTime", 0),
            num_found=num_found,
            start=start,
            docs=docs,
            facets=facets,
            highlighting=response.get("highlighting"),
            more_like_this=more_like_this or None,
            grouping=grouping_result,
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
    def close(self) -> None:
        """Close the underlying HTTP client."""
        pass
