from taiyo import SolrClient, SolrError
import time
from .utils import Store, create_collection_with_schema, COLLECTION, SOLR_URL
from taiyo.parsers import DisMaxQueryParser, ExtendedDisMaxQueryParser


def test_dismax_and_edismax_queries():
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

        dismax = DisMaxQueryParser(
            query="Alpha Beta",
            query_fields={"name": 2.0},
            min_match="1",
        )
        res = client.search(dismax, document_model=Store)
        assert res.status == 0
        assert res.num_found >= 1

        edismax = ExtendedDisMaxQueryParser(
            query="Alpha Beta",
            query_fields={"name": 1.0},
            split_on_whitespace=True,
            min_match_auto_relax=True,
        )
        res2 = client.search(edismax, document_model=Store)
        assert res2.status == 0
        assert res2.num_found >= 1

        try:
            client.delete_collection(COLLECTION)
        except SolrError as e:
            if getattr(e, "status_code", None) == 404:
                pass
            else:
                raise
