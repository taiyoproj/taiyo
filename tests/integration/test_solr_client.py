# Integration test: create collection, schema, add docs, query with parsers
import time
import pytest
from pydantic import Field
from taiyo import SolrClient, SolrDocument, StandardParser, BoundingBoxQueryParser, SolrError

SOLR_URL = "http://localhost:8983/solr"
COLLECTION = "test_taiyo_integration"

class Store(SolrDocument):
	id: str
	name: str
	store: str = Field(description="lat,lon string")

def create_collection_with_schema(client):
	# Try to delete if exists
	try:
		client.delete_collection(COLLECTION)
		time.sleep(1)
	except Exception:
		pass
	# Create collection
	client.create_collection(COLLECTION, num_shards=1, replication_factor=1)
	time.sleep(1)
	# Add schema fields
	schema_fields = [
		{"name": "id", "type": "string", "stored": True, "required": True},
		{"name": "name", "type": "string", "stored": True},
		{"name": "store", "type": "location", "stored": True, "indexed": True},
	]
	for field in schema_fields:
		client._request("POST", "schema/fields", json=field)
	time.sleep(1)

@pytest.mark.integration
def test_solr_end_to_end():
	with SolrClient(SOLR_URL, COLLECTION) as client:
		create_collection_with_schema(client)
		# Add documents
		docs = [
			Store(id="1", name="Alpha", store="45.15,-93.85"),
			Store(id="2", name="Beta", store="45.16,-93.86"),
			Store(id="3", name="Gamma", store="46.00,-94.00"),
		]
		client.add(docs)
		client.commit()
		time.sleep(1)

		# Query with StandardParser
		parser = StandardParser(query="Alpha", rows=2)
		res = client.search(parser, document_model=Store)
		assert res.status == 0
		assert res.num_found >= 1
		assert any(d.name == "Alpha" for d in res.docs)

		# Query with BoundingBoxQueryParser (spatial)
		bbox = BoundingBoxQueryParser(
			spatial_field="store",
			center_point=[45.15, -93.85],
			radial_distance=5,
		)
		res2 = client.search(bbox, document_model=Store)
		assert res2.status == 0
		assert any(d.name == "Alpha" for d in res2.docs)
		assert any(d.name == "Beta" for d in res2.docs)

		# Clean up
		client.delete_collection(COLLECTION)
