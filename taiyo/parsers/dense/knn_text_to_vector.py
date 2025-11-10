from typing import Optional, Literal
from pydantic import Field, computed_field
from taiyo.parsers.dense.base import DenseVectorSearchQueryParser


class KNNTextToVectorQueryParser(DenseVectorSearchQueryParser):
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
    @property
    def query(self) -> str:
        return f"{{!{self._def_type} model={self.model} topK={self.top_k} {self.vector_search_params}}}{self.text}"
