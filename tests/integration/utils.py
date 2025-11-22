import random
import string
import time
from pydantic import Field
from taiyo import SolrDocument
from taiyo.schema import SolrFieldType, SolrField, SolrFieldClass

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


def create_collection_with_schema(client, collection_name):
    """Create a test collection with schema configured using schema utilities.

    This sets up field types and fields needed for integration tests:
    - latlon_point: Spatial field type for lat/lon coordinates
    - knn_vector: Dense vector field type for KNN search
    - Standard fields: id, name, vector, latlon, bbox

    Args:
        client: SolrClient instance
        collection_name: Name of the collection to create

    Note: Does not call set_collection on the client - tests should do this themselves.
    """
    # Create collection
    try:
        client.create_collection(collection_name, num_shards=1, replication_factor=1)
    except Exception:
        pass  # Collection may already exist

    time.sleep(1)

    # Temporarily set collection for schema operations
    original_collection = client.collection
    client.set_collection(collection_name)

    try:
        # Define field types using schema utilities
        latlon_field_type = SolrFieldType(
            name="latlon_point",
            solr_class=SolrFieldClass.LATLON_POINT_SPATIAL,
        )

        vector_field_type = SolrFieldType(
            name="knn_vector",
            solr_class=SolrFieldClass.DENSE_VECTOR,
            vectorDimension=2,
            similarityFunction="euclidean",
            knnAlgorithm="hnsw",
        )

        # Add field types
        for field_type in [latlon_field_type, vector_field_type]:
            try:
                client.add_field_type(field_type)
            except Exception:
                pass  # Field type may already exist

        # Define fields using schema utilities
        fields = [
            SolrField(name="id", type="string", stored=True, required=True),
            SolrField(name="name", type="string", stored=True),
            SolrField(name="vector", type="knn_vector", indexed=True, stored=False),
            SolrField(name="latlon", type="latlon_point", indexed=True, stored=True),
            SolrField(name="bbox", type="bbox", indexed=True, stored=True),
        ]

        # Add fields
        for field in fields:
            try:
                client.add_field(field)
            except Exception:
                pass  # Field may already exist
    finally:
        # Restore original collection state
        if original_collection:
            client.set_collection(original_collection)
        else:
            client.collection = None

    time.sleep(1)
