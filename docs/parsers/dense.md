# Dense Vector Search Parsers

Dense vector search parsers enable semantic similarity search using vector embeddings. These parsers work with dense vector fields in your Solr schema.

## KNNQueryParser

The `KNNQueryParser` performs k-nearest neighbor search using pre-computed vector embeddings.

**Solr Documentation**: [Dense Vector Search](https://solr.apache.org/guide/solr/latest/query-guide/dense-vector-search.html)

### Basic Usage

```python
from taiyo.parsers import KNNQueryParser

# Your query vector (from your embedding model)
query_vector = [0.23, -0.45, 0.67, ...]

parser = KNNQueryParser(field="content_vector", vector=query_vector, top_k=10)

results = client.search(parser)
```

### Parameters

```python
parser = KNNQueryParser(
    field="embedding",  # Dense vector field name
    vector=[...],  # Query embedding vector
    top_k=10,  # Number of nearest neighbors
    # Common parameters
    rows=10,
    start=0,
    field_list=["id", "title", "content"],
    filters=["status:active"],
)
```

### Example

```python
from taiyo.parsers import KNNQueryParser
from your_embedding_model import embed_text

# Generate query embedding
query_text = "machine learning algorithms"
query_vector = embed_text(query_text)

# Search for similar documents
parser = KNNQueryParser(
    field="content_vector",
    vector=query_vector,
    top_k=20,
    rows=10,
    field_list=["id", "title", "author", "abstract"],
    filters=["category:technology", "published_date:[NOW-1YEAR TO NOW]"],
)

results = client.search(parser)

for doc in results.docs:
    print(f"{doc.title} by {doc.author}")
    print(f"Score: {doc.score}")
```

### Pre-Filtering

Pre-filtering narrows the candidate set before KNN search for better performance and relevance.

#### Implicit Pre-Filtering

By default, all filter queries are automatically applied as pre-filters:

```python
parser = KNNQueryParser(
    field="embedding",
    vector=query_vector,
    top_k=10,
    filters=[
        "category:science",  # Only science articles
        "language:en",  # English only
        "quality_score:[7 TO *]",  # High quality only
    ],
)
# All filters automatically pre-filter the KNN search
```

#### Explicit Pre-Filtering

Use `pre_filter` to explicitly specify pre-filter conditions:

```python
parser = KNNQueryParser(
    field="embedding",
    vector=query_vector,
    top_k=10,
    pre_filter=["category:science", "status:published"],
    filters=["language:en"],  # This becomes a post-filter
)
```

#### Tagged Filtering

Control which filters are used for pre-filtering with tags:

```python
parser = KNNQueryParser(
    field="embedding",
    vector=query_vector,
    top_k=10,
    filters=[
        "{!tag=prefilter}category:science",
        "{!tag=prefilter}status:published",
        "language:en",  # Not tagged
    ],
    include_tags=["prefilter"],  # Only use filters with this tag for pre-filtering
)

# Or exclude specific tags
parser = KNNQueryParser(
    field="embedding",
    vector=query_vector,
    top_k=10,
    filters=["{!tag=postfilter}facet_field:value", "category:science"],
    exclude_tags=["postfilter"],  # Exclude this from pre-filtering
)
```

### Query Serialization with .build()

KNN parsers serialize into Solr's local params format compatible with Apache Solr's official documentation:

```python
from taiyo.parsers import KNNQueryParser

parser = KNNQueryParser(
    field="embedding",
    vector=[0.1, 0.2, 0.3, 0.4, 0.5],
    top_k=10,
    pre_filter=["category:electronics"],
    filters=["status:active"],
)

# Build query parameters as dictionary
params = parser.build()
# {
#   'q': '{!knn f=embedding topK=10 preFilter=category:electronics}[0.1,0.2,0.3,0.4,0.5]',
#   'fq': ['status:active'],
#   'rows': 10
# }
```

The generated query `q` parameter matches Solr's local params syntax: [Apache Solr's Dense Vector Search Guide](https://solr.apache.org/guide/solr/latest/query-guide/dense-vector-search.html).

#### Compatibility with Other Clients

The dictionary output can be used with any HTTP client:

```python
import httpx

parser = KNNQueryParser(field="product_vector", vector=[0.5, 0.3, 0.8, 0.2], top_k=20)

params = parser.build()

# Use with httpx or any HTTP library
response = httpx.get("http://localhost:8983/solr/products/select", params=params)
```

## KNNTextToVectorQueryParser

The `KNNTextToVectorQueryParser` converts text queries to vectors using a configured encoder within Solr, then performs KNN search.

**Solr Documentation**: [Text-to-Vector with KNN](https://solr.apache.org/guide/solr/latest/query-guide/dense-vector-search.html)

### Basic Usage

```python
from taiyo.parsers import KNNTextToVectorQueryParser

parser = KNNTextToVectorQueryParser(
    field="content_vector",
    text="machine learning algorithms",
    model="my-encoder-model",
    top_k=10,
)

results = client.search(parser)
```

### Parameters

```python
parser = KNNTextToVectorQueryParser(
    field="embedding",  # Dense vector field name
    text="search query",  # Text query (will be encoded)
    model="my-bert-encoder",  # Model name in text-to-vector store (required)
    top_k=10,  # Number of nearest neighbors
    # Common parameters
    rows=10,
    start=0,
    field_list=["id", "title"],
    filters=["status:active"],
)
```

### Encoder Configuration

Your Solr schema needs an encoder configured:

```xml
<fieldType name="knn_vector" class="solr.DenseVectorField" vectorDimension="768">
  <encoder class="org.apache.solr.ltr.model.BertEncoder">
    <str name="modelPath">models/bert-base-uncased</str>
  </encoder>
</fieldType>

<field name="content_vector" type="knn_vector" indexed="true" stored="true"/>
```

### Example

```python
from taiyo.parsers import KNNTextToVectorQueryParser

# No need to generate embeddings yourself!
parser = KNNTextToVectorQueryParser(
    field="content_vector",
    text="What are the latest advances in neural networks?",
    model="bert-base",  # Use configured model
    rows=10,
    field_list=["id", "title", "abstract", "published_date"],
    sort="published_date desc",
    filters=["category:ai", "published_date:[NOW-2YEARS TO NOW]"],
)

results = client.search(parser)

print(f"Found {results.num_found} similar documents")
for doc in results.docs:
    print(f"\n{doc.title}")
    print(f"Published: {doc.published_date}")
    print(f"Similarity: {doc.score:.4f}")
```


## VectorSimilarityQueryParser

The `VectorSimilarityQueryParser` performs similarity search with more control over scoring and filtering.

**Solr Documentation**: [Vector Similarity Function](https://solr.apache.org/guide/solr/latest/query-guide/dense-vector-search.html)

### Basic Usage

```python
from taiyo.parsers import VectorSimilarityQueryParser

parser = VectorSimilarityQueryParser(
    field="content_vector", vector=query_vector, min_return=0.7
)

results = client.search(parser)
```

### Parameters

```python
parser = VectorSimilarityQueryParser(
    field="embedding",  # Dense vector field name
    vector=[...],  # Query embedding vector
    min_return=0.7,  # Minimum similarity threshold for returned docs
    min_traverse=0.5,  # Optional: minimum similarity to continue traversal
    # Common parameters
    rows=10,
    start=0,
    field_list=["id", "title"],
    filters=["status:active"],
)
```

### Minimum Similarity Threshold

Filter out low-similarity results using `min_return`:

```python
parser = VectorSimilarityQueryParser(
    field="content_vector",
    vector=query_vector,
    min_return=0.75,  # Only return docs with similarity >= 0.75
    min_traverse=0.6,  # Continue graph traversal for similarity >= 0.6
)
```

### Example

```python
from taiyo.parsers import VectorSimilarityQueryParser
from your_model import embed_text

query_text = "deep learning for computer vision"
query_vector = embed_text(query_text)

parser = VectorSimilarityQueryParser(
    field="abstract_vector",
    vector=query_vector,
    min_return=0.7,  # High similarity threshold
    min_traverse=0.5,  # Traverse threshold
    rows=20,
    field_list=["id", "title", "authors", "abstract", "citations"],
    sort="score desc, citations desc",  # Sort by similarity, then citations
    filters=["field:computer_science", "year:[2020 TO *]", "citations:[10 TO *]"],
)

results = client.search(parser)

print(f"Found {results.num_found} highly similar papers")
for doc in results.docs:
    print(f"\n{doc.title}")
    print(f"Authors: {', '.join(doc.authors)}")
    print(f"Similarity: {doc.score:.3f}")
    print(f"Citations: {doc.citations}")
```

## Parser Comparison

| Feature | KNN | KNN Text-to-Vector | Vector Similarity |
|---------|-----|-------------------|-------------------|
| **Input** | Vector | Text | Vector |
| **Encoding** | Client-side | Server-side | Client-side |
| **Top-K** | Yes | Yes | Yes (via rows) |
| **Similarity Function** | Fixed | Fixed | Configurable |
| **Min Score** | No | No | Yes |
| **Best for** | External encoders | Simpler setup | Fine-tuned control |

## Schema Setup

### Vector Field Definition

```python
from taiyo.schema import FieldType, Field

# Define vector field type
vector_type = FieldType(
    name="knn_vector_768",
    class_name="solr.DenseVectorField",
    vector_dimension=768,
    similarity_function="cosine",  # cosine, dot_product, or euclidean
)

# Add vector field
embedding_field = Field(
    name="content_vector", type="knn_vector_768", indexed=True, stored=True
)

# Update schema
client.schema.add_field_type(vector_type)
client.schema.add_field(embedding_field)
```

### Indexing Documents with Vectors

```python
from your_model import embed_text

documents = [
    {
        "id": "doc1",
        "title": "Introduction to Machine Learning",
        "content": "Machine learning is a subset of artificial intelligence...",
        "content_vector": embed_text(
            "Machine learning is a subset of artificial intelligence..."
        ),
    },
    {
        "id": "doc2",
        "title": "Deep Learning Fundamentals",
        "content": "Deep learning uses neural networks with multiple layers...",
        "content_vector": embed_text(
            "Deep learning uses neural networks with multiple layers..."
        ),
    },
]

client.index(documents)
```

## Best Practices

### Choose Appropriate Vector Dimensions

Common embedding dimensions:
- BERT-base: 768
- BERT-large: 1024
- Sentence-BERT: 384 or 768
- OpenAI embeddings: 1536
- word2vec: 100-300

Match schema configuration to your embedding model:

```python
vector_type = FieldType(
    name="knn_vector", class_name="solr.DenseVectorField", vector_dimension=768
)
```

### Normalize Vectors

```python
import numpy as np


def normalize_vector(vector):
    """Normalize vector to unit length for cosine similarity."""
    norm = np.linalg.norm(vector)
    return (vector / norm).tolist()


# Use normalized vectors
query_vector = normalize_vector(raw_embedding)
parser = KNNQueryParser(field="content_vector", vector=query_vector, top_k=10)
```

### Optimize Top-K

```python
# Start with reasonable top_k
parser = KNNQueryParser(
    field="embedding",
    vector=query_vector,
    top_k=100,  # Get more candidates
)

# Then filter and re-rank
reranked_parser = parser.model_copy(
    update={
        "rows": 10,  # Return only 10
        "filters": ["category:relevant"],
        "sort": "score desc",
    }
)

results = client.search(reranked_parser)
```

## Next Steps

- Learn about [Sparse Parsers](sparse.md) for keyword search
- Explore [Spatial Parsers](spatial.md) for geographic queries
- Add [Faceting](../controlling-results/faceting.md) for aggregations
- Use [Highlighting](../controlling-results/highlighting.md) for result snippets
