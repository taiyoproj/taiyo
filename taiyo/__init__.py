"""
Taiyo - A modern Python client for Apache Solr.
"""

from .types import SolrDocument, SolrResponse, SolrError
from .client import BasicAuth, BearerAuth, SolrClient, AsyncSolrClient
from .parsers import (
    KNNQueryParser,
    KNNTextToVectorQueryParser,
    VectorSimilarityParser,
    StandardParser,
    DisMaxQueryParser,
    ExtendedDisMaxQueryParser,
    BoundingBoxQueryParser,
    GeoFilterQueryParser,
)

__version__ = "0.1.0"
__all__ = [
    "AsyncSolrClient",
    "SolrClient",
    "SolrQuery",
    "SolrDocument",
    "SolrResponse",
    "SolrError",
    "BasicAuth",
    "BearerAuth",
    "StandardParser",
    "DisMaxQueryParser",
    "ExtendedDisMaxQueryParser",
    "KNNQueryParser",
    "KNNTextToVectorQueryParser",
    "VectorSimilarityParser",
    "BoundingBoxQueryParser",
    "GeoFilterQueryParser",
]
