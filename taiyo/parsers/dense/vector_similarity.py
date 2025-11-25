from typing import Optional, Literal
from pydantic import Field, computed_field

from taiyo.parsers.dense.base import DenseVectorSearchQueryParser


class VectorSimilarityQueryParser(DenseVectorSearchQueryParser):
    """Vector Similarity Query Parser for Apache Solr Dense Vector Search.

    The vectorSimilarity parser matches documents whose vector similarity to the query vector
    exceeds a minimum threshold. Unlike KNN which returns a fixed number of top results, this
    parser returns all documents meeting the similarity criteria, making it suitable for
    threshold-based retrieval.

    Solr Reference:
        https://solr.apache.org/guide/solr/latest/query-guide/dense-vector-search.html

    Key Features:
        - Threshold-based vector matching (minReturn)
        - Graph traversal control (minTraverse)
        - Pre-filtering support (explicit or implicit)
        - Returns all documents above similarity threshold
        - Useful for minimum quality requirements

    How Vector Similarity Works:
        1. Query vector is compared against indexed vectors
        2. Documents with similarity >= minReturn are returned
        3. Graph traversal continues for nodes with similarity >= minTraverse
        4. Results are ranked by similarity score

    Similarity vs KNN:
        - KNN: Returns exactly k results (top k most similar)
        - VectorSimilarity: Returns all results above threshold (0 to unlimited)
        - KNN: Best for "find similar items"
        - VectorSimilarity: Best for "find items similar enough"

    Schema Requirements:
        Field must be DenseVectorField with matching vector dimension:
        <fieldType name="knn_vector" class="solr.DenseVectorField"
                   vectorDimension="4" similarityFunction="cosine"
                   knnAlgorithm="hnsw"/>
        <field name="vector" type="knn_vector" indexed="true" stored="true"/>

    Examples:
        >>> # Basic similarity search with threshold
        >>> parser = VectorSimilarityQueryParser(
        ...     vector_field="product_vector",
        ...     vector=[1.0, 2.0, 3.0, 4.0],
        ...     min_return=0.7  # Only return docs with similarity >= 0.7
        ... )

        >>> # With traversal control
        >>> parser = VectorSimilarityQueryParser(
        ...     vector_field="doc_vector",
        ...     vector=[0.5, 0.5, 0.5, 0.5],
        ...     min_return=0.8,  # Return threshold
        ...     min_traverse=0.6  # Continue graph traversal threshold
        ... )

        >>> # With explicit pre-filtering
        >>> parser = VectorSimilarityQueryParser(
        ...     vector_field="content_vector",
        ...     vector=[0.2, 0.3, 0.4, 0.5],
        ...     min_return=0.75,
        ...     pre_filter=["inStock:true", "price:[* TO 100]"]
        ... )

        >>> # As filter query for hybrid search
        >>> # Use with q=*:* to get all docs above similarity threshold
        >>> parser = VectorSimilarityQueryParser(
        ...     vector_field="embedding",
        ...     vector=[1.5, 2.5, 3.5, 4.5],
        ...     min_return=0.85
        ... )

    Args:
        vector: Query vector as list of floats (required, must match field dimension)
        min_return: Minimum similarity threshold for returned documents (required)
        min_traverse: Minimum similarity to continue graph traversal (default: -Infinity)
        vector_field: Name of the DenseVectorField to search (inherited from base)
        pre_filter: Explicit pre-filter query strings (inherited from base)
        include_tags: Only use fq filters with these tags for implicit pre-filtering (inherited)
        exclude_tags: Exclude fq filters with these tags from implicit pre-filtering (inherited)

    Returns:
        All documents with vector similarity >= minReturn, ranked by similarity score

    Note:
        Setting minTraverse lower than minReturn allows exploring more of the graph
        to find potential matches, at the cost of more computation.

    See Also:
        - KNNQueryParser: For top-k nearest neighbor retrieval
        - KNNTextToVectorQueryParser: For text-based vector similarity search
    """

    vector: list[float] = Field(
        ...,
        alias="vector",
        exclude=True,
        description="Query vector for knn/vectorSimilarity.",
    )
    min_return: Optional[float] = Field(
        default=None,
        alias="minReturn",
        exclude=True,
        description="Minimum similarity threshold for returned matches (vectorSimilarity).",
    )
    min_traverse: Optional[float] = Field(
        default=None,
        alias="minTraverse",
        exclude=True,
        description="Minimum similarity to continue traversal (vectorSimilarity).",
    )

    _def_type: Literal["vectorSimilarity"] = "vectorSimilarity"

    @computed_field(alias="q")
    def query(self) -> str:
        return f"{{!{self._def_type} minTraverse={self.min_traverse} minReturn={self.min_return} {self.vector_search_params}}}{self.vector}"
