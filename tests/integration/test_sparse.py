from taiyo import SolrClient
import time
from .utils import Store, create_collection_with_schema, COLLECTION, SOLR_URL
from taiyo.parsers import StandardParser


def test_standard():
    with SolrClient(SOLR_URL) as client:
        create_collection_with_schema(client)
        docs = [
            Store(id="1", name="Alpha", vector=[0.0, 0.0]),
            Store(id="2", name="Beta", vector=[1.0, 1.0]),
            Store(id="3", name="Gamma", vector=[2.0, 2.0]),
        ]
        client.set_collection(COLLECTION)
        client.add(docs)
        client.commit()
        time.sleep(1)

        parser = StandardParser(query="name:Alpha", rows=2)
        res = client.search(parser, document_model=Store)
        assert res.status == 0
        assert res.num_found >= 1
        assert any(d.name == "Alpha" for d in res.docs)
