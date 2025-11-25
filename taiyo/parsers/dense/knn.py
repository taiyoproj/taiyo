from typing import Optional, Literal
from pydantic import Field, computed_field
from taiyo.parsers.dense.base import DenseVectorSearchQueryParser


class KNNQueryParser(DenseVectorSearchQueryParser):
    """K-Nearest Neighbors (KNN) Query Parser for Apache Solr Dense Vector Search.

    The KNN query parser enables efficient similarity searches on dense vector fields using
    the k-nearest neighbors algorithm. It finds the topK documents whose vectors are most
    similar to the query vector according to the configured similarity function (cosine,
    dot product, or euclidean).

    Solr Reference:
        https://solr.apache.org/guide/solr/latest/query-guide/dense-vector-search.html

    Key Features:
        - Efficient vector similarity search using HNSW algorithm
        - Configurable k (topK) for number of results
        - Pre-filtering support (explicit or implicit)
        - Re-ranking capability for hybrid search
        - Multiple similarity functions: cosine, dot_product, euclidean

    How KNN Search Works:
        1. Query vector is compared against indexed vectors
        2. HNSW (Hierarchical Navigable Small World) algorithm efficiently finds neighbors
        3. Top k most similar vectors are returned
        4. Similarity score is used for ranking

    Pre-Filtering:
        - Implicit: All fq filters (except post filters) automatically pre-filter when knn is main query
        - Explicit: Use preFilter parameter to specify filtering criteria
        - Tagged: Use includeTags/excludeTags to control which fq filters apply

    Schema Requirements:
        Field must be DenseVectorField with matching vector dimension:
        <fieldType name="knn_vector" class="solr.DenseVectorField"
                   vectorDimension="4" similarityFunction="cosine"
                   knnAlgorithm="hnsw"/>
        <field name="vector" type="knn_vector" indexed="true" stored="true"/>

    Examples:
        >>> # Basic KNN search
        >>> parser = KNNQueryParser(
        ...     vector_field="film_vector",
        ...     vector=[0.1, 0.2, 0.3, 0.4, 0.5],
        ...     top_k=10
        ... )

        >>> # With explicit pre-filtering
        >>> parser = KNNQueryParser(
        ...     vector_field="product_vector",
        ...     vector=[1.0, 2.0, 3.0, 4.0],
        ...     top_k=20,
        ...     pre_filter=["category:electronics", "inStock:true"]
        ... )

        >>> # With tagged filtering
        >>> parser = KNNQueryParser(
        ...     vector_field="doc_vector",
        ...     vector=[0.5, 0.5, 0.5, 0.5],
        ...     top_k=50,
        ...     include_tags=["for_knn"]
        ... )

        >>> # For re-ranking (use as rq parameter)
        >>> parser = KNNQueryParser(
        ...     vector_field="content_vector",
        ...     vector=[0.2, 0.3, 0.4, 0.5],
        ...     top_k=100  # Searches whole index in re-ranking context
        ... )

    Args:
        vector: Query vector as list of floats (required, must match field dimension)
        top_k: Number of nearest neighbors to return (default: 10)
        vector_field: Name of the DenseVectorField to search (inherited from base)
        pre_filter: Explicit pre-filter query strings (inherited from base)
        include_tags: Only use fq filters with these tags for implicit pre-filtering (inherited)
        exclude_tags: Exclude fq filters with these tags from implicit pre-filtering (inherited)

    Returns:
        Query results ranked by vector similarity score

    Note:
        When used in re-ranking (rq parameter), topK refers to k-nearest neighbors
        in the whole index, not just the initial result set.

    See Also:
        - VectorSimilarityQueryParser: For threshold-based vector search
        - KNNTextToVectorQueryParser: For text-to-vector conversion with KNN search
    """

    vector: list[float] = Field(
        ...,
        alias="vector",
        exclude=True,
        description="Query vector for knn/vectorSimilarity.",
    )
    top_k: Optional[int] = Field(
        default=10,
        alias="topK",
        exclude=True,
        description="How many k-nearest results to return.",
    )

    _def_type: Literal["knn"] = "knn"

    @computed_field(alias="q")
    def query(self) -> str:
        return f"{{!{self._def_type} topK={self.top_k} {self.vector_search_params}}}{self.vector}"
