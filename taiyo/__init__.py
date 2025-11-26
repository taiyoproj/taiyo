"""
Taiyo - A modern Python client for Apache Solr.
"""

from .types import (
    SolrDocument,
    SolrError,
    SolrFacetResult,
    SolrFacetFieldResult,
    SolrFacetFieldValue,
    SolrFacetRangeBucket,
    SolrFacetRangeResult,
    SolrJsonFacetBucket,
    SolrJsonFacetNode,
    SolrMoreLikeThisResult,
    SolrResponse,
)
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
    TermsQueryParser,
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
    "SolrMoreLikeThisResult",
    "SolrFacetResult",
    "SolrFacetFieldResult",
    "SolrFacetFieldValue",
    "SolrFacetRangeBucket",
    "SolrFacetRangeResult",
    "SolrJsonFacetBucket",
    "SolrJsonFacetNode",
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
    "TermsQueryParser",
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
