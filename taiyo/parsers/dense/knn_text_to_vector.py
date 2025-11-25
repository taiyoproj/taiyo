from typing import Optional, Literal
from pydantic import Field, computed_field
from taiyo.parsers.dense.base import DenseVectorSearchQueryParser


class KNNTextToVectorQueryParser(DenseVectorSearchQueryParser):
    """KNN Text-to-Vector Query Parser for Apache Solr Dense Vector Search.

    The knn_text_to_vector parser combines text encoding with k-nearest neighbors search,
    allowing you to search for similar documents using natural language queries instead of
    pre-computed vectors. It uses a language model to convert query text into a vector,
    then performs KNN search on that vector.

    Solr Reference:
        https://solr.apache.org/guide/solr/latest/query-guide/dense-vector-search.html

    Key Features:
        - Automatic text-to-vector encoding using language models
        - Eliminates need for pre-computing query vectors
        - Supports various embedding models (OpenAI, Hugging Face, etc.)
        - Combines semantic search with KNN efficiency
        - Configurable k (topK) for number of results

    How Text-to-Vector KNN Works:
        1. Query text is sent to the configured language model
        2. Model encodes text into a dense vector
        3. KNN search is performed using the generated vector
        4. Top k most similar documents are returned

    Model Requirements:
        The model must be loaded into Solr's text-to-vector model store:
        - Configure model in schema via REST API
        - Supported: OpenAI, Hugging Face, Cohere, etc.
        - Model must produce vectors matching field dimension

    Example Model Configuration (OpenAI):
        {
          "class": "dev.langchain4j.model.openai.OpenAiEmbeddingModel",
          "name": "openai-embeddings",
          "params": {
            "apiKey": "YOUR_API_KEY",
            "modelName": "text-embedding-ada-002"
          }
        }

    Schema Requirements:
        Field must be DenseVectorField:
        <fieldType name="knn_vector" class="solr.DenseVectorField"
                   vectorDimension="1536" similarityFunction="cosine"
                   knnAlgorithm="hnsw"/>
        <field name="vector" type="knn_vector" indexed="true" stored="true"/>

    Examples:
        >>> # Basic text-to-vector KNN search
        >>> parser = KNNTextToVectorQueryParser(
        ...     vector_field="content_vector",
        ...     text="machine learning algorithms",
        ...     model="openai-embeddings",
        ...     top_k=10
        ... )

        >>> # Semantic search with pre-filtering
        >>> parser = KNNTextToVectorQueryParser(
        ...     vector_field="article_embedding",
        ...     text="neural networks and deep learning",
        ...     model="huggingface-embedder",
        ...     top_k=20,
        ...     pre_filter=["category:AI", "published:[2020 TO *]"]
        ... )

        >>> # Multi-lingual semantic search
        >>> parser = KNNTextToVectorQueryParser(
        ...     vector_field="multilingual_vector",
        ...     text="apprentissage automatique",  # French
        ...     model="multilingual-embedder",
        ...     top_k=15
        ... )

        >>> # With tagged filtering
        >>> parser = KNNTextToVectorQueryParser(
        ...     vector_field="doc_vector",
        ...     text="search query optimization",
        ...     model="sentence-transformer",
        ...     top_k=50,
        ...     include_tags=["semantic_search"]
        ... )

    Args:
        text: Natural language query text to encode (required)
        model: Name of the model in text-to-vector model store (required)
        top_k: Number of nearest neighbors to return (default: 10)
        vector_field: Name of the DenseVectorField to search (inherited from base)
        pre_filter: Explicit pre-filter query strings (inherited from base)
        include_tags: Only use fq filters with these tags for implicit pre-filtering (inherited)
        exclude_tags: Exclude fq filters with these tags from implicit pre-filtering (inherited)

    Returns:
        Query results ranked by semantic similarity to the input text

    Note:
        The model name must reference an existing model loaded into the
        /schema/text-to-vector-model-store endpoint.

    See Also:
        - KNNQueryParser: For search with pre-computed vectors
        - VectorSimilarityQueryParser: For threshold-based vector search
        - Solr Text-to-Vector Models Guide: https://solr.apache.org/guide/solr/latest/query-guide/text-to-vector.html
    """

    text: str = Field(..., exclude=True, description="Text to search for.")
    model: Optional[str] = Field(
        default=None,
        exclude=True,
        description="Model to use for encoding text to vector (for knn_text_to_vector).",
    )
    top_k: Optional[int] = Field(
        default=10,
        alias="topK",
        exclude=True,
        description="How many k-nearest results to return.",
    )

    _def_type: Literal["knn_text_to_vector"] = "knn_text_to_vector"

    @computed_field(alias="q")
    def query(self) -> str:
        return f"{{!{self._def_type} model={self.model} topK={self.top_k} {self.vector_search_params}}}{self.text}"
