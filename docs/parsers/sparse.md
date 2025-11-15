# Sparse Query Parsers

Sparse query parsers are used for traditional text search and support Solr's standard, DisMax, and Extended DisMax (edismax) query syntaxes.

## Standard (lucene)

```python
from taiyo import StandardParser

parser = StandardParser(
    query="foo bar",
    query_operator="AND",  # q.op
    default_field="title", # df
    split_on_whitespace=True, # sow
    rows=20,
)
params = parser.build()  # {'q': 'foo bar', 'q.op': 'AND', 'df': 'title', 'sow': True, ...}
```

## DisMax

```python
from taiyo import DisMaxQueryParser, FacetParamsConfig

parser = DisMaxQueryParser(
    query="foo bar",
    query_fields={"title": 2.0, "body": 1.0},  # qf
    phrase_fields={"title": 3.0},                # pf
    phrase_slop=2,                                # ps
    query_slop=1,                                 # qs
    min_match="75%",                             # mm
    tie_breaker=0.1,                              # tie
    boost_queries=["cat:electronics^5.0"],       # bq
    boost_functons=["recip(rord(myfield),1,2,3)"], # bf
    facet=FacetParamsConfig(queries=["facet true"]),
)
res = client.search(parser)
```

## Extended DisMax (edismax)

```python
from taiyo import ExtendedDisMaxQueryParser

parser = ExtendedDisMaxQueryParser(
    query="foo bar",
    split_on_whitespace=True,
    lowercase_operators=True,
)
res = client.search(parser)
```

### Feature configs

You can attach feature configs (faceting, grouping, highlighting, more-like-this) to any sparse parser:

```python
from taiyo import GroupParamsConfig, HighlightParamsConfig

parser = StandardParser(
    query="laptop",
    group=GroupParamsConfig(field=["brand", "category"], limit=2),
    highlight=HighlightParamsConfig(fields=["title"], encoder="html", snippets=3),
)
res = client.search(parser)
print(res.highlighting)
```
