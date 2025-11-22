"""
Taiyo - A modern Python client for Apache Solr.
"""

from .types import SolrDocument, SolrResponse, SolrError
from .client import BasicAuth, BearerAuth, SolrClient, AsyncSolrClient
from .params import (
    CommonParamsMixin,
    DenseVectorSearchParamsMixin,
    SpatialSearchParamsMixin,
    FacetParamsConfig,
    FacetMethod,
    FacetSort,
    GroupParamsConfig,
    HighlightParamsConfig,
    HighlightMethod,
    HighlightEncoder,
    BreakIteratorType,
    FragListBuilder,
    FragmentsBuilder,
    Fragmenter,
    MoreLikeThisParamsConfig,
)
from .parsers import (
    KNNQueryParser,
    KNNTextToVectorQueryParser,
    VectorSimilarityQueryParser,
    StandardParser,
    DisMaxQueryParser,
    ExtendedDisMaxQueryParser,
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
    "VectorSimilarityQueryParser",
    "GeoFilterQueryParser",
    "CommonParamsMixin",
    "DenseVectorSearchParamsMixin",
    "SpatialSearchParamsMixin",
    "FacetParamsConfig",
    "FacetMethod",
    "FacetSort",
    "GroupParamsConfig",
    "HighlightParamsConfig",
    "HighlightMethod",
    "HighlightEncoder",
    "BreakIteratorType",
    "FragListBuilder",
    "FragmentsBuilder",
    "Fragmenter",
    "MoreLikeThisParamsConfig",
]
