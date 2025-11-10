from typing import Optional, Literal
from pydantic import Field, computed_field
from taiyo.parsers.dense.base import DenseVectorSearchQueryParser


class KNNQueryParser(DenseVectorSearchQueryParser):
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
    @property
    def query(self) -> str:
        return f"{{!{self._def_type} topK={self.top_k} {self.vector_search_params}}}{self.vector}"
