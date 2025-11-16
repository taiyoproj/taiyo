import random
import string
from pydantic import Field
from taiyo import SolrDocument

SOLR_URL = "http://localhost:8983/solr"
_rand = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))

COLLECTION = f"test_taiyo_integration_{_rand}"


class Store(SolrDocument):
    id: str
    name: str
    vector: list[float] = Field(
        default_factory=list, description="Dense vector for KNN search"
    )


class LatLonDoc(SolrDocument):
    id: str
    name: str
    latlon: str


def create_collection_with_schema(client):
    import httpx

    try:
        resp = httpx.get(
            f"http://localhost:8983/solr/{COLLECTION}/schema/fields/vector", timeout=5
        )
        print("[DEBUG] Solr 'vector' field schema:", resp.json())
    except Exception as e:
        print("[DEBUG] Failed to fetch 'vector' field schema:", e)
    try:
        client.create_collection(COLLECTION, num_shards=1, replication_factor=1)
    except Exception:
        pass
    import time

    time.sleep(1)
    latlon_field_type = {
        "name": "latlon_point",
        "class": "solr.LatLonPointSpatialField",
    }
    try:
        client._request(
            "POST",
            f"{COLLECTION}/schema/fieldtypes",
            json={"add-field-type": latlon_field_type},
        )
    except Exception:
        pass
    pdouble_field_type = {
        "name": "pdouble",
        "class": "solr.DoublePointField",
        "docValues": True,
    }
    try:
        client._request(
            "POST",
            f"{COLLECTION}/schema/fieldtypes",
            json={"add-field-type": pdouble_field_type},
        )
    except Exception:
        pass
    vector_field_type = {
        "name": "knn_vector",
        "class": "solr.DenseVectorField",
        "vectorDimension": 2,
        "similarityFunction": "euclidean",
        "knnAlgorithm": "hnsw",
    }
    try:
        client._request(
            "POST",
            f"{COLLECTION}/schema/fieldtypes",
            json={"add-field-type": vector_field_type},
        )
    except Exception:
        pass
    schema_fields = [
        {"name": "id", "type": "string", "stored": True, "required": True},
        {"name": "name", "type": "string", "stored": True},
        {"name": "vector", "type": "knn_vector", "indexed": True, "stored": False},
        {"name": "latlon", "type": "latlon_point", "indexed": True, "stored": True},
        {"name": "bbox", "type": "bbox", "indexed": True, "stored": True},
    ]
    for field in schema_fields:
        try:
            client._request(
                "POST", f"{COLLECTION}/schema/fields", json={"add-field": field}
            )
        except Exception:
            pass
    time.sleep(1)
