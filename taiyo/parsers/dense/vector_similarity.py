from typing import Optional, Literal
from pydantic import Field, computed_field

from taiyo.parsers.dense.base import DenseVectorSearchQueryParser


class VectorSimilarityQueryParser(DenseVectorSearchQueryParser):
    """
    Query parser for dense vector (KNN) search in Solr.
    Supports knn, knn_text_to_vector, and vectorSimilarity query parsers.
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
    @property
    def query(self) -> str:
        return f"{{!{self._def_type} minTraverse={self.min_traverse} minReturn={self.min_return} {self.vector_search_params}}}{self.vector}"
