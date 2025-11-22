# Taiyo

Taiyo is a Python client for Apache Solr built with httpx and Pydantic.

The library provides a type-safe interface for interacting with Apache Solr, supporting both synchronous and asynchronous operations. It includes comprehensive support for Solr's query parsers, schema management, and vector search capabilities.

## Features

- Synchronous and asynchronous client implementations with httpx
- Type safety with Pydantic for runtime validation and IDE support
- Support for Solr query parsers for sparse (standard, dismax, edismax), dense vector and spatial search
- Pythonic method chains for grouping/faceting/highlighting search results
- Programmatic schema definition for indexing
- Authentication via Basic Auth, Bearer Token, and OAuth2

## Installation

```bash
pip install taiyo
```

Or using [uv](https://github.com/astral-sh/uv):

```bash
uv add taiyo
```

## Quick Start

```python
from typing import Optional
from taiyo import SolrClient, SolrDocument
from taiyo.parsers import StandardQueryParser

class Passenger(SolrDocument):
    name: str
    sex: str
    age: Optional[float] = None
    survived: int
    pclass: int
    fare: Optional[float] = None
    embarked: Optional[str] = None

with SolrClient("http://localhost:8983/solr") as client:
    client.set_collection("titanic")
    
    passenger = Passenger(
        name="Braund, Mr. Owen Harris",
        sex="male",
        age=22.0,
        survived=0,
        pclass=3,
        fare=7.25,
        embarked="S"
    )
    client.add(passenger, commit=True)
    
    parser = StandardQueryParser(
        query="sex:male AND pclass:3",
        filter_queries=["age:[20 TO 30]"]
    )
    results: list[Passenger] = client.search(parser, rows=10, document_model=Passenger)
    
    print(f"Found {results.num_found} passengers")
    for doc in results.documents:
        print(f"{passenger.name}, Age: {passenger.age}, Class: {passenger.pclass}")
```

## Async Support

```python
from typing import Optional
from taiyo import AsyncSolrClient, SolrDocument
from taiyo.parsers import StandardQueryParser

class Passenger(SolrDocument):
    name: str
    sex: str
    age: Optional[float] = None
    survived: int
    pclass: int
    fare: Optional[float] = None

async with AsyncSolrClient("http://localhost:8983/solr") as client:
    client.set_collection("titanic")
    
    # Batch indexing
    passengers = [
        Passenger(name="Allen, Miss. Elisabeth", sex="female", age=29.0, survived=1, pclass=1, fare=211.34),
        Passenger(name="Moran, Mr. James", sex="male", age=None, survived=0, pclass=3, fare=8.46)
    ]
    await client.add(passengers, commit=True)
    
    # Search with filtering
    parser = StandardQueryParser(
        query="pclass:1 AND survived:1",
        filter_queries=["sex:female"]
    )
    results = await client.search(parser)
    
    # Type-safe result processing
    for doc in results.documents:
        p = Passenger.model_validate(doc)
        print(f"{p.name} survived, paid ${p.fare}")
```

## Requirements

- Python 3.11+
- Apache Solr 8.0+

## License

MIT License. See LICENSE for details.
