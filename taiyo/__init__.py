"""
Taiyo - A modern Python client for Apache Solr.
"""

from .client import SolrClient
from .types import SolrDocument, SolrResponse, SolrError
from .auth import BasicAuth, BearerAuth
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
