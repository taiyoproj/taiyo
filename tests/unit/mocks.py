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
    docs: list[Dict[str, Any]],
    facets: Dict[str, Dict[str, int]],
    json_facets: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Create a Solr response with realistic facet structures."""

    response = mock_search_response(docs)

    field_payload: Dict[str, list[Any]] = {}
    for field_name, bucket_map in facets.items():
        entries: list[Any] = []
        for value, count in bucket_map.items():
            entries.extend([value, count])
        field_payload[field_name] = entries

    response["facet_counts"] = {
        "facet_queries": {},
        "facet_fields": field_payload,
        "facet_ranges": {},
        "facet_intervals": {},
        "facet_pivot": {},
        "facet_heatmaps": {},
    }

    if json_facets is None:
        doc_count = len(docs) or 1
        default_json = {}
        if "category" in facets:
            default_json = {
                "count": len(docs),
                "by_category": {
                    "numBuckets": len(facets["category"]),
                    "buckets": [
                        {
                            "val": value,
                            "count": count,
                            "share": count / doc_count,
                        }
                        for value, count in facets["category"].items()
                    ],
                },
            }
        json_facets = default_json

    if json_facets:
        response["facets"] = json_facets

    return response


def mock_highlight_response(
    docs: list[Dict[str, Any]], highlights: Dict[str, Dict[str, list[str]]]
) -> Dict[str, Any]:
    """Create a Solr response with highlighting."""
    response = mock_search_response(docs)
    response["highlighting"] = highlights
    return response
