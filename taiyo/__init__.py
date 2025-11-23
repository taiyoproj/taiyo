"""
Taiyo - A modern Python client for Apache Solr.
"""

from .types import SolrDocument, SolrResponse, SolrError
from .client import (
    BasicAuth,
    BearerAuth,
    SolrClient,
    AsyncSolrClient,
    SolrAuth,
    OAuth2Auth,
)
from .params import (
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
    # client
    "AsyncSolrClient",
    "SolrClient",
    # data models
    "SolrDocument",
    "SolrResponse",
    "SolrError",
    # auth
    "SolrAuth",
    "BasicAuth",
    "BearerAuth",
    "OAuth2Auth",
    # parsers
    "StandardParser",
    "DisMaxQueryParser",
    "ExtendedDisMaxQueryParser",
    "KNNQueryParser",
    "KNNTextToVectorQueryParser",
    "VectorSimilarityQueryParser",
    "GeoFilterQueryParser",
    # Configs
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
