
# Terms Query Parser

## Overview

The `TermsQueryParser` efficiently matches documents where a specified field contains any of a provided list of terms. It is ideal for filtering by IDs, tags, categories, or batch lookups.

- **Supported Features:** Multi-value matching, configurable separator, multiple query methods, docValues support, filter appending.

**Solr Reference:** [Terms Query Parser](https://solr.apache.org/guide/solr/latest/query-guide/other-parsers.html#terms-query-parser)


## Basic Usage 

```python
TermsQueryParser(
    field: str,                # Field to search (required)
    terms: list[str],          # List of terms to match (required)
    query: str = "*:*",        # Main query (default: '*:*')
    separator: str = ",",      # Separator for joining terms (default: ',')
    method: Optional[str] = None,  # Query implementation method
    filters: Optional[list[str]] = None,  # Additional filters (appends terms filter)
)
```

### Query Methods

| Method                       | Description                                      | Use Case                        |
|------------------------------|--------------------------------------------------|---------------------------------|
| `termsFilter` (default)      | Auto-selects best implementation                 | General use                     |
| `booleanQuery`               | BooleanQuery                                     | Small term sets, large indices  |
| `automaton`                  | Automaton-based                                  | Specialized cases               |
| `docValuesTermsFilter`       | DocValues field support                          | DocValues-enabled fields        |
| `docValuesTermsFilterPerSegment` | Per-segment docValues filtering               | Large indices, docValues fields |
| `docValuesTermsFilterTopLevel`   | Top-level docValues filtering                 | Small indices, docValues fields |

## Examples


### Basic Tag Search with Document Model

```python
from taiyo import SolrDocument
from taiyo.parsers import TermsQueryParser


class Product(SolrDocument):
    product_id: str
    name: str
    category: str
    tags: list[str]
    price: float
    inStock: bool
    brand: str


parser = TermsQueryParser(field="tags", terms=["python", "java", "rust"])
results = client.search(parser, document_model=Product)
for doc in results.docs:
    print(doc.product_id, doc.name)
```

### Grouping Example

```python
parser = TermsQueryParser(field="category", terms=["books", "electronics"]).group(
    by="brand", limit=3
)

results = client.search(parser, document_model=Product)
if results.extra and "grouped" in results.extra:
    for brand, group_data in results.extra["grouped"].items():
        print(f"Brand: {brand}")
        for doc in group_data["docs"]:
            print("  ", doc.product_id, doc.name)
```

### Custom Query

```python
parser = TermsQueryParser(field="tags", terms=["python", "java"], query="inStock:true")
results = client.search(parser)
```

### Space Separator

```python
parser = TermsQueryParser(
    field="categoryId",
    terms=["8", "6", "7", "5309"],
    separator=" ",
    method="booleanQuery",
)
results = client.search(parser)
```

### ID Filtering

```python
parser = TermsQueryParser(field="product_id", terms=["P001", "P003", "P005"])
results = client.search(parser)
```

### DocValues Field

```python
parser = TermsQueryParser(
    field="brand", terms=["TechBooks", "DevPress"], method="docValuesTermsFilter"
)
results = client.search(parser)
```

### Appending Filters

```python
parser = TermsQueryParser(
    field="tags", terms=["python", "java"], filters=["category:books", "inStock:true"]
)
results = client.search(parser)
```

### Pagination, Sorting, and Field Selection

```python
parser = TermsQueryParser(
    field="category",
    terms=["books", "electronics"],
    rows=3,
    start=0,
    sort="price asc",
    field_list=["product_id", "name"],
)
results = client.search(parser)
```

## Performance Tips

- Use `termsFilter` for most cases.
- Use `docValuesTermsFilter` only on fields with docValues enabled.
- Use space separator for whitespace-trimmed terms.
- Filters are appended; terms filter is always included.


## See Also

- [StandardParser](sparse.md#standardparser)
- [DisMaxQueryParser](sparse.md#dismaxqueryparser)
