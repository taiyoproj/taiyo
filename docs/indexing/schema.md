# Schema Management

Taiyo provides comprehensive support for managing Apache Solr schemas programmatically. You can define field types, fields, dynamic fields, and copy fields using Python objects, and apply them to your Solr collections.

## Overview

Solr schemas define how documents are indexed and stored. Taiyo supports:

- **Field Types**: Define how fields are analyzed and indexed
- **Fields**: Individual field definitions
- **Dynamic Fields**: Pattern-based field templates
- **Copy Fields**: Copy data from one field to another

## Field Types

Field types define how text is analyzed, tokenized, and indexed.

### Basic Field Type

```python
from taiyo import SolrClient
from taiyo.schema import SolrFieldType, SolrFieldClass

# Define a field type
field_type = SolrFieldType(
    name="text_general", solr_class=SolrFieldClass.TEXT, position_increment_gap=100
)

# Add to Solr
with SolrClient("http://localhost:8983/solr") as client:
    client.set_collection("my_collection")
    client.add_field_type(field_type)
```

### Built-in Field Classes

Solr provides many built-in field classes:

```python
from taiyo.schema import SolrFieldClass

# Text fields
SolrFieldClass.TEXT  # solr.TextField
SolrFieldClass.STRING  # solr.StrField

# Numeric fields
SolrFieldClass.INT  # solr.IntPointField
SolrFieldClass.LONG  # solr.LongPointField
SolrFieldClass.FLOAT  # solr.FloatPointField
SolrFieldClass.DOUBLE  # solr.DoublePointField

# Date/Time
SolrFieldClass.DATE  # solr.DatePointField

# Boolean
SolrFieldClass.BOOLEAN  # solr.BoolField

# Binary
SolrFieldClass.BINARY  # solr.BinaryField

# Vector search
SolrFieldClass.DENSE_VECTOR  # solr.DenseVectorField
```

### Dense Vector Field Type

For vector similarity search:

```python
from taiyo.schema import SolrFieldType, SolrFieldClass

vector_field_type = SolrFieldType(
    name="embedding_vector",
    solr_class=SolrFieldClass.DENSE_VECTOR,
    vectorDimension=384,  # Vector size
    similarityFunction="cosine",  # cosine, dot_product, euclidean
    knnAlgorithm="hnsw",  # HNSW algorithm
)

client.add_field_type(vector_field_type)
```

### Text Field Type with Analysis

```python
from taiyo.schema import SolrFieldType, SolrFieldClass
from taiyo.schema.field_type import Analyzer, Tokenizer, Filter

# Define text field with custom analysis
text_type = SolrFieldType(
    name="text_en",
    solr_class=SolrFieldClass.TEXT,
    position_increment_gap=100,
    analyzer=Analyzer(
        tokenizer=Tokenizer(name="standard"),
        filters=[
            Filter(name="lowercase"),
            Filter(name="stop", words="lang/stopwords_en.txt"),
            Filter(name="englishPossessive"),
            Filter(name="keywordMarker", protected="protwords.txt"),
            Filter(name="porterStem"),
        ],
    ),
)

client.add_field_type(text_type)
```

## Fields

Fields define individual document attributes in your schema.

### Basic Field

```python
from taiyo.schema import SolrField

# Required text field
title_field = SolrField(
    name="title", type="text_general", indexed=True, stored=True, required=True
)

client.add_field(title_field)
```

### Common Field Patterns

```python
# ID field (string, indexed, stored, required)
id_field = SolrField(name="id", type="string", indexed=True, stored=True, required=True)

# Full-text search field
content_field = SolrField(
    name="content", type="text_general", indexed=True, stored=True, multi_valued=False
)

# Numeric field
price_field = SolrField(
    name="price",
    type="pfloat",
    indexed=True,
    stored=True,
    doc_values=True,  # Enable for sorting/faceting
)

# Date field
published_date = SolrField(
    name="published_date", type="pdate", indexed=True, stored=True, doc_values=True
)

# Multi-valued field (array)
tags_field = SolrField(
    name="tags", type="string", indexed=True, stored=True, multi_valued=True
)

# Vector embedding field
embedding_field = SolrField(
    name="embedding",
    type="embedding_vector",  # Uses field type defined earlier
    indexed=True,
    stored=False,  # Don't store vectors
)
```

### Field Options

```python
field = SolrField(
    name="custom_field",
    type="text_general",
    # Indexing
    indexed=True,  # Enable indexing for search
    stored=True,  # Store original value
    doc_values=True,  # Enable for sorting/faceting/grouping
    # Validation
    required=False,  # Field is optional
    # Multi-value
    multi_valued=False,  # Single value (set True for arrays)
    # Other
    omit_norms=False,  # Omit length normalization
    omit_term_freq_and_positions=False,  # Omit term frequency
    omit_positions=False,  # Omit positions
    # Default value
    default="default_value",
)
```

## Dynamic Fields

Dynamic fields are patterns that match multiple field names.

### Basic Dynamic Field

```python
from taiyo.schema import SolrDynamicField

# All fields ending in _txt use text_general
dynamic_field = SolrDynamicField(
    name="*_txt", type="text_general", indexed=True, stored=True
)

client.add_dynamic_field(dynamic_field)
```

### Common Dynamic Field Patterns

```python
# Language-specific text fields
SolrDynamicField(name="*_en", type="text_en", indexed=True, stored=True)
SolrDynamicField(name="*_es", type="text_es", indexed=True, stored=True)
SolrDynamicField(name="*_fr", type="text_fr", indexed=True, stored=True)

# String fields for exact matching
SolrDynamicField(name="*_s", type="string", indexed=True, stored=True)
SolrDynamicField(
    name="*_ss", type="string", indexed=True, stored=True, multi_valued=True
)

# Integer fields
SolrDynamicField(name="*_i", type="pint", indexed=True, stored=True)
SolrDynamicField(name="*_is", type="pint", indexed=True, stored=True, multi_valued=True)

# Long fields
SolrDynamicField(name="*_l", type="plong", indexed=True, stored=True)
SolrDynamicField(
    name="*_ls", type="plong", indexed=True, stored=True, multi_valued=True
)

# Float fields
SolrDynamicField(name="*_f", type="pfloat", indexed=True, stored=True)
SolrDynamicField(
    name="*_fs", type="pfloat", indexed=True, stored=True, multi_valued=True
)

# Double fields
SolrDynamicField(name="*_d", type="pdouble", indexed=True, stored=True)
SolrDynamicField(
    name="*_ds", type="pdouble", indexed=True, stored=True, multi_valued=True
)

# Boolean fields
SolrDynamicField(name="*_b", type="boolean", indexed=True, stored=True)
```

## Copy Fields

Copy fields duplicate data from one field to another, useful for catch-all search fields.

### Basic Copy Field

```python
from taiyo.schema import CopyField

# Copy title to catch-all search field
copy_field = CopyField(source="title", dest="text")

client.add_copy_field(copy_field)
```

### Multiple Sources

```python
# Copy multiple fields to a single search field
copy_fields = [
    CopyField(source="title", dest="text"),
    CopyField(source="description", dest="text"),
    CopyField(source="content", dest="text"),
    CopyField(source="author", dest="text"),
]

for cf in copy_fields:
    client.add_copy_field(cf)
```

### With Character Limit

```python
# Copy only first 500 characters
copy_field = CopyField(source="content", dest="summary", max_chars=500)
```

### Wildcard Sources

```python
# Copy all *_txt fields to text
copy_field = CopyField(source="*_txt", dest="text")
```

## Schema Example

Setting up a schema for a book catalog:

```python
from taiyo import SolrClient
from taiyo.schema import SolrField, CopyField

with SolrClient("http://localhost:8983/solr") as client:
    # Create collection
    client.create_collection("books", num_shards=1, replication_factor=1)
    client.set_collection("books")

    # Define fields
    fields = [
        SolrField(name="title", type="text_general", stored=True, indexed=True),
        SolrField(
            name="author", type="string", stored=True, indexed=True, doc_values=True
        ),
        SolrField(name="year", type="pint", stored=True, indexed=True, doc_values=True),
        SolrField(
            name="genre", type="string", stored=True, indexed=True, doc_values=True
        ),
        SolrField(name="description", type="text_general", stored=True, indexed=True),
        SolrField(
            name="text",
            type="text_general",
            stored=False,
            indexed=True,
            multi_valued=True,
        ),
    ]

    for field in fields:
        client.add_field(field)

    # Copy fields for unified search
    copy_fields = [
        CopyField(source="title", dest="text"),
        CopyField(source="author", dest="text"),
        CopyField(source="description", dest="text"),
    ]

    for cf in copy_fields:
        client.add_copy_field(cf)
```

## Schema for Vector Search

Setting up a schema for semantic search with embeddings:

```python
from taiyo import SolrClient
from taiyo.schema import SolrFieldType, SolrField, SolrFieldClass

with SolrClient("http://localhost:8983/solr") as client:
    client.set_collection("semantic_search")

    # Define vector field type
    vector_type = SolrFieldType(
        name="dense_vector",
        solr_class=SolrFieldClass.DENSE_VECTOR,
        vectorDimension=384,  # e.g., all-MiniLM-L6-v2
        similarityFunction="cosine",
        knnAlgorithm="hnsw",
    )
    client.add_field_type(vector_type)

    # Add fields
    fields = [
        # Document content
        SolrField(name="title", type="text_general", indexed=True, stored=True),
        SolrField(name="content", type="text_general", indexed=True, stored=True),
        # Embedding vector
        SolrField(name="embedding", type="dense_vector", indexed=True, stored=False),
        # Metadata
        SolrField(name="category", type="string", indexed=True, stored=True),
        SolrField(name="created_at", type="pdate", indexed=True, stored=True),
    ]

    for field in fields:
        client.add_field(field)
```

## Working with Dictionaries

You can also define schemas using dictionaries:

```python
# Field type as dict
field_type_dict = {
    "name": "text_custom",
    "class": "solr.TextField",
    "positionIncrementGap": "100",
}
client.add_field_type(field_type_dict)

# Field as dict
field_dict = {
    "name": "custom_field",
    "type": "text_general",
    "indexed": True,
    "stored": True,
}
client.add_field(field_dict)
```

## Best Practices

### Define Schema Before Indexing

```python
client.add_field(SolrField(name="title", type="text_general", ...))
client.add(documents)
```

Defining schema before indexing prevents suboptimal auto-generated field types.

### Use DocValues for Faceting/Sorting

```python
SolrField(name="category", type="string", indexed=True, stored=True, doc_values=True)
```

Enable `doc_values` for fields used in facets, sorting, or grouping.

### Choose Appropriate Field Types

Use specific field types instead of generic string types:

```python
SolrField(name="price", type="pfloat")
SolrField(name="date", type="pdate")
```

Numeric types enable proper sorting and range queries. Date types enable date math operations.

### Use Dynamic Fields Wisely

Define clear naming conventions:

```python
*_txt -> text fields
*_s   -> string fields
*_i   -> integer fields
```

Avoid overly broad patterns like `*` that match everything.

### Don't Store What You Don't Need

```python
# Store original values only when needed
SolrField(
    name="text", type="text_general", indexed=True, stored=False
)  # No need to store analyzed text
SolrField(
    name="title", type="text_general", indexed=True, stored=True
)  # Store for display
```

## Troubleshooting

### Field Already Exists

```python
try:
    client.add_field(field)
except Exception as e:
    if "already exists" in str(e).lower():
        print("Field already exists, skipping")
    else:
        raise
```

### Collection Not Set

```python
# Always set collection before schema operations
client.set_collection("my_collection")
client.add_field(field)
```

### Field Type Not Found

```python
# Add field type before fields that use it
field_type = SolrFieldType(name="custom_text", ...)
client.add_field_type(field_type)

# Now add fields using this type
field = SolrField(name="content", type="custom_text", ...)
client.add_field(field)
```

## Next Steps

- Learn about [Data Models](../clients/models.md) to use your schema with type-safe documents
- Explore [Query Parsers](../parsers/overview.md) to search your indexed data
- See [Clients](../clients/overview.md) for indexing documents with your schema
