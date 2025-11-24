"""Integration tests for schema operations.

Tests field types, fields, dynamic fields, and copy fields operations
with verification against Solr's Schema API responses.
"""

import random
import string
import time
from typing import Dict, List, Any
import pytest

from taiyo import SolrClient, SolrError
from taiyo.schema import (
    SolrField,
    SolrDynamicField,
    SolrFieldType,
    SolrFieldClass,
)
from taiyo.schema.field_type import Analyzer, Tokenizer, Filter

SOLR_URL = "http://localhost:8983/solr"


def get_schema_field_types(client) -> List[Dict[str, Any]]:
    """Retrieve all field types from the schema.

    Reference: https://solr.apache.org/guide/solr/latest/indexing-guide/schema-api.html#list-field-types
    """
    response = client._request(
        method="GET", endpoint=f"{client.collection}/schema/fieldtypes"
    )
    return response.get("fieldTypes", [])


def get_schema_field_type(client, name: str) -> Dict[str, Any]:
    """Retrieve a specific field type from the schema.

    Reference: https://solr.apache.org/guide/solr/latest/indexing-guide/schema-api.html#retrieve-field-type-information
    """
    response = client._request(
        method="GET", endpoint=f"{client.collection}/schema/fieldtypes/{name}"
    )
    return response.get("fieldType", {})


def get_schema_fields(client) -> List[Dict[str, Any]]:
    """Retrieve all fields from the schema.

    Reference: https://solr.apache.org/guide/solr/latest/indexing-guide/schema-api.html#list-fields
    """
    response = client._request(
        method="GET", endpoint=f"{client.collection}/schema/fields"
    )
    return response.get("fields", [])


def get_schema_field(client, name: str) -> Dict[str, Any]:
    """Retrieve a specific field from the schema.

    Reference: https://solr.apache.org/guide/solr/latest/indexing-guide/schema-api.html#retrieve-field-information
    """
    response = client._request(
        method="GET", endpoint=f"{client.collection}/schema/fields/{name}"
    )
    return response.get("field", {})


def get_schema_dynamic_fields(client) -> List[Dict[str, Any]]:
    """Retrieve all dynamic fields from the schema.

    Reference: https://solr.apache.org/guide/solr/latest/indexing-guide/schema-api.html#list-dynamic-fields
    """
    response = client._request(
        method="GET", endpoint=f"{client.collection}/schema/dynamicfields"
    )
    return response.get("dynamicFields", [])


def get_schema_copy_fields(client) -> List[Dict[str, Any]]:
    """Retrieve all copy fields from the schema.

    Reference: https://solr.apache.org/guide/solr/latest/indexing-guide/schema-api.html#list-copy-fields
    """
    response = client._request(
        method="GET", endpoint=f"{client.collection}/schema/copyfields"
    )
    return response.get("copyFields", [])


def test_add_field_type_basic():
    """Test adding a basic field type and verify it's in the schema."""
    _rand = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    collection = f"test_schema_field_type_{_rand}"

    with SolrClient(SOLR_URL) as client:
        client.create_collection(collection, num_shards=1, replication_factor=1)
        client.set_collection(collection)
        time.sleep(1)

        try:
            # Create a simple text field type
            field_type = SolrFieldType(
                name=f"text_custom_{_rand}",
                solr_class=SolrFieldClass.TEXT,
                position_increment_gap=100,
            )

            # Add field type
            response = client.add_field_type(field_type)
            assert response.get("responseHeader", {}).get("status") == 0

            time.sleep(1)

            # Verify field type exists in schema
            field_types = get_schema_field_types(client)
            field_type_names = [ft["name"] for ft in field_types]
            assert f"text_custom_{_rand}" in field_type_names

            # Retrieve specific field type and verify properties
            retrieved_ft = get_schema_field_type(client, f"text_custom_{_rand}")
            assert retrieved_ft["name"] == f"text_custom_{_rand}"
            assert "TextField" in retrieved_ft["class"]
            # Solr returns positionIncrementGap as string
            assert int(retrieved_ft.get("positionIncrementGap")) == 100

        finally:
            client.delete_collection(collection)


def test_add_field_type_with_analyzer():
    """Test adding a field type with custom analyzer and verify configuration."""
    _rand = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    collection = f"test_schema_analyzer_{_rand}"

    with SolrClient(SOLR_URL) as client:
        client.create_collection(collection, num_shards=1, replication_factor=1)
        client.set_collection(collection)
        time.sleep(1)

        try:
            # Create field type with analyzer
            analyzer = Analyzer(
                tokenizer=Tokenizer(name="standard"),
                filters=[
                    Filter(name="lowercase"),
                    Filter(name="stop", words="stopwords.txt", ignoreCase=True),
                    Filter(name="synonymGraph", synonyms="synonyms.txt"),
                ],
            )

            field_type = SolrFieldType(
                name=f"text_analyzed_{_rand}",
                solr_class=SolrFieldClass.TEXT,
                analyzer=analyzer,
            )

            # Add field type
            response = client.add_field_type(field_type)
            assert response.get("responseHeader", {}).get("status") == 0

            time.sleep(1)

            # Verify field type with analyzer
            retrieved_ft = get_schema_field_type(client, f"text_analyzed_{_rand}")
            assert retrieved_ft["name"] == f"text_analyzed_{_rand}"

            # Verify analyzer configuration
            assert "analyzer" in retrieved_ft
            analyzer_config = retrieved_ft["analyzer"]

            # Check tokenizer - Solr may return it in different formats
            assert "tokenizer" in analyzer_config
            tokenizer = analyzer_config["tokenizer"]
            if isinstance(tokenizer, dict):
                # Check if it has class key or className key
                tokenizer_class = tokenizer.get("class") or tokenizer.get(
                    "className", ""
                )
                assert (
                    "Standard" in tokenizer_class or tokenizer.get("name") == "standard"
                )

            # Check filters exist
            assert "filters" in analyzer_config
            filters = analyzer_config["filters"]
            assert len(filters) == 3

            # Verify filter names/classes
            filter_info = []
            for f in filters:
                if isinstance(f, dict):
                    filter_info.append(
                        f.get("class", "")
                        or f.get("className", "")
                        or f.get("name", "")
                    )

            filter_str = " ".join(filter_info).lower()
            assert "lowercase" in filter_str or "lower" in filter_str
            assert "stop" in filter_str
            assert "synonym" in filter_str

        finally:
            client.delete_collection(collection)


def test_add_field_type_dense_vector():
    """Test adding a dense vector field type for KNN search."""
    _rand = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    collection = f"test_schema_vector_{_rand}"

    with SolrClient(SOLR_URL) as client:
        client.create_collection(collection, num_shards=1, replication_factor=1)
        client.set_collection(collection)
        time.sleep(1)

        try:
            # Create dense vector field type
            field_type = SolrFieldType(
                name=f"knn_vector_{_rand}",
                solr_class=SolrFieldClass.DENSE_VECTOR,
                vectorDimension=384,
                similarityFunction="cosine",
                knnAlgorithm="hnsw",
            )

            # Add field type
            response = client.add_field_type(field_type)
            assert response.get("responseHeader", {}).get("status") == 0

            time.sleep(1)

            # Verify vector field type
            retrieved_ft = get_schema_field_type(client, f"knn_vector_{_rand}")
            assert retrieved_ft["name"] == f"knn_vector_{_rand}"
            assert "DenseVectorField" in retrieved_ft["class"]
            # Solr returns numeric values as strings
            assert int(retrieved_ft.get("vectorDimension")) == 384
            assert retrieved_ft.get("similarityFunction") == "cosine"
            assert retrieved_ft.get("knnAlgorithm") == "hnsw"

        finally:
            client.delete_collection(collection)


def test_add_field():
    """Test adding a field and verify it's in the schema."""
    _rand = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    collection = f"test_schema_field_{_rand}"

    with SolrClient(SOLR_URL) as client:
        client.create_collection(collection, num_shards=1, replication_factor=1)
        client.set_collection(collection)
        time.sleep(1)

        try:
            # Add a field
            field = SolrField(
                name=f"title_{_rand}",
                type="text_general",
                indexed=True,
                stored=True,
                required=False,
                multiValued=False,
            )

            response = client.add_field(field)
            assert response.get("responseHeader", {}).get("status") == 0

            time.sleep(1)

            # Verify field exists
            fields = get_schema_fields(client)
            field_names = [f["name"] for f in fields]
            assert f"title_{_rand}" in field_names

            # Retrieve specific field and verify properties
            retrieved_field = get_schema_field(client, f"title_{_rand}")
            assert retrieved_field["name"] == f"title_{_rand}"
            assert retrieved_field["type"] == "text_general"
            assert retrieved_field["indexed"]
            assert retrieved_field["stored"]

        finally:
            client.delete_collection(collection)


def test_add_multiple_fields():
    """Test adding multiple fields with different types."""
    _rand = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    collection = f"test_schema_multi_fields_{_rand}"

    with SolrClient(SOLR_URL) as client:
        client.create_collection(collection, num_shards=1, replication_factor=1)
        client.set_collection(collection)
        time.sleep(1)

        try:
            # Add multiple fields
            fields = [
                SolrField(
                    name=f"title_{_rand}",
                    type="text_general",
                    stored=True,
                    indexed=True,
                ),
                SolrField(
                    name=f"price_{_rand}", type="pfloat", stored=True, indexed=True
                ),
                SolrField(
                    name=f"category_{_rand}", type="string", stored=True, indexed=True
                ),
                SolrField(
                    name=f"published_{_rand}", type="pdate", stored=True, indexed=True
                ),
                SolrField(
                    name=f"tags_{_rand}", type="strings", stored=True, multiValued=True
                ),
            ]

            for field in fields:
                response = client.add_field(field)
                assert response.get("responseHeader", {}).get("status") == 0

            time.sleep(1)

            # Verify all fields exist
            schema_fields = get_schema_fields(client)
            field_names = [f["name"] for f in schema_fields]

            assert f"title_{_rand}" in field_names
            assert f"price_{_rand}" in field_names
            assert f"category_{_rand}" in field_names
            assert f"published_{_rand}" in field_names
            assert f"tags_{_rand}" in field_names

            # Verify specific field properties
            title_field = get_schema_field(client, f"title_{_rand}")
            assert title_field["type"] == "text_general"
            assert title_field["indexed"]

            price_field = get_schema_field(client, f"price_{_rand}")
            assert price_field["type"] == "pfloat"

            tags_field = get_schema_field(client, f"tags_{_rand}")
            assert tags_field["multiValued"]

        finally:
            client.delete_collection(collection)


def test_add_dynamic_field():
    """Test adding a dynamic field and verify it's in the schema."""
    _rand = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    collection = f"test_schema_dynamic_{_rand}"

    with SolrClient(SOLR_URL) as client:
        client.create_collection(collection, num_shards=1, replication_factor=1)
        client.set_collection(collection)
        time.sleep(1)

        try:
            # Add dynamic field
            dynamic_field = SolrDynamicField(
                name=f"*_txt_{_rand}",
                type="text_general",
                indexed=True,
                stored=True,
                multiValued=True,
            )

            response = client.add_dynamic_field(dynamic_field)
            assert response.get("responseHeader", {}).get("status") == 0

            time.sleep(1)

            # Verify dynamic field exists
            dynamic_fields = get_schema_dynamic_fields(client)
            dynamic_field_names = [df["name"] for df in dynamic_fields]
            assert f"*_txt_{_rand}" in dynamic_field_names

            # Find and verify the specific dynamic field
            matching_df = next(
                (df for df in dynamic_fields if df["name"] == f"*_txt_{_rand}"), None
            )
            assert matching_df is not None
            assert matching_df["type"] == "text_general"
            assert matching_df["indexed"]
            assert matching_df["stored"]
            assert matching_df["multiValued"]

        finally:
            client.delete_collection(collection)


def test_add_multiple_dynamic_fields():
    """Test adding multiple dynamic fields with different patterns."""
    _rand = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    collection = f"test_schema_multi_dynamic_{_rand}"

    with SolrClient(SOLR_URL) as client:
        client.create_collection(collection, num_shards=1, replication_factor=1)
        client.set_collection(collection)
        time.sleep(1)

        try:
            # Add multiple dynamic fields
            dynamic_fields = [
                SolrDynamicField(name=f"*_s_{_rand}", type="string", stored=True),
                SolrDynamicField(
                    name=f"*_i_{_rand}", type="pint", indexed=True, stored=True
                ),
                SolrDynamicField(
                    name=f"*_f_{_rand}", type="pfloat", indexed=True, stored=True
                ),
                SolrDynamicField(
                    name=f"*_dt_{_rand}", type="pdate", indexed=True, stored=True
                ),
                SolrDynamicField(
                    name=f"*_ss_{_rand}", type="strings", multiValued=True, stored=True
                ),
            ]

            for df in dynamic_fields:
                response = client.add_dynamic_field(df)
                assert response.get("responseHeader", {}).get("status") == 0

            time.sleep(1)

            # Verify all dynamic fields exist
            schema_dynamic_fields = get_schema_dynamic_fields(client)
            dynamic_names = [df["name"] for df in schema_dynamic_fields]

            assert f"*_s_{_rand}" in dynamic_names
            assert f"*_i_{_rand}" in dynamic_names
            assert f"*_f_{_rand}" in dynamic_names
            assert f"*_dt_{_rand}" in dynamic_names
            assert f"*_ss_{_rand}" in dynamic_names

            # Verify specific properties
            string_df = next(
                (df for df in schema_dynamic_fields if df["name"] == f"*_s_{_rand}"),
                None,
            )
            assert string_df["type"] == "string"

            multi_df = next(
                (df for df in schema_dynamic_fields if df["name"] == f"*_ss_{_rand}"),
                None,
            )
            assert multi_df["multiValued"]

        finally:
            client.delete_collection(collection)


def test_field_type_spatial():
    """Test adding spatial field type for geospatial queries."""
    _rand = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    collection = f"test_schema_spatial_{_rand}"

    with SolrClient(SOLR_URL) as client:
        client.create_collection(collection, num_shards=1, replication_factor=1)
        client.set_collection(collection)
        time.sleep(1)

        try:
            # Create LatLonPointSpatialField
            field_type = SolrFieldType(
                name=f"location_{_rand}",
                solr_class=SolrFieldClass.LATLON_POINT_SPATIAL,
            )

            response = client.add_field_type(field_type)
            assert response.get("responseHeader", {}).get("status") == 0

            time.sleep(1)

            # Verify spatial field type
            retrieved_ft = get_schema_field_type(client, f"location_{_rand}")
            assert retrieved_ft["name"] == f"location_{_rand}"
            assert "LatLonPointSpatialField" in retrieved_ft["class"]

            # Add a field using this type
            field = SolrField(
                name=f"coordinates_{_rand}",
                type=f"location_{_rand}",
                indexed=True,
                stored=True,
            )

            response = client.add_field(field)
            assert response.get("responseHeader", {}).get("status") == 0

            time.sleep(1)

            # Verify field
            retrieved_field = get_schema_field(client, f"coordinates_{_rand}")
            assert retrieved_field["type"] == f"location_{_rand}"

        finally:
            client.delete_collection(collection)


def test_error_duplicate_field():
    """Test that adding a duplicate field raises an error."""
    _rand = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    collection = f"test_schema_duplicate_{_rand}"

    with SolrClient(SOLR_URL) as client:
        client.create_collection(collection, num_shards=1, replication_factor=1)
        client.set_collection(collection)
        time.sleep(1)

        try:
            # Add a field
            field = SolrField(
                name=f"duplicate_{_rand}",
                type="string",
                stored=True,
            )

            response = client.add_field(field)
            assert response.get("responseHeader", {}).get("status") == 0

            time.sleep(1)

            # Try to add the same field again - should fail
            with pytest.raises(SolrError) as exc_info:
                client.add_field(field)

            # Verify error indicates duplicate field
            assert exc_info.value.status_code == 400

        finally:
            client.delete_collection(collection)


def test_error_invalid_field_type_reference():
    """Test that referencing a non-existent field type raises an error."""
    _rand = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    collection = f"test_schema_invalid_type_{_rand}"

    with SolrClient(SOLR_URL) as client:
        client.create_collection(collection, num_shards=1, replication_factor=1)
        client.set_collection(collection)
        time.sleep(1)

        try:
            # Try to add field with non-existent type
            field = SolrField(
                name=f"test_{_rand}",
                type=f"nonexistent_type_{_rand}",
                stored=True,
            )

            with pytest.raises(SolrError) as exc_info:
                client.add_field(field)

            # Should get an error about the field type not existing
            assert exc_info.value.status_code == 400

        finally:
            client.delete_collection(collection)


def test_complete_schema_workflow():
    """Test complete workflow: add field type, fields, dynamic fields, and verify all."""
    _rand = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    collection = f"test_schema_complete_{_rand}"

    with SolrClient(SOLR_URL) as client:
        client.create_collection(collection, num_shards=1, replication_factor=1)
        client.set_collection(collection)
        time.sleep(1)

        try:
            # 1. Add custom field type
            field_type = SolrFieldType(
                name=f"text_custom_{_rand}",
                solr_class=SolrFieldClass.TEXT,
                analyzer=Analyzer(
                    tokenizer=Tokenizer(name="standard"),
                    filters=[Filter(name="lowercase")],
                ),
            )
            response = client.add_field_type(field_type)
            assert response.get("responseHeader", {}).get("status") == 0

            time.sleep(0.5)

            # 2. Add regular fields
            fields = [
                SolrField(
                    name=f"id_{_rand}", type="string", stored=True, required=True
                ),
                SolrField(
                    name=f"title_{_rand}",
                    type=f"text_custom_{_rand}",
                    indexed=True,
                    stored=True,
                ),
                SolrField(
                    name=f"price_{_rand}", type="pfloat", indexed=True, stored=True
                ),
            ]

            for field in fields:
                response = client.add_field(field)
                assert response.get("responseHeader", {}).get("status") == 0

            time.sleep(0.5)

            # 3. Add dynamic fields
            dynamic_fields = [
                SolrDynamicField(name=f"*_s_{_rand}", type="string", stored=True),
                SolrDynamicField(
                    name=f"*_txt_{_rand}",
                    type=f"text_custom_{_rand}",
                    indexed=True,
                    stored=True,
                ),
            ]

            for df in dynamic_fields:
                response = client.add_dynamic_field(df)
                assert response.get("responseHeader", {}).get("status") == 0

            time.sleep(1)

            # 4. Verify all schema components
            # Verify field type
            field_types = get_schema_field_types(client)
            assert any(ft["name"] == f"text_custom_{_rand}" for ft in field_types)

            # Verify fields
            schema_fields = get_schema_fields(client)
            field_names = [f["name"] for f in schema_fields]
            assert f"id_{_rand}" in field_names
            assert f"title_{_rand}" in field_names
            assert f"price_{_rand}" in field_names

            # Verify title field uses custom type
            title_field = get_schema_field(client, f"title_{_rand}")
            assert title_field["type"] == f"text_custom_{_rand}"

            # Verify dynamic fields
            schema_dynamic_fields = get_schema_dynamic_fields(client)
            dynamic_names = [df["name"] for df in schema_dynamic_fields]
            assert f"*_s_{_rand}" in dynamic_names
            assert f"*_txt_{_rand}" in dynamic_names

        finally:
            client.delete_collection(collection)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
