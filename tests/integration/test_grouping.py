from taiyo import SolrClient, SolrError
import time
from .utils import Store, create_collection_with_schema, COLLECTION, SOLR_URL
from taiyo.params.configs.group import GroupParamsConfig
from taiyo.parsers import StandardParser


def test_grouping():
    with SolrClient(SOLR_URL) as client:
        create_collection_with_schema(client)
        docs = [
            Store(id="1", name="Alpha", vector=[0.0, 0.0]),
            Store(id="2", name="Alpha", vector=[1.0, 1.0]),
            Store(id="3", name="Beta", vector=[2.0, 2.0]),
        ]
        client.set_collection(COLLECTION)
        client.add(docs)
        client.commit()
        time.sleep(1)

        parser = StandardParser(query="*:*", rows=10)
        parser.group = GroupParamsConfig(field="name", limit=2)
        res = client.search(parser, document_model=Store)
        assert res.status == 0
        extra = getattr(res, "extra", {})
        assert "grouped" in extra
        grouped = extra["grouped"]
        assert "name" in grouped
        assert "groups" in grouped["name"]
        assert len(grouped["name"]["groups"]) >= 1
        try:
            client.delete_collection(COLLECTION)
        except SolrError as e:
            if getattr(e, "status_code", None) == 404:
                pass
            else:
                raise
