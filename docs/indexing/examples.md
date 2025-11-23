# Indexing Examples

This guide demonstrates practical indexing patterns using the Titanic dataset as an example.

## Titanic Dataset

The Titanic dataset contains passenger information from the RMS Titanic. Each record includes:

- **name**: Passenger name
- **sex**: Gender (male/female)
- **age**: Age in years
- **survived**: Survival status (0=No, 1=Yes)
- **pclass**: Passenger class (1=1st, 2=2nd, 3=3rd)
- **fare**: Ticket fare
- **embarked**: Port of embarkation (C=Cherbourg, Q=Queenstown, S=Southampton)
- **sibsp**: Number of siblings/spouses aboard
- **parch**: Number of parents/children aboard

## Synchronous Indexing

### Basic Example

```python
from taiyo import SolrClient, SolrDocument

passengers = [
    {
        "name": "Braund, Mr. Owen Harris",
        "sex": "male",
        "age": 22.0,
        "survived": 0,
        "pclass": 3,
        "fare": 7.25,
        "embarked": "S",
        "sibsp": 1,
        "parch": 0
    },
    {
        "name": "Cumings, Mrs. John Bradley",
        "sex": "female",
        "age": 38.0,
        "survived": 1,
        "pclass": 1,
        "fare": 71.2833,
        "embarked": "C",
        "sibsp": 1,
        "parch": 0
    },
    {
        "name": "Heikkinen, Miss. Laina",
        "sex": "female",
        "age": 26.0,
        "survived": 1,
        "pclass": 3,
        "fare": 7.925,
        "embarked": "S",
        "sibsp": 0,
        "parch": 0
    }
]

with SolrClient("http://localhost:8983/solr") as client:
    client.set_collection("titanic")
    
    docs = [SolrDocument(**passenger) for passenger in passengers]
    client.add(docs, commit=True)
    
    print(f"Indexed {len(docs)} passengers")
```

### Loading from CSV

```python
import csv
from taiyo import SolrClient, SolrDocument

def index_titanic_csv(csv_path: str):
    with SolrClient("http://localhost:8983/solr") as client:
        client.set_collection("titanic")
        
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            
            batch = []
            batch_size = 100
            
            for row in reader:
                doc = SolrDocument(
                    name=row['name'],
                    sex=row['sex'],
                    age=float(row['age']) if row['age'] else None,
                    survived=int(row['survived']),
                    pclass=int(row['pclass']),
                    fare=float(row['fare']) if row['fare'] else None,
                    embarked=row.get('embarked', ''),
                    sibsp=int(row['sibsp']),
                    parch=int(row['parch'])
                )
                
                batch.append(doc)
                
                if len(batch) >= batch_size:
                    client.add(batch, commit=False)
                    print(f"Indexed {len(batch)} passengers")
                    batch = []
            
            if batch:
                client.add(batch, commit=False)
                print(f"Indexed {len(batch)} passengers")
            
            client.commit()
            print("Indexing complete")

index_titanic_csv("titanic.csv")
```

### With Type-Safe Model

```python
from typing import Optional
from taiyo import SolrDocument, SolrClient

class Passenger(SolrDocument):
    name: str
    sex: str
    age: Optional[float] = None
    survived: int
    pclass: int
    fare: Optional[float] = None
    embarked: Optional[str] = None
    sibsp: int = 0
    parch: int = 0

passengers = [
    Passenger(
        name="Braund, Mr. Owen Harris",
        sex="male",
        age=22.0,
        survived=0,
        pclass=3,
        fare=7.25,
        embarked="S",
        sibsp=1,
        parch=0
    ),
    Passenger(
        name="Cumings, Mrs. John Bradley",
        sex="female",
        age=38.0,
        survived=1,
        pclass=1,
        fare=71.2833,
        embarked="C",
        sibsp=1,
        parch=0
    )
]

with SolrClient("http://localhost:8983/solr") as client:
    client.set_collection("titanic")
    client.add(passengers, commit=True)
```

## Asynchronous Indexing

### Basic Async Example

```python
import asyncio
from taiyo import AsyncSolrClient, SolrDocument

async def index_passengers():
    passengers = [
        {
            "name": "Braund, Mr. Owen Harris",
            "sex": "male",
            "age": 22.0,
            "survived": 0,
            "pclass": 3,
            "fare": 7.25,
            "embarked": "S"
        },
        {
            "name": "Cumings, Mrs. John Bradley",
            "sex": "female",
            "age": 38.0,
            "survived": 1,
            "pclass": 1,
            "fare": 71.2833,
            "embarked": "C"
        }
    ]
    
    async with AsyncSolrClient("http://localhost:8983/solr") as client:
        client.set_collection("titanic")
        
        docs = [SolrDocument(**p) for p in passengers]
        await client.add(docs, commit=True)
        
        print(f"Indexed {len(docs)} passengers")

asyncio.run(index_passengers())
```

### Async CSV Loading

```python
import asyncio
import csv
from taiyo import AsyncSolrClient, SolrDocument

async def index_titanic_async(csv_path: str):
    async with AsyncSolrClient("http://localhost:8983/solr") as client:
        client.set_collection("titanic")
        
        batch = []
        batch_size = 100
        
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                doc = SolrDocument(
                    name=row['name'],
                    sex=row['sex'],
                    age=float(row['age']) if row['age'] else None,
                    survived=int(row['survived']),
                    pclass=int(row['pclass']),
                    fare=float(row['fare']) if row['fare'] else None,
                    embarked=row.get('embarked', ''),
                    sibsp=int(row['sibsp']),
                    parch=int(row['parch'])
                )
                
                batch.append(doc)
                
                if len(batch) >= batch_size:
                    await client.add(batch, commit=False)
                    print(f"Indexed {len(batch)} passengers")
                    batch = []
            
            if batch:
                await client.add(batch, commit=False)
                print(f"Indexed {len(batch)} passengers")
            
            await client.commit()
            print("Indexing complete")

asyncio.run(index_titanic_async("titanic.csv"))
```

### Concurrent Indexing from Multiple Sources

```python
import asyncio
from taiyo import AsyncSolrClient, SolrDocument

async def load_male_passengers():
    return [
        SolrDocument(name="Braund, Mr. Owen Harris", sex="male", age=22.0, survived=0, pclass=3),
        SolrDocument(name="Allen, Mr. William Henry", sex="male", age=35.0, survived=0, pclass=3)
    ]

async def load_female_passengers():
    return [
        SolrDocument(name="Cumings, Mrs. John Bradley", sex="female", age=38.0, survived=1, pclass=1),
        SolrDocument(name="Heikkinen, Miss. Laina", sex="female", age=26.0, survived=1, pclass=3)
    ]

async def index_from_source(client, source_func, name):
    docs = await source_func()
    await client.add(docs, commit=False)
    print(f"Indexed {len(docs)} passengers from {name}")

async def index_concurrently():
    async with AsyncSolrClient("http://localhost:8983/solr") as client:
        client.set_collection("titanic")
        
        await asyncio.gather(
            index_from_source(client, load_male_passengers, "male source"),
            index_from_source(client, load_female_passengers, "female source")
        )
        
        await client.commit()
        print("All sources indexed")

asyncio.run(index_concurrently())
```

## Pandas Integration

```python
import pandas as pd
from taiyo import SolrClient, SolrDocument

df = pd.read_csv("titanic.csv")

df = df.fillna({
    'age': 0.0,
    'fare': 0.0,
    'embarked': ''
})

with SolrClient("http://localhost:8983/solr") as client:
    client.set_collection("titanic")
    
    batch = []
    batch_size = 100
    
    for _, row in df.iterrows():
        doc = SolrDocument(
            name=row['name'],
            sex=row['sex'],
            age=float(row['age']),
            survived=int(row['survived']),
            pclass=int(row['pclass']),
            fare=float(row['fare']),
            embarked=row['embarked'],
            sibsp=int(row['sibsp']),
            parch=int(row['parch'])
        )
        
        batch.append(doc)
        
        if len(batch) >= batch_size:
            client.add(batch, commit=False)
            batch = []
    
    if batch:
        client.add(batch, commit=False)
    
    client.commit()
    print(f"Indexed {len(df)} passengers")
```

## Schema Setup for Titanic Dataset

```python
from taiyo import SolrClient
from taiyo.schema import SolrField, SolrFieldClass

with SolrClient("http://localhost:8983/solr") as client:
    client.set_collection("titanic")
    
    fields = [
        SolrField(name="name", type="text_general", indexed=True, stored=True),
        SolrField(name="sex", type="string", indexed=True, stored=True),
        SolrField(name="age", type="pfloat", indexed=True, stored=True),
        SolrField(name="survived", type="pint", indexed=True, stored=True),
        SolrField(name="pclass", type="pint", indexed=True, stored=True),
        SolrField(name="fare", type="pfloat", indexed=True, stored=True),
        SolrField(name="embarked", type="string", indexed=True, stored=True),
        SolrField(name="sibsp", type="pint", indexed=True, stored=True),
        SolrField(name="parch", type="pint", indexed=True, stored=True)
    ]
    
    for field in fields:
        client.add_field(field)
    
    print("Schema configured")
```

## Searching Indexed Data

```python
from taiyo import SolrClient
from taiyo.parsers import ExtendedDisMaxQueryParser

with SolrClient("http://localhost:8983/solr") as client:
    client.set_collection("titanic")
    
    parser = (
        ExtendedDisMaxQueryParser(
            query="Mrs",
            query_fields={"name": 2.0}
        )
        .facet(fields=["sex", "pclass", "survived"], mincount=1)
    )
    
    results = client.search(parser)
    
    print(f"Found {results.num_found} passengers")
    
    for doc in results.docs:
        print(f"{doc.name} - Class {doc.pclass}, Survived: {doc.survived}")
    
    if results.facets:
        print("\nFacets:")
        facets = results.facets
        for field, facet in facets.fields.items():
            print(f"\n{field}:")
            for bucket in facet.buckets:
                print(f"  {bucket.value}: {bucket.count}")
```

## Performance Tips

### Batch Size Optimization

```python
batch_size = 500

for i in range(0, len(passengers), batch_size):
    batch = passengers[i:i + batch_size]
    client.add(batch, commit=False)

client.commit()
```

### Progress Tracking

```python
from tqdm import tqdm

with SolrClient("http://localhost:8983/solr") as client:
    client.set_collection("titanic")
    
    batch = []
    batch_size = 100
    
    for passenger in tqdm(passengers, desc="Indexing"):
        doc = SolrDocument(**passenger)
        batch.append(doc)
        
        if len(batch) >= batch_size:
            client.add(batch, commit=False)
            batch = []
    
    if batch:
        client.add(batch, commit=False)
    
    client.commit()
```

## Error Handling

```python
from taiyo import SolrClient, SolrDocument, SolrError

def safe_index(passengers):
    with SolrClient("http://localhost:8983/solr") as client:
        client.set_collection("titanic")
        
        failed = []
        
        for passenger in passengers:
            try:
                doc = SolrDocument(**passenger)
                client.add(doc, commit=False)
            except ValueError as e:
                print(f"Invalid passenger data: {e}")
                failed.append(passenger)
            except SolrError as e:
                print(f"Solr error: {e}")
                failed.append(passenger)
        
        try:
            client.commit()
        except SolrError as e:
            print(f"Commit failed: {e}")
        
        return failed
```

## See Also

- [Indexing Overview](overview.md) - Core indexing concepts
- [Schema Management](schema.md) - Define fields and types
- [Client Overview](../clients/overview.md) - Client configuration
