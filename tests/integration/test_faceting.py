import random
import string
import time
from pydantic import Field
from taiyo import SolrClient, SolrError, SolrDocument
from taiyo.schema import SolrField
from taiyo.params.configs.facet import FacetParamsConfig
from taiyo.params.configs.highlight import HighlightMethod, HighlightParamsConfig
from taiyo.parsers import StandardParser

SOLR_URL = "http://localhost:8983/solr"


class Store(SolrDocument):
    name: str
    vector: list[float] = Field(
        default_factory=list, description="Dense vector for KNN search"
    )


def test_faceting_and_highlighting():
    """End-to-end test for faceting and highlighting."""
    _rand = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    collection = f"test_taiyo_faceting_{_rand}"
    
    with SolrClient(SOLR_URL) as client:
        # Create collection
        client.create_collection(collection, num_shards=1, replication_factor=1)
        time.sleep(1)
        
        client.set_collection(collection)
        
        # Define and add fields
        fields = [
            SolrField(name="name", type="string", stored=True),
        ]
        
        for field in fields:
            try:
                client.add_field(field)
            except SolrError:
                pass  # Field may already exist
        
        time.sleep(1)
        
        # Add test documents
        docs = [
            Store(name="Alpha", vector=[0.0, 0.0]),
            Store(name="Alpha", vector=[1.0, 1.0]),
            Store(name="Beta", vector=[2.0, 2.0]),
        ]
        client.add(docs)
        client.commit()
        time.sleep(1)

        # Test faceting and highlighting
        parser = StandardParser(query="name:Alpha", rows=10)
        parser.facet = FacetParamsConfig(fields=["name"])
        parser.highlight = HighlightParamsConfig(
            method=HighlightMethod.UNIFIED,
            fields=["name"],
        )
        res = client.search(parser, document_model=Store)
        assert res.status == 0
        assert res.num_found >= 1
        assert all(isinstance(doc, Store) for doc in res.docs)
        extra = getattr(res, "extra", {})
        assert "facet_counts" in extra or "facets" in extra
        params = extra.get("responseHeader", {}).get("params", {})
        assert params.get("highlight") == "true"
        assert "name" in params.get("hl.fl", "")
        
        # Cleanup
        try:
            client.delete_collection(collection)
        except SolrError as e:
            if getattr(e, "status_code", None) == 404:
                pass
            else:
                raise
