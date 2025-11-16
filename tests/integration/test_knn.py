from taiyo import SolrClient, SolrError
import time
from .utils import Store, create_collection_with_schema, COLLECTION, SOLR_URL
from taiyo.parsers.dense.knn import KNNQueryParser


def test_knn():
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

        knn = KNNQueryParser(field="vector", vector=[0.0, 0.0], top_k=2)
        try:
            res3 = client.search(knn, document_model=Store)
            assert res3.status == 0
        except SolrError as e:
            print("[DEBUG] Solr KNN query error response:", getattr(e, "response", e))
            raise
        try:
            client.delete_collection(COLLECTION)
        except SolrError as e:
            if getattr(e, "status_code", None) == 404:
                pass
            else:
                raise
