# Mixins and Configs

Taiyo exposes common Solr query features as Pydantic models you can compose into parsers. This yields validated, discoverable parameters that serialize into flat Solr params.

## CommonParamsMixin

Available on all parsers via `BaseQueryParser`.

Selected fields:
- `sort: str = 'score desc'`
- `start: int = 0`
- `rows: int = 10`
- `filters (fq): list[str] | None`
- `field_list (fl): str | list[str] = '*'`
- `debug: str | list[str] | None`
- `time_allowed (timeAllowed): int | None`
- `omit_header (omitHeader): bool = False`
- Many more: see `taiyo/params/mixins/common.py`

Usage:

```python
from taiyo import StandardParser
parser = StandardParser(query="foo", rows=50, filters=["category:books"])  # sow, q.op, etc also available
params = parser.build()
```

## DenseVectorSearchParamsMixin

Shared by dense vector parsers. Keys serialize into an inline "local params" string used inside `q`.

Fields:
- `field (f): str` — required vector field
- `pre_filter (preFilter): list[str] | None`
- `include_tags (includeTags): list[str] | None`
- `exclude_tags (excludeTags): list[str] | None`

Example inline params:

```text
f=vector preFilter=inStock:true includeTags=tag1 excludeTags=tag2
```

## SpatialSearchParamsMixin

For spatial queries (bbox/geofilt).

Fields:
- `spatial_field (sfield): str` — required
- `center_point (pt): list[float]` — required, serialized as "lat,lon"
- `radial_distance (d): float` — required
- `score: str | None`
- `filter: bool | None`

```python
from taiyo import BoundingBoxQueryParser
parser = BoundingBoxQueryParser(
    spatial_field="store", center_point=[45.15, -93.85], radial_distance=5,
)
params = parser.build()  # {'sfield': 'store', 'pt': '45.15,-93.85', 'd': 5}
```

## Feature Configs

These are optional objects you attach to sparse parsers. They serialize as top-level Solr params and also set a corresponding flag (e.g., `facet=true`).

### Faceting — `FacetParamsConfig`

Highlights:
- `facet.field: list[str]`
- `facet.query: list[str]`
- Range faceting: `facet.range`, `facet.range.start`, `facet.range.end`, `facet.range.gap`, etc.
- Pivot: `facet.pivot`

```python
from taiyo import StandardParser, FacetParamsConfig
parser = StandardParser(
    query="*:*",
    facet=FacetParamsConfig(fields=["category"], mincount=1),
)
params = parser.build()  # includes facet=true & facet.field=['category']
```

### Grouping — `GroupParamsConfig`

```python
from taiyo import StandardParser, GroupParamsConfig
parser = StandardParser(
    query="laptop",
    group=GroupParamsConfig(by=["brand", "category"], limit=2, ngroups=True),
)
```

### Highlighting — `HighlightParamsConfig`

Supports Unified/Original/FastVector variants and many tuning parameters.

```python
from taiyo import StandardParser, HighlightParamsConfig
parser = StandardParser(
    query="search terms",
    highlight=HighlightParamsConfig(fields=["title"], encoder="html", snippets=3),
)
```

### MoreLikeThis — `MoreLikeThisParamsConfig`

```python
from taiyo import StandardParser, MoreLikeThisParamsConfig
parser = StandardParser(
    query="id:123",
    more_like_this=MoreLikeThisParamsConfig(fields=["title","body"], min_term_freq=2),
)
```

## How configs serialize

Configs are regular Pydantic models extending `ParamsConfig`. When attached to a parser, they are flattened into top-level Solr params and the corresponding feature flag is set automatically.

For example, attaching `facet=FacetParamsConfig(fields=["category"])` yields:

```python
{
  'facet': True,
  'facet.field': ['category'],
  # ... plus any other set fields
}
```
