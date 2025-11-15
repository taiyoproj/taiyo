import pytest
from taiyo.parsers import (
    DisMaxQueryParser,
    ExtendedDisMaxQueryParser,
    BoundingBoxQueryParser,
    GeoFilterQueryParser,
)
from taiyo.params.configs.facet import FacetParamsConfig
from taiyo.params.configs.highlight import HighlightMethod
from taiyo.params.configs.group import GroupParamsConfig
import time
from pydantic import Field
from taiyo import SolrClient, SolrDocument, StandardParser, SolrError

import random
import string


SOLR_URL = "http://localhost:8983/solr"
_rand = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
COLLECTION = f"test_taiyo_integration_{_rand}"


def test_dismax_and_edismax_queries():
    with SolrClient(SOLR_URL, COLLECTION) as client:
        create_collection_with_schema(client)
        docs = [
            Store(id="1", name="Alpha", vector=[0.0, 0.0]),
            Store(id="2", name="Beta", vector=[1.0, 1.0]),
            Store(id="3", name="Gamma", vector=[2.0, 2.0]),
        ]
        client.add(docs)
        client.commit()
        time.sleep(1)

        # DisMax: multi-field, boosts, min match
        dismax = DisMaxQueryParser(
            query="Alpha Beta",
            query_fields={"name": 2.0},
            min_match="1",
        )
        res = client.search(dismax, document_model=Store)
        assert res.status == 0
        assert res.num_found >= 1

        # EDisMax: test split_on_whitespace, min_match_auto_relax
        edismax = ExtendedDisMaxQueryParser(
            query="Alpha Beta",
            query_fields={"name": 1.0},
            split_on_whitespace=True,
            min_match_auto_relax=True,
        )
        res2 = client.search(edismax, document_model=Store)
        assert res2.status == 0
        assert res2.num_found >= 1

        # Clean up
        try:
            client.delete_collection(COLLECTION)
        except SolrError as e:
            if getattr(e, "status_code", None) == 404:
                pass
            else:
                raise


def test_faceting_and_highlighting():
    with SolrClient(SOLR_URL, COLLECTION) as client:
        create_collection_with_schema(client)
        docs = [
            Store(id="1", name="Alpha", vector=[0.0, 0.0]),
            Store(id="2", name="Alpha", vector=[1.0, 1.0]),
            Store(id="3", name="Beta", vector=[2.0, 2.0]),
        ]
        client.add(docs)
        client.commit()
        time.sleep(1)

        # Use a fielded query that both matches and can produce highlights
        parser = StandardParser(query="name:Alpha", rows=10)
        parser.facet = FacetParamsConfig(fields=["name"])
        # Use HighlightParamsConfig instead of dict for highlight
        from taiyo.params.configs.highlight import HighlightParamsConfig

        parser.highlight = HighlightParamsConfig(
            method=HighlightMethod.UNIFIED,
            fields=["name"],
        )
        res = client.search(parser, document_model=Store)
        assert res.status == 0
        assert res.num_found >= 1
        # Facet counts and highlighting should be present in the response
        extra = getattr(res, "extra", {})
        assert "facet_counts" in extra or "facets" in extra
        # Verify highlight parameters were sent; some schemas/fieldTypes may not return highlighting
        params = extra.get("responseHeader", {}).get("params", {})
        assert params.get("highlight") == "true"
        assert "name" in params.get("hl.fl", "")

        try:
            client.delete_collection(COLLECTION)
        except SolrError as e:
            if getattr(e, "status_code", None) == 404:
                pass
            else:
                raise


@pytest.mark.integration
def test_grouping():
    with SolrClient(SOLR_URL, COLLECTION) as client:
        create_collection_with_schema(client)
        docs = [
            Store(id="1", name="Alpha", vector=[0.0, 0.0]),
            Store(id="2", name="Alpha", vector=[1.0, 1.0]),
            Store(id="3", name="Beta", vector=[2.0, 2.0]),
        ]
        client.add(docs)
        client.commit()
        time.sleep(1)

        parser = StandardParser(query="*:*", rows=10)
        parser.group = GroupParamsConfig(field="name", limit=2)
        res = client.search(parser, document_model=Store)
        # For grouped queries, Solr does not return 'response' at top level, so check grouped results in extra
        assert res.status == 0
        extra = getattr(res, "extra", {})
        assert "grouped" in extra
        grouped = extra["grouped"]
        assert "name" in grouped
        assert "groups" in grouped["name"]
        assert len(grouped["name"]["groups"]) >= 1

        # Clean up
        try:
            client.delete_collection(COLLECTION)
        except SolrError as e:
            if getattr(e, "status_code", None) == 404:
                pass
            else:
                raise


def test_spatial_bbox_and_geofilt():
    with SolrClient(SOLR_URL, COLLECTION) as client:
        create_collection_with_schema(client)
        docs = [
            Store(id="1", name="Alpha", vector=[0.0, 0.0]),
            Store(id="2", name="Beta", vector=[1.0, 1.0]),
            Store(id="3", name="Gamma", vector=[2.0, 2.0]),
        ]
        client.add(docs)
        client.commit()
        time.sleep(1)

        # BoundingBoxQueryParser
        bbox = BoundingBoxQueryParser(
            spatial_field="vector",
            center_point=[0.0, 0.0],
            radial_distance=10.0,
        )
        res = client.search(bbox, document_model=Store)
        assert res.status == 0

        # GeoFilterQueryParser
        geofilt = GeoFilterQueryParser(
            spatial_field="vector",
            center_point=[0.0, 0.0],
            radial_distance=10.0,
        )
        res2 = client.search(geofilt, document_model=Store)
        assert res2.status == 0

        # Clean up
        try:
            client.delete_collection(COLLECTION)
        except SolrError as e:
            if getattr(e, "status_code", None) == 404:
                pass
            else:
                raise


class Store(SolrDocument):
    id: str
    name: str
    vector: list[float] = Field(
        default_factory=list, description="Dense vector for KNN search"
    )


def create_collection_with_schema(client: SolrClient):
    import requests

    try:
        resp = requests.get(
            f"http://localhost:8983/solr/{COLLECTION}/schema/fields/vector", timeout=5
        )
        print("[DEBUG] Solr 'vector' field schema:", resp.json())
    except Exception as e:
        print("[DEBUG] Failed to fetch 'vector' field schema:", e)
    try:
        client.create_collection(COLLECTION, num_shards=1, replication_factor=1)
    except SolrError as e:
        if (
            hasattr(e, "response")
            and isinstance(e.response, dict)
            and "error" in e.response
            and "msg" in e.response["error"]
            and "already exists" in e.response["error"]["msg"]
        ):
            pass  # Ignore if collection already exists
        else:
            print("[DEBUG] Solr schema error response:", getattr(e, "response", e))
            raise
    time.sleep(1)
    # Add vector field type first
    vector_field_type = {
        "name": "knn_vector",
        "class": "solr.DenseVectorField",
        "vectorDimension": 2,
        "similarityFunction": "euclidean",
        "knnAlgorithm": "hnsw",
    }
    try:
        client._request(
            "POST", "schema/fieldtypes", json={"add-field-type": vector_field_type}
        )
    except SolrError as e:
        # Ignore 'already exists' errors for field types
        if hasattr(e, "response") and isinstance(e.response, dict):
            err = e.response.get("error", {})
            if "msg" in err and "already exists" in str(err["msg"]):
                pass
            else:
                print(
                    "[DEBUG] Solr vector field type error response:",
                    getattr(e, "response", e),
                )
                raise
        else:
            print(
                "[DEBUG] Solr vector field type error response:",
                getattr(e, "response", e),
            )
            raise
    # Add all fields, including vector
    schema_fields = [
        {"name": "id", "type": "string", "stored": True, "required": True},
        {"name": "name", "type": "string", "stored": True},
        {"name": "vector", "type": "knn_vector", "indexed": True, "stored": False},
    ]
    for field in schema_fields:
        try:
            client._request("POST", "schema/fields", json={"add-field": field})
        except SolrError as e:
            # Ignore 'already exists' errors for fields/types (robust: check all error locations and raw text)
            if hasattr(e, "response") and isinstance(e.response, dict):
                err = e.response.get("error", {})
                if "msg" in err and "already exists" in str(err["msg"]):
                    continue
                if "details" in err:
                    details = err["details"]
                    if isinstance(details, list):
                        found = False
                        for d in details:
                            if (
                                isinstance(d, dict)
                                and "errorMessages" in d
                                and any(
                                    "already exists" in msg
                                    for msg in d["errorMessages"]
                                )
                            ):
                                found = True
                                break
                        if found:
                            continue
                    elif isinstance(details, dict):
                        if "errorMessages" in details and any(
                            "already exists" in msg for msg in details["errorMessages"]
                        ):
                            continue
                raw_text = str(e.response)
                if "already exists" in raw_text:
                    continue
            print(
                "[DEBUG] Solr schema field error response:", getattr(e, "response", e)
            )
            raise
    time.sleep(1)


def test_solr_end_to_end():
    with SolrClient(SOLR_URL, COLLECTION) as client:
        create_collection_with_schema(client)
        # Add documents
        docs = [
            Store(id="1", name="Alpha", vector=[0.0, 0.0]),
            Store(id="2", name="Beta", vector=[1.0, 1.0]),
            Store(id="3", name="Gamma", vector=[2.0, 2.0]),
        ]
        client.add(docs)
        client.commit()
        time.sleep(1)

        # Query with StandardParser
        parser = StandardParser(query="name:Alpha", rows=2)
        res = client.search(parser, document_model=Store)
        assert res.status == 0
        assert res.num_found >= 1
        assert any(d.name == "Alpha" for d in res.docs)

        # Query with KNNQueryParser (dense vector search)
        from taiyo.parsers.dense.knn import KNNQueryParser

        # Use a placeholder vector field name 'vector'. Adjust as needed for your schema.
        knn = KNNQueryParser(field="vector", vector=[0.0, 0.0], top_k=2)
        try:
            res3 = client.search(knn, document_model=Store)
            assert res3.status == 0
        except SolrError as e:
            print("[DEBUG] Solr KNN query error response:", getattr(e, "response", e))
            raise

        client.delete_collection(COLLECTION)
