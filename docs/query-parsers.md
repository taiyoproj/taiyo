bbox = BoundingBoxQueryParser(
geofilt = GeoFilterQueryParser(

# Query Parsers Overview

Taiyo provides several families of query parsers, each in its own module mirroring the codebase structure:

- [Sparse Parsers](parsers/sparse.md): Standard (lucene), DisMax, Extended DisMax
- [Dense Vector Parsers](parsers/dense.md): KNN, KNNTextToVector, VectorSimilarity
- [Spatial Parsers](parsers/spatial.md): BoundingBox, GeoFilter

All parsers are Pydantic models you instantiate and pass to `client.search()`. They serialize to Solr parameters via `.build()` (called internally by the client). Common parameters (paging, sorting, filters, field list, etc.) come from `CommonParamsMixin` and are supported across all parsers.

See each section for detailed usage and examples.

## Passing extra params

Any extra keyword args passed to `client.search()` are merged into the built parameters and sent to Solr.

```python
parser = StandardParser(query="test")
res = client.search(parser, facet="true", facet_field="category")
```
