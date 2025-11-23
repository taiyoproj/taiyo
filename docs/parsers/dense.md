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

parser = KNNQueryParser(
    field="content_vector",
    query_vector=query_vector,
    top_k=10
)

results = client.search(parser)
```

### Parameters

```python
parser = KNNQueryParser(
    field="embedding",           # Dense vector field name
    query_vector=[...],         # Query embedding vector
    top_k=10,                   # Number of nearest neighbors
    
    # Common parameters
    rows=10,
    start=0,
    fields=["id", "title", "content"],
    filter_query=["status:active"]
)
```

### Complete Example

```python
from taiyo.parsers import KNNQueryParser
from your_embedding_model import embed_text

# Generate query embedding
query_text = "machine learning algorithms"
query_vector = embed_text(query_text)

# Search for similar documents
parser = (
    KNNQueryParser(
        field="content_vector",
        query_vector=query_vector,
        top_k=20,
        rows=10,
        field_list=["id", "title", "author", "abstract"],
        filters=[
            "category:technology",
            "published_date:[NOW-1YEAR TO NOW]"
        ]
    )
)

results = client.search(parser)

for doc in results.docs:
    print(f"{doc.title} by {doc.author}")
    print(f"Score: {doc.score}")
```

### Filtering Before Search

Apply filters to limit the candidate set:

```python
parser = KNNQueryParser(
    field="embedding",
    query_vector=query_vector,
    top_k=10,
    filter_query=[
        "category:science",           # Only science articles
        "language:en",                # English only
        "quality_score:[7 TO *]"      # High quality only
    ]
)
```

### Hybrid Search: Vector + Keyword

Combine vector search with keyword search:

```python
from taiyo.parsers import KNNQueryParser, ExtendedDisMaxQueryParser

# Vector search component
knn_parser = KNNQueryParser(
    field="content_vector",
    query_vector=query_vector,
    top_k=20
)

# Keyword search component
keyword_parser = ExtendedDisMaxQueryParser(
    query="machine learning",
    query_fields={"title": 3.0, "content": 1.0}
)

# Combine using Solr's query boosting
results = client.search(
    knn_parser,
    bq=f"{{!edismax qf='title^3 content' v='machine learning'}}"
)
```

## KNNTextToVectorQueryParser

The `KNNTextToVectorQueryParser` converts text queries to vectors using a configured encoder within Solr, then performs KNN search.

**Solr Documentation**: [Text-to-Vector with KNN](https://solr.apache.org/guide/solr/latest/query-guide/dense-vector-search.html)

### Basic Usage

```python
from taiyo.parsers import KNNTextToVectorQueryParser

parser = KNNTextToVectorQueryParser(
    field="content_vector",
    query_text="machine learning algorithms",
    top_k=10
)

results = client.search(parser)
```

### Parameters

```python
parser = KNNTextToVectorQueryParser(
    field="embedding",                    # Dense vector field name
    query_text="search query",           # Text query (will be encoded)
    top_k=10,                            # Number of nearest neighbors
    encoder="my-bert-encoder",           # Optional: specific encoder name
    
    # Common parameters
    rows=10,
    start=0,
    fields=["id", "title"],
    filter_query=["status:active"]
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

### Complete Example

```python
from taiyo.parsers import KNNTextToVectorQueryParser

# No need to generate embeddings yourself!
parser = (
    KNNTextToVectorQueryParser(
        field="content_vector",
        query_text="What are the latest advances in neural networks?",
        top_k=20,
        encoder="bert-base",  # Use configured encoder
        rows=10,
        field_list=["id", "title", "abstract", "published_date"],
        sort="published_date desc",
        filters=[
            "category:ai",
            "published_date:[NOW-2YEARS TO NOW]"
        ]
    )
)

results = client.search(parser)

print(f"Found {results.num_found} similar documents")
for doc in results.docs:
    print(f"\n{doc.title}")
    print(f"Published: {doc.published_date}")
    print(f"Similarity: {doc.score:.4f}")
```

### Advantages Over KNNQueryParser

```python
# KNNQueryParser: You handle encoding
from your_model import encode
query_vector = encode("machine learning")
parser = KNNQueryParser(field="embedding", query_vector=query_vector, top_k=10)

# KNNTextToVectorQueryParser: Solr handles encoding
parser = KNNTextToVectorQueryParser(
    field="embedding",
    query_text="machine learning",  # Plain text!
    top_k=10
)
```

**Benefits:**
- No need to deploy your own encoding service
- Consistent encoding between indexing and querying
- Reduced latency (encoding happens server-side)
- Simpler client code

## VectorSimilarityQueryParser

The `VectorSimilarityQueryParser` performs similarity search with more control over scoring and filtering.

**Solr Documentation**: [Vector Similarity Function](https://solr.apache.org/guide/solr/latest/query-guide/dense-vector-search.html)

### Basic Usage

```python
from taiyo.parsers import VectorSimilarityQueryParser

parser = VectorSimilarityQueryParser(
    field="content_vector",
    query_vector=query_vector,
    similarity_function="cosine"
)

results = client.search(parser)
```

### Parameters

```python
parser = VectorSimilarityQueryParser(
    field="embedding",                # Dense vector field name
    query_vector=[...],              # Query embedding vector
    similarity_function="cosine",    # cosine, euclidean, dot_product, manhattan
    min_score=0.7,                   # Optional: minimum similarity threshold
    
    # Common parameters
    rows=10,
    start=0,
    fields=["id", "title"],
    filter_query=["status:active"]
)
```

### Similarity Functions

```python
# Cosine similarity (most common, range -1 to 1)
parser = VectorSimilarityQueryParser(
    field="embedding",
    query_vector=query_vector,
    similarity_function="cosine"
)

# Euclidean distance (L2 norm, lower = more similar)
parser = VectorSimilarityQueryParser(
    field="embedding",
    query_vector=query_vector,
    similarity_function="euclidean"
)

# Dot product (for normalized vectors)
parser = VectorSimilarityQueryParser(
    field="embedding",
    query_vector=query_vector,
    similarity_function="dot_product"
)

# Manhattan distance (L1 norm)
parser = VectorSimilarityQueryParser(
    field="embedding",
    query_vector=query_vector,
    similarity_function="manhattan"
)
```

### Minimum Score Threshold

Filter out low-similarity results:

```python
parser = VectorSimilarityQueryParser(
    field="content_vector",
    query_vector=query_vector,
    similarity_function="cosine",
    min_score=0.75  # Only return docs with similarity >= 0.75
)
```

### Complete Example

```python
from taiyo.parsers import VectorSimilarityQueryParser
from your_model import embed_text

query_text = "deep learning for computer vision"
query_vector = embed_text(query_text)

parser = (
    VectorSimilarityQueryParser(
        field="abstract_vector",
        query_vector=query_vector,
        similarity_function="cosine",
        min_score=0.7,  # High similarity threshold
        rows=20,
        field_list=["id", "title", "authors", "abstract", "citations"],
        sort="score desc, citations desc",  # Sort by similarity, then citations
        filters=[
            "field:computer_science",
            "year:[2020 TO *]",
            "citations:[10 TO *]"
        ]
    )
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
    similarity_function="cosine"
)

# Add vector field
embedding_field = Field(
    name="content_vector",
    type="knn_vector_768",
    indexed=True,
    stored=True
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
        "content_vector": embed_text("Machine learning is a subset of artificial intelligence...")
    },
    {
        "id": "doc2",
        "title": "Deep Learning Fundamentals",
        "content": "Deep learning uses neural networks with multiple layers...",
        "content_vector": embed_text("Deep learning uses neural networks with multiple layers...")
    }
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
    name="knn_vector",
    class_name="solr.DenseVectorField",
    vector_dimension=768
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
parser = KNNQueryParser(
    field="content_vector",
    query_vector=query_vector,
    top_k=10
)
```

### Optimize Top-K

```python
# Start with reasonable top_k
parser = KNNQueryParser(
    field="embedding",
    query_vector=query_vector,
    top_k=100  # Get more candidates
)

# Then filter and re-rank
reranked_parser = parser.model_copy(
    update={
        "rows": 10,  # Return only 10
        "filters": ["category:relevant"],
        "sort": "score desc"
    }
)

results = client.search(reranked_parser)
```

### Combine with Filters

```python
# Apply filters to reduce search space
parser = KNNQueryParser(
    field="content_vector",
    query_vector=query_vector,
    top_k=20,
    filter_query=[
        "status:published",      # Pre-filter
        "language:en",           # Reduce candidates
        "quality_score:[7 TO *]" # Only high quality
    ]
)
```

### Hybrid Search Pattern

```python
def hybrid_search(query_text: str, top_k: int = 20):
    """Combine vector and keyword search."""
    # Generate embedding
    query_vector = embed_text(query_text)
    
    # Vector search (semantic)
    vector_parser = KNNQueryParser(
        field="content_vector",
        query_vector=query_vector,
        top_k=top_k
    )
    
    # Keyword search (lexical)
    keyword_boost = f"{{!edismax qf='title^3 content' v='{query_text}'}}"
    
    # Combine by adding boost query at request time
    return client.search(
        vector_parser,
        bq=[keyword_boost],
        rows=10
    )
```

### Monitor Performance

```python
# Track query times
results = client.search(parser)
print(f"Query time: {results.query_time}ms")

# Measure recall
# (requires ground truth data)

# Tune based on metrics
if results.query_time > 100:
    # Reduce top_k or add more filters
    parser = KNNQueryParser(
        field="embedding",
        query_vector=query_vector,
        top_k=50,  # Reduced from 100
        filter_query=["category:relevant"]  # Added filter
    )
```

## Common Patterns

### Multi-Field Vector Search

```python
# Search across different embedding fields
from taiyo.parsers import KNNQueryParser

# Title embeddings (smaller, focused)
title_query = embed_text(query_text, model="title-encoder")
title_parser = KNNQueryParser(
    field="title_vector",
    query_vector=title_query,
    top_k=10
)

# Content embeddings (larger, comprehensive)
content_query = embed_text(query_text, model="content-encoder")
content_parser = KNNQueryParser(
    field="content_vector",
    query_vector=content_query,
    top_k=10
)

# Boost title matches
boosted_results = client.search(
    content_parser,
    bq=f"{{!knn f=title_vector topK=10}}[{','.join(map(str, title_query))}]^2"
)
```

### Faceted Vector Search

```python
parser = (
    KNNQueryParser(
        field="content_vector",
        query_vector=query_vector,
        top_k=100,
        rows=20
    )
    .facet(
        fields=["category", "author", "year"],
        mincount=1
    )
)

results = client.search(parser)

# Show facets
for category, count in results.facet_counts["facet_fields"]["category"]:
    print(f"{category}: {count}")
```

### Re-ranking Results

```python
# Initial vector search
parser = KNNQueryParser(
    field="content_vector",
    query_vector=query_vector,
    top_k=100  # Get many candidates
)

# Re-rank using additional signals
reranked = parser.model_copy(
    update={
        "rows": 20,
        "boost_functons": [
            "recip(ms(NOW,published_date),3.16e-11,1,1)",  # Recency
            "log(views)",  # Popularity
            "product(rating,10)"  # Quality
        ],
        "sort": "score desc"
    }
)

results = client.search(reranked)
```

## Next Steps

- Learn about [Sparse Parsers](sparse.md) for keyword search
- Explore [Spatial Parsers](spatial.md) for geographic queries
- Add [Faceting](../faceting.md) for aggregations
- Use [Highlighting](../highlighting.md) for result snippets
