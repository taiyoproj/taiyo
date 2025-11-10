"""Mock responses for Solr API endpoints."""

from typing import Dict, Any


def mock_solr_response(status: int = 0, qtime: int = 5) -> Dict[str, Any]:
    """Create a basic Solr response structure."""
    return {"responseHeader": {"status": status, "QTime": qtime, "params": {}}}


def mock_solr_error(message: str, code: int = 400) -> Dict[str, Any]:
    """Create a Solr error response."""
    return {
        "responseHeader": {"status": code, "QTime": 5},
        "error": {"code": code, "message": message},
    }


def mock_search_response(
    docs: list[Dict[str, Any]], num_found: int = None, start: int = 0
) -> Dict[str, Any]:
    """Create a Solr search response with documents."""
    if num_found is None:
        num_found = len(docs)

    return {
        **mock_solr_response(),
        "response": {"numFound": num_found, "start": start, "docs": docs},
    }


def mock_update_response(status: int = 0) -> Dict[str, Any]:
    """Create a Solr update response."""
    return mock_solr_response(status=status)


def mock_delete_response(status: int = 0) -> Dict[str, Any]:
    """Create a Solr delete response."""
    return mock_solr_response(status=status)


def mock_facet_response(
    docs: list[Dict[str, Any]], facets: Dict[str, Dict[str, int]]
) -> Dict[str, Any]:
    """Create a Solr response with facets."""
    response = mock_search_response(docs)
    response["facet_counts"] = {"facet_fields": facets}
    return response


def mock_highlight_response(
    docs: list[Dict[str, Any]], highlights: Dict[str, Dict[str, list[str]]]
) -> Dict[str, Any]:
    """Create a Solr response with highlighting."""
    response = mock_search_response(docs)
    response["highlighting"] = highlights
    return response
