# Dense Vector Query Parsers

Dense vector parsers are used for KNN and vector similarity search in Solr. All dense parsers extend `DenseVectorSearchParamsMixin` and require the vector field name (`f`).

## KNN

```python
from taiyo import KNNQueryParser

parser = KNNQueryParser(
    field="vector",            # f
    vector=[0.1, 0.2, 0.3],
    top_k=5,                    # topK
    pre_filter=["inStock:true"],
    include_tags=["tag1"],
    exclude_tags=["tag2"],
    debug="INFO",
)
res = client.search(parser)
```

## KNN text-to-vector

```python
from taiyo import KNNTextToVectorQueryParser

parser = KNNTextToVectorQueryParser(
    field="vector",
    text="wireless mouse",
    model="emb_model",
    top_k=5,
)
res = client.search(parser)
```

## vectorSimilarity

```python
from taiyo import VectorSimilarityParser

parser = VectorSimilarityParser(
    field="vector",
    vector=[0.1, 2.0, 3.9],
    min_traverse=0.2,
    min_return=0.7,
)
res = client.search(parser)
```
