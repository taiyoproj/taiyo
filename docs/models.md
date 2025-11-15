# Models and errors

## SolrDocument

Base class for your documents. It's a Pydantic model configured to allow extra fields by default.

```python
from taiyo import SolrDocument

class Product(SolrDocument):
    id: str
    title: str
    category: str
```

## SolrResponse[T]

A typed response wrapper returned by `client.search()`.

Fields:
- `status: int`
- `query_time (qtime): int`
- `num_found (numFound): int`
- `start: int`
- `docs: list[T]`
- `facet_counts: dict | None`
- `highlighting: dict[str, dict[str, list[str]]] | None`

```python
res = client.search("*:*")
print(res.status, res.query_time, res.num_found)
for d in res.docs:
    ...
```

## SolrError

Raised for any non-2xx HTTP responses or request failures. Includes optional status code and parsed response when available.

```python
from taiyo import SolrError
try:
    client.search("invalid:query]")
except SolrError as e:
    print(e.status_code)
    print(e.response)
```
